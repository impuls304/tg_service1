from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...database import get_db

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=list[schemas.ServicePublic])
def read_services(db: Session = Depends(get_db)):
    return crud.list_services(db)
