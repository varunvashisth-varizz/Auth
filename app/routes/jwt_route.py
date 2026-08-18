from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..services.authenticate_service import create_jwt_token, validate_user
from ..db.db_init import get_db
from ..settings import settings
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(prefix="/login")


@router.post("/jwt")
def jwt_authenticate(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # BUG FIX: the original body called `services.authenticate_service...`,
    # but `services` was never imported -- this endpoint could not have
    # run at all before. Also missing: a `db` session was never obtained
    # or passed to `validate_user`, even though `validate_user` requires
    # one.
    user = validate_user(form_data.username, form_data.password, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    # BUG FIX: `create_jwt_token` requires `expire_min`, but the route
    # never supplied it (would have raised TypeError on every login).
    token = create_jwt_token(user.id, settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": token,
        "token_type": "Bearer"
    }


@router.post("/session")
def session_login():
    # PLACEHOLDER: hook up real session-cookie issuance here. See
    # docs/integration_guide.md. Returning 501 keeps the frontend button
    # functional (it gets a clean, handled response) without pretending
    # session auth already works.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session authentication is not implemented yet.",
    )


@router.get("/google")
def google_login():
    # PLACEHOLDER: hook up the real Google OAuth redirect/callback here.
    # See docs/integration_guide.md.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth authentication is not implemented yet.",
    )
