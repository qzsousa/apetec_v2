from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# O Render fornece URLs postgres://, mas SQLAlchemy exige postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    alters = [
        "ALTER TABLE item ADD COLUMN fotoUrl TEXT",
        "ALTER TABLE item ADD COLUMN status TEXT DEFAULT 'disponivel'",
        "ALTER TABLE item ADD COLUMN data_saida DATE",
        "ALTER TABLE chamado ADD COLUMN data_resposta TIMESTAMP",
        "ALTER TABLE chamado ADD COLUMN data_entrega TIMESTAMP",
        "ALTER TABLE chamado ADD COLUMN entregue_por TEXT",
        "ALTER TABLE chamado ADD COLUMN observacao_entrega TEXT",
        "ALTER TABLE chamado ADD COLUMN notificado BOOLEAN DEFAULT 0",
        "ALTER TABLE chamado ADD COLUMN fotoUrl TEXT",
        "ALTER TABLE chamado ADD COLUMN codigo_retirada TEXT",
        "ALTER TABLE usuario ADD COLUMN email_confirmado BOOLEAN DEFAULT 0",
        "ALTER TABLE usuario ADD COLUMN token_confirmacao TEXT",
    ]
    for sql in alters:
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql(sql)
                conn.commit()
        except Exception:
            pass

def get_session():
    with Session(engine) as session:
        yield session