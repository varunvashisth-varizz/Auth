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