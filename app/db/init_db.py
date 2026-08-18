from app.db_models import *
from .database import engine , base

def init_db() :
    base.metadata.create_all(bind=engine)