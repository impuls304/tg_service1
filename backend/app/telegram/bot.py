from __future__ import annotations

import logging
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, Update
from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..core.config import get_settings

logger = logging.getLogger(__name__)


def _build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()

    @dispatcher.message(CommandStart())
    async def handle_start(message: Message):
        await message.answer(
            "Здравствуйте! Жду вас в мини-приложении — нажмите кнопку 'Открыть'."
        )

    @dispatcher.message(F.text)
    async def fallback(message: Message):
        await message.answer(
            "Спасибо за сообщение! Для расчета стоимости воспользуйтесь кнопкой в мини-приложении."
        )

    return dispatcher


class TelegramWebhookRouter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.router = APIRouter(prefix="/telegram", tags=["telegram"])
        self.dispatcher = _build_dispatcher()
        self.bot: Bot | None = None
        self._register_routes()

    def _require_bot(self) -> Bot:
        if self.bot:
            return self.bot

        if not self.settings.telegram_bot_token:
            raise HTTPException(
                status.HTTP_503_SERVICE_UNAVAILABLE, "Telegram bot is not configured"
            )

        self.bot = Bot(token=self.settings.telegram_bot_token)
        return self.bot

    def _register_routes(self) -> None:
        @self.router.post("/webhook")
        async def handle_webhook(request: Request) -> Dict[str, Any]:
            bot = self._require_bot()
            raw = await request.json()
            update = Update.model_validate(raw)
            await self.dispatcher.feed_update(bot, update)
            logger.debug("Processed Telegram update")
            return {"ok": True}

        @self.router.post("/set-webhook")
        async def set_webhook_endpoint() -> Dict[str, Any]:
            bot = self._require_bot()
            if not self.settings.webhook_base_url:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Base URL is not set")

            webhook_url = f"{self.settings.webhook_base_url}/telegram/webhook"
            await bot.set_webhook(webhook_url)
            return {"ok": True, "url": webhook_url}

        @self.router.post("/delete-webhook")
        async def delete_webhook_endpoint() -> Dict[str, Any]:
            bot = self._require_bot()
            await bot.delete_webhook(drop_pending_updates=True)
            return {"ok": True}


telegram_webhook_router = TelegramWebhookRouter()
router = telegram_webhook_router.router
