from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from typing import Any, Dict
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from ..core.config import get_settings
from ..schemas import TelegramUserPayload


@dataclass(slots=True)
class TelegramAuthResult:
    payload: TelegramUserPayload
    raw: Dict[str, Any]


class TelegramAuthError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def _compute_hash(data_check_string: str, bot_token: str) -> str:
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()


def validate_init_data(init_data: str | None) -> TelegramAuthResult:
    """Validate Telegram initData payload that comes from the WebApp."""

    if not init_data:
        raise TelegramAuthError("Missing Telegram init data")

    settings = get_settings()
    if not settings.telegram_bot_token:
        raise TelegramAuthError("Bot token is not configured")

    data_pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = data_pairs.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("Missing signature")

    data_check_string = "\n".join(
        f"{k}={data_pairs[k]}" for k in sorted(data_pairs.keys()) if k != "hash"
    )

    expected_hash = _compute_hash(data_check_string, settings.telegram_bot_token)
    if not secrets.compare_digest(expected_hash, received_hash):
        raise TelegramAuthError("Invalid Telegram signature")

    user_raw = data_pairs.get("user")
    if not user_raw:
        raise TelegramAuthError("Missing user payload")

    user_payload = json.loads(user_raw)
    payload = TelegramUserPayload(
        id=user_payload["id"],
        first_name=user_payload.get("first_name"),
        last_name=user_payload.get("last_name"),
        username=user_payload.get("username"),
    )

    return TelegramAuthResult(payload=payload, raw=user_payload)
