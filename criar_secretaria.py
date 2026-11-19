from sqlmodel import Session, create_engine, select
from app.models import Secretaria
from app.auth import hash_senha
from dotenv import load_dotenv
import os
import sys

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

cpf = os.getenv("SECRETARIA_CPF", "47266774896")
nome = os.getenv("SECRETARIA_NOME", "Pablo Nascimento Vieira de Sousa")
email = os.getenv("SECRETARIA_EMAIL", "nascpablo1709@gmail.com")
telefone = os.getenv("SECRETARIA_TELEFONE", "11952437282")
senha = os.getenv("SECRETARIA_SENHA")

if not senha:
    print("Defina SECRETARIA_SENHA no ambiente antes de rodar este script.")
    sys.exit(1)

with Session(engine) as session:
    existente = session.get(Secretaria, cpf)
    if existente:
        existente.nome = nome
        existente.email = email
        existente.telefone = telefone
        existente.senha = hash_senha(senha)
        session.add(existente)
        session.commit()
        print("Secretaria atualizada com sucesso!")
    else:
        secretaria = Secretaria(
            cpf=cpf,
            nome=nome,
            email=email,
            telefone=telefone,
            senha=hash_senha(senha),
        )
        session.add(secretaria)
        session.commit()
        print("Secretaria criada com sucesso!")
