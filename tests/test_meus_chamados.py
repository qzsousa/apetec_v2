import os
os.environ["DATABASE_URL"] = "sqlite:///./test_chamados.db"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from main import app
from app.database import create_db_and_tables, engine, get_session
from sqlmodel import SQLModel, Session
from app.models import Usuario, Secretaria
from app.auth import hash_senha
from app.cpf import normalizar_cpf


class TestMeusChamados(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SQLModel.metadata.drop_all(engine)
        create_db_and_tables()
        cls.client = TestClient(app)
        # create user
        with Session(engine) as s:
            u = Usuario(cpf=normalizar_cpf("529.982.247-25"), nome="Teste", telefone="11999999999",
                        email="t@e.com", turma_modulo="1 DS A", cargo="aluno", senha=hash_senha("Senha@123"))
            s.add(u)
            s.commit()
        # login
        r = cls.client.post("/auth/login/usuario", json={"cpf": "529.982.247-25", "senha": "Senha@123"})
        cls.token = r.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_listar_chamados(self):
        # create a chamado
        payload = {
            "tipo": "Mochila", "cor": "Preta", "marca": "Nike",
            "data_perda": "2026-01-01", "local_perda": "Sala 1", "criterio_validacao": "Etiqueta"
        }
        r = self.client.post("/chamados/", json=payload, headers=self.headers)
        print("create status:", r.status_code, r.text)
        self.assertEqual(r.status_code, 201)
        # list
        r = self.client.get("/chamados/", headers=self.headers)
        print("list status:", r.status_code, r.text)
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
