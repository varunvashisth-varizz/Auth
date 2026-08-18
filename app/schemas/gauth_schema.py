from pydantic import BaseModel


# NEW placeholder schema. Once Google OAuth is wired up (see
# docs/integration_guide.md), fill this in with real profile data
# (e.g. google_sub, email, picture, id_token expiry).
class GAuthCard(BaseModel):
    status: str = "not_implemented"
    message: str = "Google OAuth authentication is not implemented yet."
