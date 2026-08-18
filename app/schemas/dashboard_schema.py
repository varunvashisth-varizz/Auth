from pydantic import BaseModel

from .user_schema import UserResponse
from .jwt_schema import JWTCard


class DashboardResponse(BaseModel):
    authentication_method: str

    user: UserResponse

    jwt: JWTCard | None = None