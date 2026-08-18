# This file is intentionally left as a placeholder / extension point.
#
# The actual `/login/session` endpoint (its path and function name,
# `session_login`) already lives in `app/routes/jwt_route.py` and must
# stay there per the "do not change existing endpoint paths" constraint.
# This module is where a *dedicated* session-auth router (cookie
# issuance, session store lookups, logout, etc.) can be built out later
# without touching jwt_route.py at all.
#
# See docs/integration_guide.md for the recommended approach:
#   1. Build a real `session_login` implementation here (or move the
#      logic authenticate_service._authenticate_session calls into a
#      dedicated `session_service.py`).
#   2. Issue a signed, HttpOnly `session_id` cookie on successful login.
#   3. `authenticate_service.get_current_user` already detects that
#      cookie via `auth_type_service.extract_session_id` and routes to
#      `_authenticate_session` -- just replace its body (currently a 501)
#      with real session-store validation.
#
# Example future router (not wired into main.py yet):
#
# from fastapi import APIRouter
# router = APIRouter(prefix="/session")
#
# @router.post("/logout")
# def session_logout():
#     ...
