from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .. import crud, models
from ..core.config import get_settings
from ..database import Base, SessionLocal, engine

cli = typer.Typer(help="Админ-инструменты мастера")


def _ensure_db() -> None:
    Base.metadata.create_all(bind=engine)


@cli.command()
def seed(sample_images: Optional[str] = None) -> None:
    """Fill the database with demo services and portfolio items."""

    _ensure_db()
    demo_services = [
        {
            "name": "Поклейка обоев",
            "description": "Профессиональная поклейка любых типов обоев с полной подготовкой стен.",
            "price": "от 600 ₽/м²",
            "icon": "wallpaper",
        },
        {
            "name": "Установка бытовой техники",
            "description": "Монтаж стиральных машин, кухонной техники и подключение коммуникаций.",
            "price": "от 2500 ₽",
            "icon": "tools",
        },
        {
            "name": "Установка кондиционеров",
            "description": "Комплексные услуги по монтажу и сервису кондиционеров.",
            "price": "от 8000 ₽",
            "icon": "ac_unit",
        },
    ]

    default_images = [
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
        "https://images.unsplash.com/photo-1493666438817-866a91353ca9",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
    ]

    image_pool = default_images
    if sample_images:
        image_pool = Path(sample_images).read_text().splitlines()

    demo_portfolio = [
        {
            "title": "Сканди минимализм",
            "description": "Флизелиновые обои, скрытые швы, объект 42 м².",
            "image_url": image_pool[0],
            "wallpaper_type": "Флизелин",
            "area_sqm": "42",
            "highlights": "Монтаж без запаха, готово за 2 дня",
            "category": "wallpaper",
        },
        {
            "title": "Современная классика",
            "description": "Виниловые обои с подбором рисунка, гостиная 28 м².",
            "image_url": image_pool[1],
            "wallpaper_type": "Винил",
            "area_sqm": "28",
            "highlights": "Сложная стыковка узора",
            "category": "wallpaper",
        },
    ]

    with SessionLocal() as db:
        for data in demo_services:
            existing = (
                db.query(models.Service)
                .filter(models.Service.name == data["name"])
                .first()
            )
            if existing:
                continue
            service = models.Service(**data, is_active=True)
            db.add(service)

        for data in demo_portfolio:
            exists = (
                db.query(models.PortfolioItem)
                .filter(models.PortfolioItem.title == data["title"])
                .first()
            )
            if exists:
                continue
            item = models.PortfolioItem(**data)
            db.add(item)

        db.commit()
        typer.echo("Demo content created")


@cli.command()
def list_requests() -> None:
    _ensure_db()
    with SessionLocal() as db:
        for request in crud.list_requests(db):
            typer.echo(
                f"#{request.id} | {request.status} | user={request.user_id} | service={request.service_id}"
            )


if __name__ == "__main__":
    cli()
