from sqlmodel import SQLModel, create_engine, text
from dotenv import load_dotenv
import os

load_dotenv(".venv/.env")
sqlite_file_name = os.getenv('DB_NAME')
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))  # for SQLite only
