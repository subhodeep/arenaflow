import logging
import re
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key\s*[=:]\s*)[^\s,;]+", re.IGNORECASE),
    re.compile(r"(authorization\s*[=:]\s*bearer\s+)[^\s,;]+", re.IGNORECASE),
    re.compile(r"(token\s*[=:]\s*)[^\s,;]+", re.IGNORECASE),
]


def redact(value: Any) -> str:
    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text


class RedactingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        rendered = record.getMessage()
        record.msg = redact(rendered)
        record.args = ()
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(
        RedactingFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s"
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
