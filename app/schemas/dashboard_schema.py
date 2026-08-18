from pydantic import BaseModel

from .user_schema import UserResponse
from .jwt_schema import JWTCard
from .session_schema import SessionCard
from .gauth_schema import GAuthCard


class DashboardResponse(BaseModel):
    authentication_method: str

    user: UserResponse

    jwt: JWTCard | None = None

    # NEW: added so the dashboard endpoint can carry method-specific data
    # for session/gauth too, without breaking the existing `jwt` field.
    session: SessionCard | None = None
    gauth: GAuthCard | None = None
