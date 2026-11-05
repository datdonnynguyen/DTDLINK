"""API contracts and input validation. The URL sent to the model is never rewritten."""
import ipaddress
import re
import unicodedata
from typing import Literal
from urllib.parse import unquote, urlsplit

import idna
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .config import MAX_URL_LENGTH

class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def validate_url(value: str) -> str:
    if not value or value != value.strip():
        raise ValueError("Enter a URL without surrounding spaces.")
    if any(c.isspace() or unicodedata.category(c).startswith("C") for c in value):
        raise ValueError("Spaces and control characters are not allowed.")
    if "\\" in value:
        raise ValueError("Backslashes are not allowed; use forward slashes.")
    if re.search(r"%(?![0-9a-fA-F]{2})", value):
        raise ValueError("Percent encoding must contain two hexadecimal digits.")
    decoded = value
    for _ in range(3):
        decoded = unquote(decoded)
        if any(unicodedata.category(c).startswith("C") for c in decoded):
            raise ValueError("Encoded control characters are not allowed.")
    try:
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"} or not value.lower().startswith(("http://", "https://")):
            raise ValueError("Start the URL with http:// or https://.")
        host = parts.hostname
        port = parts.port
        if not host:
            raise ValueError("Enter a hostname after the protocol.")
        if port is not None and port == 0:
            raise ValueError("The port must be between 1 and 65535.")
        host = host.rstrip(".")
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if re.fullmatch(r"[0-9.]+", host):
                raise ValueError("The numeric host is not a valid IP address.")
            ascii_host = idna.encode(host, uts46=True).decode("ascii")
            if len(ascii_host) > 253 or any(not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label) for label in ascii_host.split(".")):
                raise ValueError("Enter a valid hostname.")
    except (ValueError, UnicodeError, idna.IDNAError) as exc:
        # Do not echo the submitted URL or exception internals in API errors.
        known = {"Start the URL with http:// or https://.", "Enter a hostname after the protocol.",
                 "The port must be between 1 and 65535.", "The numeric host is not a valid IP address.", "Enter a valid hostname."}
        raise ValueError(str(exc) if str(exc) in known else "Enter a valid URL with a valid hostname and port.") from None
    return value


class PredictRequest(APIModel):
    url: str = Field(strict=True, min_length=1, max_length=MAX_URL_LENGTH,
                     description="One complete HTTP(S) URL, preserved exactly for A2 feature extraction.")
    _validate = field_validator("url")(validate_url)
    model_config = ConfigDict(extra="forbid", json_schema_extra={"examples": [{"url": "https://example.com/"}]})


class ErrorField(APIModel):
    field: str
    message: str


class ErrorDetail(APIModel):
    code: str
    message: str
    fields: list[ErrorField] = Field(default_factory=list)


class ErrorResponse(APIModel):
    error: ErrorDetail
    request_id: str


class SignalEvidence(APIModel):
    label: str
    value: str


class Signal(APIModel):
    id: str
    title: str
    present: bool
    severity: Literal["high", "medium", "low"]
    detail: str
    evidence: list[SignalEvidence]
    action: str


class URLPart(APIModel):
    kind: Literal["protocol", "userinfo", "host", "port", "path", "query", "fragment"]
    text: str


class Components(APIModel):
    scheme: str
    host: str
    registrable_domain: str
    port: int | None
    path_length: int = Field(ge=0)
    query_parameter_count: int = Field(ge=0)


class PredictResponse(APIModel):
    request_id: str
    predicted_class: Literal[0, 1]
    label: Literal["Potentially dangerous", "Likely legitimate"]
    explanation: str
    dangerous_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0.5, le=1, description="Probability assigned to the predicted combined class; not calibrated.")
    threshold: float = Field(ge=0, le=1)
    uncertain: bool
    signals: list[Signal]
    url_parts: list[URLPart]
    components: Components
    analysis_ms: float = Field(ge=0)
    model_version: str
    disclaimer: str


class HealthResponse(APIModel):
    status: Literal["ready"]
    model_loaded: bool
    model_version: str
    feature_count: int
    max_concurrent: int
    active_predictions: int


class ModelInfo(APIModel):
    name: str
    version: str
    feature_count: int
    threshold: float
    labels: dict[str, str]
    limits: dict[str, int]
    limitations: list[str]
