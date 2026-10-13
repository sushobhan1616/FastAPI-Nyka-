from sqlalchemy import text
from app.database import engine

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT SYS_CONTEXT('USERENV', 'CON_NAME') FROM DUAL")
    )
    print("Connected to Oracle container:", result.scalar())