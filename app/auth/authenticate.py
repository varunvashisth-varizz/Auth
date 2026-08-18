from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .auth_context import AuthenticatedContext
from ..database import get_db
from ..config import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login/jwt"
)


def get_current_user(

    token: str = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid Token"
    )

    try:

        header = jwt.get_unverified_header(token)

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except Exception:
        raise credentials_exception

    user_id = payload.get("id")

    if user_id is None:
        raise credentials_exception

    current_user = fetch_user_by_id(
        user_id,
        db
    )

    if current_user is None:
        raise credentials_exception

    return AuthenticatedContext(

        user=current_user,

        token=token,

        header=header,

        payload=payload,

        provider="JWT"
    )