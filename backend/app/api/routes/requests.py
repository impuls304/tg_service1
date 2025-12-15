from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...database import get_db
from ...services.notifications import NotificationService, get_notification_service
from ...services.telegram_auth import validate_init_data

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("/", response_model=list[schemas.RequestPublic])
def read_requests(db: Session = Depends(get_db)):
    return crud.list_requests(db)


@router.post("/", response_model=schemas.RequestPublic, status_code=status.HTTP_201_CREATED)
def create_request(
    request_in: schemas.RequestCreate,
    db: Session = Depends(get_db),
    notifier: NotificationService = Depends(get_notification_service),
):
    auth_result = validate_init_data(request_in.init_data)

    user = crud.upsert_user(db, auth_result.payload)

    if request_in.service_id and not crud.get_service(db, request_in.service_id):
        raise HTTPException(status_code=404, detail="Service not found")

    request = crud.create_request(db, user=user, request_in=request_in)
    db.commit()
    db.refresh(request)

    notifier.enqueue(request)
    return request
