"""ASGI boundary: bounded request bodies, exact CORS and headers on every response."""
import asyncio
import uuid

from starlette.responses import JSONResponse, Response
from .config import API_ORIGIN, MAX_BODY_BYTES


def error_response(code, message, request_id, status, fields=None, headers=None):
    return JSONResponse({"error": {"code": code, "message": message, "fields": fields or []},
                         "request_id": request_id}, status_code=status, headers=headers)


class SecurityBoundary:
    def __init__(self, app, settings):
        self.app = app
        self.settings = settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        headers = {key.decode("latin1").lower(): value.decode("latin1") for key, value in scope["headers"]}
        origin = headers.get("origin")
        response_started = False
        async def secure_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                additions = {
                    "x-request-id": request_id,
                    "x-content-type-options": "nosniff",
                    "x-frame-options": "DENY",
                    "referrer-policy": "no-referrer",
                    "permissions-policy": "camera=(), microphone=(), geolocation=()",
                    "cache-control": "no-store",
                    "content-security-policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
                }
                # API docs assets are self-hosted and use an external initializer.
                if scope["path"].startswith(("/docs", "/static/")):
                    additions["content-security-policy"] = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
                if origin == self.settings.frontend_origin:
                    additions["access-control-allow-origin"] = origin
                    additions["vary"] = "Origin"
                message["headers"] = list(message.get("headers", [])) + [(k.encode(), v.encode()) for k, v in additions.items()]
            await send(message)
        async def reject(code, message, status, extra=None):
            await error_response(code, message, request_id, status, headers=extra)(scope, receive, secure_send)
        # Swagger runs on the API's own origin; that is same-origin, not a CORS grant.
        if origin and origin not in {self.settings.frontend_origin, API_ORIGIN}:
            await reject("origin_not_allowed", "This browser origin is not allowed.", 403)
            return
        if scope["method"] == "OPTIONS" and "access-control-request-method" in headers:
            requested = headers["access-control-request-method"].upper()
            requested_headers = {h.strip().lower() for h in headers.get("access-control-request-headers", "").split(",") if h.strip()}
            if requested not in {"GET", "POST"} or not requested_headers <= {"content-type", "accept"}:
                await reject("cors_preflight_rejected", "The requested method or headers are not allowed.", 400)
                return
            await Response(status_code=204, headers={"Access-Control-Allow-Methods": "GET, POST",
                          "Access-Control-Allow-Headers": "Content-Type, Accept", "Access-Control-Max-Age": "600"})(scope, receive, secure_send)
            return
        if scope["method"] == "POST" and headers.get("content-type", "").split(";", 1)[0].lower() != "application/json":
            await reject("unsupported_media_type", "Send the request as application/json.", 415)
            return
        try:
            declared = int(headers.get("content-length", "0"))
            if declared < 0:
                raise ValueError()
        except ValueError:
            await reject("invalid_content_length", "Content-Length must be a non-negative integer.", 400)
            return
        if declared > MAX_BODY_BYTES:
            await reject("request_too_large", "The request exceeds the 16 KiB body limit.", 413)
            return
        body = bytearray()
        async def read_body():
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return False
                body.extend(message.get("body", b""))
                if len(body) > MAX_BODY_BYTES:
                    return "too_large"
                if not message.get("more_body", False):
                    return True
        try:
            outcome = await asyncio.wait_for(read_body(), timeout=self.settings.body_timeout)
        except asyncio.TimeoutError:
            await reject("request_timeout", "The request body was not received in time.", 408)
            return
        if outcome == "too_large":
            await reject("request_too_large", "The request exceeds the 16 KiB body limit.", 413)
            return
        if outcome is False:
            return
        delivered = False
        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()
        try:
            await self.app(scope, replay, secure_send)
        except Exception:
            if not response_started:
                await reject("internal_error", "The request could not be completed. Try again.", 500)
