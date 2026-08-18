from fastapi import APIRouter, Depends, HTTPException, status

from ..services.authenticate_service import get_current_user
from ..schemas.dashboard_schema import DashboardResponse
from ..schemas.user_schema import UserResponse
from ..schemas.jwt_schema import JWTCard
from ..schemas.session_schema import SessionCard
from ..schemas.gauth_schema import GAuthCard

# NEW FILE: no /dashboard endpoint existed before. This wires up the
# unified `get_current_user` dependency (Core Objective #2) to a
# method-specific response (Core Objective #3).
router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(auth=Depends(get_current_user)):
    current_user, method, context = auth

    jwt_card: JWTCard | None = None
    session_card: SessionCard | None = None
    gauth_card: GAuthCard | None = None

    if method == "jwt":
        user_response = UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            logged_in=context["issued_at"],
            expire=context["expires_at"],
        )
        jwt_card = JWTCard(
            algorithm=context["algorithm"],
            provider=context["provider"],
            issued_at=context["issued_at"],
            expires_at=context["expires_at"],
            payload=context["payload"],
            signature=context["masked_signature"],
        )

    elif method == "session":
        # PLACEHOLDER: `get_current_user` currently raises HTTP 501 for
        # session auth before execution ever reaches this branch, so this
        # is not reachable yet -- it's kept ready so that wiring up real
        # session auth (see docs/integration_guide.md) only requires
        # `context` to be populated upstream; this endpoint won't need
        # to change.
        user_response = UserResponse.model_validate(current_user)
        session_card = SessionCard()

    elif method == "gauth":
        # PLACEHOLDER: see note above for "session". Same idea for GAuth.
        user_response = UserResponse.model_validate(current_user)
        gauth_card = GAuthCard()

    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown authentication method",
        )

    return DashboardResponse(
        authentication_method=method,
        user=user_response,
        jwt=jwt_card,
        session=session_card,
        gauth=gauth_card,
    )
