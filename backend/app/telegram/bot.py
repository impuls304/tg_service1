from __future__ import annotations

import logging
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, Update
from aiogram.types.web_app_info import WebAppInfo
from fastapi import APIRouter, HTTPException, Request, status

from ..core.config import get_settings

logger = logging.getLogger(__name__)


def _build_dispatcher(web_app_url: str | None) -> Dispatcher:
    dispatcher = Dispatcher()

    def _build_keyboard() -> ReplyKeyboardMarkup | None:
        if not web_app_url:
            return None
        web_app = WebAppInfo(url=web_app_url)
        button = KeyboardButton(text="Открыть приложение", web_app=web_app)
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[button]],
            resize_keyboard=True,
            one_time_keyboard=False,
            input_field_placeholder="Нажмите кнопку, чтобы открыть мини-приложение",
        )
        return keyboard

    @dispatcher.message(CommandStart())
    async def handle_start(message: Message):
        keyboard = _build_keyboard()
        await message.answer(
            "Здравствуйте! Жду вас в мини-приложении — нажмите кнопку 'Открыть'.",
            reply_markup=keyboard,
        )

    @dispatcher.message(F.web_app_data)
    async def handle_webapp_data(message: Message):
        payload = message.web_app_data.data if message.web_app_data else "{}"
        logger.info("Received web_app_data payload: %s", payload)
        await message.answer(f"Получены данные: {payload}")

    @dispatcher.message(F.text)
    async def fallback(message: Message):
        keyboard = _build_keyboard()
        await message.answer(
            "Спасибо за сообщение! Для расчета стоимости воспользуйтесь кнопкой в мини-приложении.",
            reply_markup=keyboard,
        )

    return dispatcher


class TelegramWebhookRouter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.router = APIRouter(prefix="/telegram", tags=["telegram"])
        web_app_url = (
            str(self.settings.telegram_web_app_url).rstrip("/")
            if self.settings.telegram_web_app_url
            else None
        )
        if web_app_url and not web_app_url.startswith("https://"):
            logger.warning("Web App URL must be HTTPS. Ignoring value: %s", web_app_url)
            web_app_url = None
        self.dispatcher = _build_dispatcher(web_app_url)
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

            base = str(self.settings.webhook_base_url).rstrip().rstrip("/")    
            webhook_url = f"{base}/telegram/webhook"
            await bot.set_webhook(webhook_url)
            return {"ok": True, "url": webhook_url}

        @self.router.post("/delete-webhook")
        async def delete_webhook_endpoint() -> Dict[str, Any]:
            bot = self._require_bot()
            await bot.delete_webhook(drop_pending_updates=True)
            return {"ok": True}


telegram_webhook_router = TelegramWebhookRouter()
router = telegram_webhook_router.router
