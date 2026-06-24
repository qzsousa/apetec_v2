from sqlmodel import Session, create_engine
from app.models import Secretaria
from app.auth import hash_senha
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    secretaria = Secretaria(
        cpf="47266774896",
        nome="Pablo Nascimento Vieira de Sousa",
        email="nascpablo1709@gmail.com",
        telefone="11952437282",
        senha=hash_senha("thuane2405")
    )
    session.add(secretaria)
    session.commit()
    print("Secretaria criada com sucesso!")