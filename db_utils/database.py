from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from settings_app import APP_DATABASE_URL

engine = create_engine(APP_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
