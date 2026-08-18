import re

from pydantic import BaseModel , StringConstraints, EmailStr, field_validator
from typing import Annotated

strictusername = Annotated[
    str ,
    StringConstraints(
        strip_whitespace= True,
        pattern=r"^[a-z0-9_-]+$" ,
        min_length= 5,
        max_length=20
    )
]

class register_username(BaseModel):
    username : strictusername
    password : str


class registered_username(BaseModel):
    username : str


# ---------------------------------------------------------------------------
# NEW (added, does not replace anything above): a fuller registration
# request schema used by the /register endpoint. It reuses the existing
# `strictusername` constraint and adds email + strong-password validation
# as requested, without touching `register_username` / `registered_username`.
# ---------------------------------------------------------------------------

STRONG_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,64}$"
)


class RegisterRequest(BaseModel):
    username: strictusername
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not STRONG_PASSWORD_PATTERN.match(value):
            raise ValueError(
                "Password must be 8-64 characters and include at least one "
                "uppercase letter, one lowercase letter, one digit, and one "
                "special character."
            )
        return value
