import os
from sqlalchemy.ext.automap import automap_base

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
SQLALCHEMY_DATABASE_URI = (f"postgresql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@"
                           f"{os.environ.get('DB_HOST')}/{os.environ.get('DB_NAME')}")
engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use existing tables in the database
Base = automap_base()
Base.prepare(engine, reflect=True)


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
