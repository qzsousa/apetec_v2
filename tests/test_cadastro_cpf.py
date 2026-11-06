import os
os.environ["DATABASE_URL"] = "sqlite:///./test_apetec.db"

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from fastapi.testclient import TestClient
from main import app
from app.database import create_db_and_tables, engine
from sqlmodel import SQLModel


class TestCadastroCPF(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # ensure fresh schema
        SQLModel.metadata.drop_all(engine)
        create_db_and_tables()
        cls.client = TestClient(app)

    def test_cpf_valido_mascarado_aceito(self):
        payload = {
            "cpf": "529.982.247-25",
            "nome": "Teste Usuario",
            "telefone": "11999999999",
            "email": "teste@example.com",
            "turma_modulo": "1 DS A",
            "cargo": "aluno",
            "senha": "Senha@123",
        }
        r = self.client.post("/usuarios/", json=payload)
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(r.json()["cpf"], "52998224725")

    def test_cpf_invalido_rejeitado(self):
        payload = {
            "cpf": "123.456.789-00",
            "nome": "Teste Usuario2",
            "telefone": "11999999999",
            "email": "teste2@example.com",
            "turma_modulo": "1 DS A",
            "cargo": "aluno",
            "senha": "Senha@123",
        }
        r = self.client.post("/usuarios/", json=payload)
        self.assertEqual(r.status_code, 400)
        self.assertIn("CPF", r.json()["detail"])

    def test_cpf_valido_digitos_aceito(self):
        payload = {
            "cpf": "12345678909",
            "nome": "Teste Usuario3",
            "telefone": "11999999999",
            "email": "teste3@example.com",
            "turma_modulo": "1 DS A",
            "cargo": "aluno",
            "senha": "Senha@123",
        }
        r = self.client.post("/usuarios/", json=payload)
        self.assertEqual(r.status_code, 201, r.text)


if __name__ == "__main__":
    unittest.main()
