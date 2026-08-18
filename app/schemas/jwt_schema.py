from datetime import datetime
from pydantic import BaseModel


class JWTCard(BaseModel):
    algorithm: str
    provider: str

    issued_at: datetime
    expires_at: datetime

    issuer: str | None = None
    audience: str | None = None

    payload: dict
    signature: str


# NEW: schema used to validate the *shape* of a decoded JWT payload before
# the app trusts any of its claims (id/iat/exp). This hardens the JWT flow
# per the "validate inputs using Pydantic schemas" requirement without
# altering the actual encode/decode logic in authenticate_service.py.
class TokenPayload(BaseModel):
    id: int
    iat: datetime
    exp: datetime
