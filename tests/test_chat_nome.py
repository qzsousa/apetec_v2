import os
os.environ["DATABASE_URL"] = "sqlite:///./test_chat.db"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from main import app
from app.database import create_db_and_tables, engine, get_session
from sqlmodel import SQLModel, Session
from app.models import Usuario
from app.auth import hash_senha
from app.cpf import normalizar_cpf


class TestChatNome(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SQLModel.metadata.drop_all(engine)
        create_db_and_tables()
        cls.client = TestClient(app)
        with Session(engine) as s:
            u = Usuario(cpf=normalizar_cpf("529.982.247-25"), nome="Maria Silva", telefone="11999999999",
                        email="m@e.com", turma_modulo="1 DS A", cargo="aluno", senha=hash_senha("Senha@123"))
            s.add(u)
            s.commit()
        r = cls.client.post("/auth/login/usuario", json={"cpf": "529.982.247-25", "senha": "Senha@123"})
        cls.token = r.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        # create chamado
        r = cls.client.post("/chamados/", json={"tipo":"Mochila","cor":"Preta","marca":"Nike","data_perda":"2026-01-01","local_perda":"Sala","criterio_validacao":"X"}, headers=cls.headers)
        cls.chamado_id = r.json()["id"]
        # send message
        cls.client.post(f"/chamados/{cls.chamado_id}/mensagens", json={"texto":"oi"}, headers=cls.headers)

    def test_mensagens_tem_autor_nome(self):
        r = self.client.get(f"/chamados/{self.chamado_id}/mensagens", headers=self.headers)
        self.assertEqual(r.status_code, 200)
        msgs = r.json()
        self.assertTrue(len(msgs) > 0)
        self.assertEqual(msgs[0]["autor_nome"], "Maria Silva")


if __name__ == "__main__":
    unittest.main()
