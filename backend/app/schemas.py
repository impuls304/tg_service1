from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl

from .models import RequestStatusEnum


class ServiceBase(BaseModel):
    name: str
    description: str
    price: str
    icon: str
    is_active: bool


class ServicePublic(ServiceBase):
    id: int

    class Config:
        from_attributes = True


class PortfolioBase(BaseModel):
    title: str
    description: str
    image_url: HttpUrl
    wallpaper_type: str
    area_sqm: str
    highlights: str
    category: str


class PortfolioPublic(PortfolioBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserPublic(UserBase):
    registered_at: datetime

    class Config:
        from_attributes = True


class RequestCreate(BaseModel):
    service_id: Optional[int]
    details: Optional[str] = None
    init_data: Optional[str] = None


class RequestPublic(BaseModel):
    id: int
    status: RequestStatusEnum
    details: Optional[str]
    created_at: datetime
    service: Optional[ServicePublic]

    class Config:
        from_attributes = True


class APIHealth(BaseModel):
    status: str
    timestamp: datetime


class TelegramUserPayload(BaseModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
