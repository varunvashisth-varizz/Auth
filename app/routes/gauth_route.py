# This file is intentionally left as a placeholder / extension point.
#
# The actual `/login/google` endpoint (its path and function name,
# `google_login`) already lives in `app/routes/jwt_route.py` and must
# stay there per the "do not change existing endpoint paths" constraint.
# This module is where a *dedicated* Google OAuth router (authorization
# redirect, callback, token exchange) can be built out later without
# touching jwt_route.py at all.
#
# See docs/integration_guide.md for the recommended approach:
#   1. Build the OAuth redirect + callback handlers here.
#   2. On successful callback, either issue your own JWT/session for the
#      user, or store a `gauth_session` cookie identifying the Google
#      session.
#   3. `authenticate_service.get_current_user` already detects that
#      cookie/header via `auth_type_service.extract_gauth_token` and
#      routes to `_authenticate_gauth` -- just replace its body
#      (currently a 501) with real Google token verification.
#
# Example future router (not wired into main.py yet):
#
# from fastapi import APIRouter
# router = APIRouter(prefix="/gauth")
#
# @router.get("/callback")
# def gauth_callback(code: str):
#     ...
