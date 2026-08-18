from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import jwt_route, register_route, dashboard_route
from .db.database import base, engine
from .db_models import user as _user_model  # noqa: F401  (import so the table is registered on `base`)

app = FastAPI(title="Auth")

# BUG FIX: original import was `from routes import jwt_route`, which only
# works if `routes` happens to be on sys.path as a top-level package. The
# rest of the codebase uses relative imports (e.g. `..db.database`),
# meaning this project is meant to be run as the `app` package
# (`uvicorn app.main:app`), so the import must be relative too.
app.include_router(jwt_route.router)
app.include_router(register_route.router)
app.include_router(dashboard_route.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# --- Centralized error handling -------------------------------------------
# HTTPException (401/403/400/422/...) raised anywhere in the routes/services
# already gets FastAPI's default clean JSON handling. This adds a safety net
# so genuinely unexpected errors don't leak stack traces to clients.

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # NOTE: exc.errors() can contain raw exception objects (e.g. inside
    # ctx.error for a failed @field_validator) that aren't JSON
    # serializable on their own; jsonable_encoder converts everything to
    # plain JSON-safe types first.
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# --- Frontend pages ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.get("/dashboard-page", response_class=HTMLResponse)
def dashboard_page(request: Request):
    # Note: kept as a distinct path from the JSON API's GET /dashboard
    # (dashboard_route.py) so the existing API endpoint path is untouched.
    return templates.TemplateResponse(request, "dashboard.html")


@app.on_event("startup")
def on_startup():
    # BUG FIX: the original `@app.on_event("startup")` decorator had no
    # function under it at all, which is a syntax error. This creates the
    # `users` table if it doesn't exist yet, so the app is usable out of
    # the box against a fresh database.
    base.metadata.create_all(bind=engine)
