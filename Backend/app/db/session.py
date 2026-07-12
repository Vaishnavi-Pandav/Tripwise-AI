from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

_is_sqlite = "sqlite" in settings.DATABASE_URL

# PostgreSQL connect args — Supabase pooler requires SSL
_pg_connect_args = {
    "connect_timeout": 10,
    "sslmode": "require",
}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else _pg_connect_args,
    pool_pre_ping=True,
    **({} if _is_sqlite else {
        "pool_size": 5,
        "max_overflow": 2,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    })
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
