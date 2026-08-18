from dataclasses import dataclass

from ..db_models.user import User


@dataclass
class AuthenticatedContext:

    user: User

    token: str

    header: dict

    payload: dict

    provider: strAuthenticatedContext