from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db.db_init import get_db
from ..db_models.user import user
from ..schemas.register_request import RegisterRequest, registered_username
from ..services.authenticate_service import hash_password

# NEW FILE: there was no registration endpoint anywhere in the original
# repo (only login stubs existed), so this whole router is additive and
# does not touch any existing path/function/file.
router = APIRouter()


@router.post("/register", response_model=registered_username, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):

    existing = (
        db.query(user)
        .filter((user.username == payload.username) | (user.email == payload.email))
        .first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that username or email already exists.",
        )

    new_user = user(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that username or email already exists.",
        )

    db.refresh(new_user)

    return new_user
