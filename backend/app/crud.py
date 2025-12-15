from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def list_services(db: Session) -> Iterable[models.Service]:
    statement = select(models.Service).where(models.Service.is_active.is_(True))
    return db.scalars(statement).all()


def list_portfolio(db: Session) -> Iterable[models.PortfolioItem]:
    statement = select(models.PortfolioItem).order_by(models.PortfolioItem.created_at.desc())
    return db.scalars(statement).all()


def get_service(db: Session, service_id: int) -> Optional[models.Service]:
    return db.get(models.Service, service_id)


def upsert_user(db: Session, payload: schemas.TelegramUserPayload) -> models.User:
    user = db.get(models.User, payload.id)
    if user:
        user.first_name = payload.first_name or user.first_name
        user.last_name = payload.last_name or user.last_name
        user.username = payload.username or user.username
        return user

    user = models.User(
        telegram_id=payload.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        username=payload.username,
    )
    db.add(user)
    return user


def create_request(
    db: Session,
    *,
    user: models.User,
    request_in: schemas.RequestCreate,
) -> models.Request:
    request = models.Request(
        user=user,
        service_id=request_in.service_id,
        details=request_in.details,
    )
    db.add(request)
    return request


def list_requests(db: Session) -> Iterable[models.Request]:
    statement = select(models.Request).order_by(models.Request.created_at.desc())
    return db.scalars(statement).all()
