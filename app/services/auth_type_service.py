from fastapi import Request


# NOTE: this file was empty in the original repository, so everything
# below is new. These small helpers are used by
# `authenticate_service.get_current_user` to figure out, purely from the
# incoming request, which authentication mechanism the caller is using.
# Keeping the detection logic here (rather than inline) makes it easy to
# extend later for Session Auth / Google OAuth (see
# docs/integration_guide.md).

JWT_HEADER = "authorization"
SESSION_COOKIE_NAME = "session_id"
GAUTH_COOKIE_NAME = "gauth_session"
GAUTH_HEADER = "x-google-auth-token"


def extract_bearer_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()


def extract_session_id(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE_NAME)


def extract_gauth_token(request: Request) -> str | None:
    return request.cookies.get(GAUTH_COOKIE_NAME) or request.headers.get(GAUTH_HEADER)


def detect_auth_method(request: Request) -> str | None:
    """Returns 'jwt', 'session', 'gauth', or None if no credentials were
    presented at all. Order matters: JWT bearer tokens are checked first
    since that is the only fully implemented flow today."""

    if extract_bearer_token(request):
        return "jwt"
    if extract_session_id(request):
        return "session"
    if extract_gauth_token(request):
        return "gauth"
    return None
