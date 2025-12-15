import logging

from ..core.config import get_settings
from ..models import Request

logger = logging.getLogger(__name__)


class NotificationService:
    """Simple async notification publisher for the master."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def send_new_request(self, request: Request) -> None:
        if not self.settings.telegram_master_chat_id:
            logger.info("Master chat id is not set; skipping notification")
            return

        # Placeholder for integration with aiogram Bot or another channel.
        logger.info(
            "Notify master about request",
            extra={
                "request_id": request.id,
                "user": request.user_id,
                "service_id": request.service_id,
            },
        )

    def enqueue(self, request: Request) -> None:
        self.send_new_request(request)


def get_notification_service() -> NotificationService:
    return NotificationService()
