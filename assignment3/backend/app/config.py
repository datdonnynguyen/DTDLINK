"""Small, explicit configuration; the model trust anchor is not user supplied."""
import os
from dataclasses import dataclass
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
MODEL_SHA256 = "d4aa8ff332ab82c36e3befce1a0e74c336b25a07a19ee9012e489c56239cb586"
MAX_URL_LENGTH = 2048
MAX_BODY_BYTES = 16384
API_ORIGIN = "http://127.0.0.1:8000"

@dataclass(frozen=True)
class Settings:
    frontend_origin: str = "http://127.0.0.1:5173"
    max_concurrent: int = 2
    body_timeout: float = 5.0

    @classmethod
    def from_env(cls):
        origin = os.getenv("DTDLINK_FRONTEND_ORIGIN", cls.frontend_origin)
        from urllib.parse import urlsplit
        parts = urlsplit(origin)
        if (parts.scheme not in {"http", "https"} or not parts.hostname
                or parts.path or parts.query or parts.fragment or parts.username
                or "*" in origin):
            raise ValueError("DTDLINK_FRONTEND_ORIGIN must be one exact origin without a trailing slash.")
        capacity = int(os.getenv("DTDLINK_MAX_CONCURRENT", "2"))
        if not 1 <= capacity <= 8:
            raise ValueError("DTDLINK_MAX_CONCURRENT must be between 1 and 8.")
        return cls(frontend_origin=origin, max_concurrent=capacity)
