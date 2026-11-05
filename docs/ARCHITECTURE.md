# Arquitetura — Apetec

## Visão geral
Monólito FastAPI com frontend estático servido pelo próprio backend. Banco relacional (SQLite em dev, PostgreSQL em prod). Armazenamento de fotos no Supabase Storage. E-mails via Resend.

## Camadas
- `main.py` — app FastAPI, CORS, routers, static files, startup (create tables).
- `app/models.py` — modelos SQLModel (tabelas + schemas de entrada/saída).
- `app/database.py` — engine, sessão, migrations idempotentes (ALTER TABLE).
- `app/auth.py` — hashing (bcrypt), JWT, dependências de auth/secretaria.
- `app/audit.py` — helper de auditoria.
- `app/supabase_storage.py` — upload/delete de arquivos.
- `app/routers/*` — endpoints por domínio.
- `frontend/*` — HTML/CSS/JS puro consumindo a API.

## Modelos principais
- `Usuario` (aluno/professor/funcionário) — CPF PK, email, turma, cargo, senha, email_confirmado, token_confirmacao.
- `Secretaria` — CPF PK.
- `Item` — item encontrado (marca, cor, tipo, tamanho, local, data_entrada, fotoUrl, status, data_saida).
- `Chamado` — item perdido reportado pelo aluno (tipo, cor, marca, critério, data_perda, local_perda, status, cpf_usuario, id_item, datas, código de retirada, fotoUrl).
- `Mensagem` — chat por chamado.
- `Notificacao` — notificações in-app.
- `AuditLog` — auditoria.
- `Feedback` — avaliação pós-entrega.
- `TokenRecuperacao` — recuperação de senha.

## Status
- Chamado: `em_aberto` → `respondido` (item vinculado) → `finalizado` (entregue).
- Item: `disponivel` → `entregue` / `doado`.

## Matching
Score calculado por tipo (40), cor (20), marca (15), local (15), data ±7 dias (até 10). Limiar 30 para sugestões/notificações.

## Segurança
- JWT (HS256) com expiração 60 min.
- Senhas com bcrypt.
- Rotas protegidas por `get_usuario_atual` / `exigir_secretaria`.
- Validação de CPF (11 dígitos).
- Confirmação de e-mail no cadastro.
- Upload com validação de extensão e tamanho (5MB).

## Banco
- `create_db_and_tables` cria tabelas e aplica ALTERs idempotentes para compatibilidade.
- SQLite (dev) / PostgreSQL (prod via `DATABASE_URL`).
