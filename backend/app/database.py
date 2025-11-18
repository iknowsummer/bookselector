import os
from dotenv import load_dotenv
from typing import Iterator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

load_dotenv()

# DATABASE_URLからSQLite URLを構築
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite用
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

# SQLiteで外部キー制約を有効化
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
