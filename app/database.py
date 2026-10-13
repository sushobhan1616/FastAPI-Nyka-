import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = "ECOMMERCE"
DB_PASSWORD = os.getenv("DB_PASSWORD", "Viper@3061")
DB_HOST = "localhost"
DB_PORT = 1521
DB_SERVICE = "FREEPDB1"

DATABASE_URL = URL.create(
    drivername="oracle+oracledb",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    query={"service_name": DB_SERVICE}
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
