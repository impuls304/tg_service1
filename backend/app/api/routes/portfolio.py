from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...database import get_db

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/", response_model=list[schemas.PortfolioPublic])
def read_portfolio(db: Session = Depends(get_db)):
    return crud.list_portfolio(db)
