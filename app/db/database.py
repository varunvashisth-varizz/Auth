from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase , sessionmaker

from ..settings import settings


class base(DeclarativeBase):
    pass


# NOTE: `engine` must always be a valid Engine object so that SessionLocal
# (and every route that depends on get_db) doesn't crash with a NameError
# if the database happens to be unreachable at import time. We still try
# the connection eagerly (as the original code did) purely for the
# startup diagnostic message, but engine creation itself no longer fails.
engine = create_engine(settings.DATABASE_URL)

try:

    with engine.connect() as conn:
        print("connected successfully")

except OperationalError as err:

    print("Database Connection Failed")
    print(err)

SessionLocal = sessionmaker(
    bind = engine,
    autoflush= False,
)
