import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dominio.entidades import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://tcc:tcc@db:5432/tcc")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def criar_tabelas():
    Base.metadata.create_all(engine)

def ping_db() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
