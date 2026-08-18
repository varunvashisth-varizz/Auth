from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.dependency import get_db
from ..schemas.register_request import register_username , registered_username
from ..services.authenticate_service import  validate_user , create_user

router = APIRouter()


@router.post(
    "/register",
    response_model=registered_username
)
def register(
    payload: register_username,
    db: Session = Depends(get_db)
):

    check = validate_user(
        payload.username,
        db
    )

    if check != "username is available":

        raise HTTPException(
            status_code=400,
            detail=check
        )




    return  check.username