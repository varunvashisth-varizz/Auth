from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase , sessionmaker

class base(DeclarativeBase):
    pass

try:

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        print("connected successfully")
    
except OperationalError as err:

    print("Database Connection Failed")
    print(err)

SessionLocal = sessionmaker(
    bind = engine,
    autoflush= False,
)
    