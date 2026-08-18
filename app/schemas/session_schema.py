from pydantic import BaseModel


# NEW placeholder schema. Once session auth is wired up (see
# docs/integration_guide.md), fill this in with real session metadata
# (e.g. session_id (masked), created_at, expires_at, ip_address).
class SessionCard(BaseModel):
    status: str = "not_implemented"
    message: str = "Session authentication is not implemented yet."
