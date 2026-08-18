from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    logged_in : datetime
    expire : datetime

    model_config = ConfigDict(from_attributes=True)