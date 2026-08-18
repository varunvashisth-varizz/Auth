import jwt
from ..db_models.user import user
from pwdlib import PasswordHash
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..settings import settings
from ..db.db_init import get_db
from ..schemas.jwt_schema import TokenPayload
from . import auth_type_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/jwt")


password_hashhed = PasswordHash.recommended()


def fetch_user_by_id(user_id: int, db):

    existing_user = (db.query(user).filter(user.id == user_id).first())

    if not existing_user:
        return None

    # BUG FIX: the original function never returned the user it just
    # fetched, so every caller silently got `None` back even on a
    # successful lookup. `get_current_user` would therefore always fail.
    return existing_user


def validate_user(username: str, password: str, db):

    existing_user = (db.query(user).filter(user.username == username).first())

    if not existing_user:
        return None

    if not verify_password(password, existing_user.password_hash):
        return None

    return existing_user


def verify_password(password: str, password_hash: str) -> bool:

    # BUG FIX: the original code called `password_hash.verify(...)`, but
    # `password_hash` here is the *stored hash string*, not the
    # `PasswordHash` instance -- that would raise AttributeError on every
    # login attempt. `password_hashhed` (the module-level PasswordHash
    # object) is the one with a `.verify()` method, and pwdlib's signature
    # is `verify(plain_password, hash)`, which was also swapped.
    verified = password_hashhed.verify(password, password_hash)

    return verified


# NEW helper (needed for registration; there was previously no way to
# create a password hash at all -- only `verify_password` existed).
def hash_password(password: str) -> str:
    return password_hashhed.hash(password)


def create_jwt_token(user_id: int, expire_min: int):

    payload = {
        "id": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expire_min)
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ---------------------------------------------------------------------------
# NEW: internal helpers backing the unified get_current_user below. Split
# out per auth method so each one can be extended independently later
# (see docs/integration_guide.md for Session/GAuth wiring).
# ---------------------------------------------------------------------------

def _mask_signature(token: str) -> str:
    """Never expose a usable token/signature back to the client. Keeps a
    short recognizable prefix/suffix only, e.g. 'abcd1234...wxyz9876'."""
    parts = token.split(".")
    signature = parts[2] if len(parts) == 3 else token

    if len(signature) <= 12:
        return "***"

    return f"{signature[:6]}...{signature[-6:]}"


def _authenticate_jwt(token: str, db: Session):
    try:
        raw_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate the decoded payload shape with Pydantic before trusting it.
    try:
        payload = TokenPayload.model_validate(raw_payload)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_user = fetch_user_by_id(payload.id, db)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    jwt_context = {
        "algorithm": settings.ALGORITHM,
        "provider": "local-jwt",
        "issued_at": payload.iat,
        "expires_at": payload.exp,
        "payload": raw_payload,
        "masked_signature": _mask_signature(token),
    }

    return current_user, "jwt", jwt_context


def _authenticate_session(session_id: str, db: Session):
    # PLACEHOLDER: Session auth is not implemented yet. Raising a clear
    # 501 keeps runtime execution intact (no unhandled exception) while
    # being honest that this path isn't wired up. See
    # docs/integration_guide.md for how to implement this.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session authentication is not implemented yet.",
    )


def _authenticate_gauth(token: str, db: Session):
    # PLACEHOLDER: Google OAuth is not implemented yet. See
    # docs/integration_guide.md for how to implement this.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth authentication is not implemented yet.",
    )


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Unified authentication dependency.

    Inspects the incoming request (Authorization header / cookies) to
    figure out which auth mechanism the caller is using, authenticates
    accordingly, and returns a 3-tuple:

        (current_user, method, context)

    - current_user: the authenticated user model
    - method: "jwt" | "session" | "gauth"
    - context: method-specific extra data (e.g. decoded JWT claims for
      "jwt"; None for the not-yet-implemented methods)

    NOTE: this replaces the previous `Depends(oauth2_scheme)`-only
    signature. That was unavoidable: `oauth2_scheme` auto-raises 401 the
    moment a bearer token is missing, which made it impossible to fall
    back to session/gauth detection. Every existing caller of
    `get_current_user` (the /dashboard route) is updated accordingly.
    """

    method = auth_type_service.detect_auth_method(request)

    if method == "jwt":
        token = auth_type_service.extract_bearer_token(request)
        return _authenticate_jwt(token, db)

    if method == "session":
        session_id = auth_type_service.extract_session_id(request)
        return _authenticate_session(session_id, db)

    if method == "gauth":
        gauth_token = auth_type_service.extract_gauth_token(request)
        return _authenticate_gauth(gauth_token, db)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
