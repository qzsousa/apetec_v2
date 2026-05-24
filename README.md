# Apetec - Sistema de Achados e Perdidos

API RESTful desenvolvida como TCC para substituir o sistema manual de achados e perdidos da escola por uma solução tecnológica.

## Tecnologias
- Python 3.10+
- FastAPI
- SQLite
- SQLModel
- Uvicorn

## Como rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/apetec_v2.git
cd apetec_v2
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Crie o arquivo .env na raiz
SECRET_KEY=sua-chave-secreta-aqui

### 5. Rode o servidor
```bash
uvicorn main:app --reload
```

### 6. Acesse a documentação
http://localhost:8000/docs

## Rotas disponíveis
- `/usuarios` → cadastro e gerenciamento de alunos
- `/itens` → gerenciamento de itens encontrados
- `/chamados` → abertura e acompanhamento de chamados
- `/auth` → autenticação e geração de token

