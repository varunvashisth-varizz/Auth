# Integration Guide: Wiring up Session Auth & Google OAuth

This describes how to plug **Session Authentication** and **Google OAuth
(GAuth)** into the existing unified `get_current_user` flow
(`app/services/authenticate_service.py`) without touching any existing
file names, function names, variable names, or endpoint paths.

## How detection already works today

`get_current_user(request, db)` does three things, in order:

1. Calls `auth_type_service.detect_auth_method(request)`, which looks at
   the request for:
   - `Authorization: Bearer <token>` header → `"jwt"`
   - `session_id` cookie → `"session"`
   - `gauth_session` cookie **or** `X-Google-Auth-Token` header → `"gauth"`
2. Dispatches to the matching private helper: `_authenticate_jwt`,
   `_authenticate_session`, or `_authenticate_gauth`.
3. Returns `(current_user, method, context)`.

Right now `_authenticate_session` and `_authenticate_gauth` simply raise
`HTTP 501 Not Implemented`. **This is the only part you need to replace.**
Nothing in `get_current_user`'s signature, the detection logic, or any
route (`/dashboard`, `/login/jwt`, etc.) needs to change.

## Wiring up Session Authentication

1. **Session store.** Add a `Session` SQLAlchemy model (new file, e.g.
   `app/db_models/session.py`) with `id` (the opaque session token),
   `user_id`, `created_at`, `expires_at`.
2. **Issue a session on login.** Implement the body of the existing
   `session_login` function in `app/routes/jwt_route.py` (its name/path,
   `POST /login/session`, must not change):
   - Validate credentials with the existing `validate_user(...)`.
   - Create a `Session` row.
   - Set an `HttpOnly`, `Secure`, `SameSite=Lax` cookie named
     `session_id` (matching `auth_type_service.SESSION_COOKIE_NAME`)
     containing the session token.
3. **Validate on every request.** Replace the body of
   `_authenticate_session` in `authenticate_service.py`:
   ```python
   def _authenticate_session(session_id: str, db: Session):
       session = db.query(session_model).filter(session_model.id == session_id).first()
       if session is None or session.expires_at < datetime.now(timezone.utc):
           raise HTTPException(status_code=401, detail="Invalid or expired session")
       current_user = fetch_user_by_id(session.user_id, db)
       if current_user is None:
           raise HTTPException(status_code=401, detail="User not found")
       return current_user, "session", {"session_id": session.id, "expires_at": session.expires_at}
   ```
4. **Dashboard.** In `app/routes/dashboard_route.py`, the `elif method ==
   "session":` branch already exists -- populate `SessionCard` from
   `context` instead of the placeholder default.
5. **Logout.** Add a real handler in `app/routes/session_route.py`
   (already scaffolded) to delete the `Session` row and clear the
   cookie.

## Wiring up Google OAuth (GAuth)

1. **Register OAuth credentials** with Google Cloud Console
   (Client ID/Secret, authorized redirect URI).
2. **Authorization + callback routes.** Implement in
   `app/routes/gauth_route.py` (already scaffolded, not yet mounted in
   `main.py`):
   - `GET /gauth/login` → redirect to Google's OAuth consent screen.
   - `GET /gauth/callback?code=...` → exchange the code for tokens,
     verify the ID token, find-or-create a local `user` row keyed by the
     Google `sub`/email, then either:
     - Issue your own JWT via the existing `create_jwt_token(...)` (simplest --
       reuses the fully working JWT path end-to-end), **or**
     - Issue a `gauth_session` cookie (matching
       `auth_type_service.GAUTH_COOKIE_NAME`) referencing a stored,
       verified Google session.
3. **Mount the router.** Add `app.include_router(gauth_route.router)` in
   `app/main.py` once the router has real routes.
4. **Validate on every request.** If you went the cookie route, replace
   the body of `_authenticate_gauth` in `authenticate_service.py`
   similarly to `_authenticate_session`, verifying the stored Google
   session/token and returning `(current_user, "gauth", context)`.
5. **Dashboard.** The `elif method == "gauth":` branch in
   `dashboard_route.py` already exists -- populate `GAuthCard` with real
   profile data (`google_sub`, `email`, `picture`, token expiry) from
   `context`.

## Frontend

- `login.html`'s "Sign in with Session" and "Sign in with Google"
  buttons already call `POST /login/session` and `GET /login/google`
  respectively, and already handle the current `501` response
  gracefully. Once the backend above is implemented, those same calls
  will succeed (or, for Google, you'll swap the `fetch` for a full page
  redirect to `/gauth/login` -- there's a comment marking exactly where
  in `login.html`).
- `dashboard.html` already branches on `authentication_method` and
  renders `dashboard.session` / `dashboard.gauth` if present -- no
  frontend changes needed once the backend returns real data for those
  methods.

## Summary of what stays untouched

- `get_current_user`'s name and its `(user, method, context)` return
  shape.
- All existing endpoint paths/methods (`POST /login/jwt`,
  `POST /login/session`, `GET /login/google`, `GET /dashboard`).
- The existing JWT encode/decode logic in `create_jwt_token`.
- Every existing Pydantic model/field name.

Only the bodies of `_authenticate_session`, `_authenticate_gauth`,
`session_login`, `google_login`, and the two `elif` branches in
`dashboard_route.py` need real implementations.
