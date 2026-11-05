# API — Apetec

Base URL: `http://localhost:8000` (ou a URL de produção). Autenticação via Bearer token (JWT) no header `Authorization`.

## Auth (`/auth`)
- `POST /auth/login/usuario` — login aluno. Body: `{cpf, senha}`. Retorna `{access_token, token_type}`.
- `POST /auth/login/secretaria` — login secretaria.
- `POST /auth/recuperar-senha` — solicita código de recuperação. Body: `{email}`.
- `POST /auth/verificar-codigo` — verifica código. Body: `{email, codigo}`.
- `POST /auth/resetar-senha` — redefine senha. Body: `{email, codigo, nova_senha}`.
- `GET /auth/confirmar-email?token=...` — confirma e-mail.
- `POST /auth/setup/secretaria` — cria secretaria inicial (header `X-Setup-Key`).

## Usuários (`/usuarios`)
- `GET /usuarios/` — lista (secretaria). Query: skip, limit.
- `GET /usuarios/me` — perfil do usuário logado.
- `GET /usuarios/{cpf}` — busca por CPF.
- `POST /usuarios/` — cadastro. Body: UsuarioCreate.
- `PUT /usuarios/{cpf}` — atualiza.
- `DELETE /usuarios/{cpf}` — remove.

## Itens (`/item`)
- `POST /item/` — cadastra item (secretaria).
- `GET /item/` — lista (secretaria). Query: skip, limit, tipo, cor, local, status.
- `GET /item/disponiveis` — itens disponíveis (aluno). Query: skip, limit, tipo, cor, local.
- `GET /item/{id}` — busca por ID.
- `PUT /item/{id}` — atualiza (secretaria).
- `DELETE /item/{id}` — remove (secretaria).
- `POST /item/{id}/foto` — upload de foto (secretaria).
- `POST /item/{id}/reivindicar` — aluno reivindica item.
- `POST /item/expirar` — marca itens +90 dias como doados (secretaria).

## Chamados (`/chamados`)
- `POST /chamados/` — abre chamado (aluno).
- `GET /chamados/` — lista (secretaria vê todos; aluno vê os seus). Query: skip, limit, status, tipo, cor, local.
- `GET /chamados/{id}` — busca.
- `PUT /chamados/{id}` — atualiza (secretaria).
- `DELETE /chamados/{id}` — remove (secretaria).
- `GET /chamados/{id}/sugestoes` — itens compatíveis (secretaria).
- `POST /chamados/{id}/vincular` — vincula item e notifica aluno (secretaria). Body: `{id_item, observacao?}`.
- `POST /chamados/{id}/entregar` — marca como entregue (secretaria). Body: `{confirmado, codigo, observacao?}`.
- `POST /chamados/{id}/foto` — upload de foto.
- `GET /chamados/{id}/mensagens` — lista mensagens.
- `POST /chamados/{id}/mensagens` — envia mensagem. Body: `{texto}`.
- `POST /chamados/{id}/feedback` — avalia atendimento. Body: `{nota, comentario?}`.

## Secretaria (`/secretaria`)
- `GET /secretaria/me` — perfil.
- `GET /secretaria/relatorio` — métricas e itens não reclamados.
- `GET /secretaria/auditoria` — logs. Query: skip, limit.
- `GET /secretaria/exportar/itens` — CSV de itens.
- `GET /secretaria/exportar/chamados` — CSV de chamados.

## Notificações (`/notificacoes`)
- `GET /notificacoes/me` — lista notificações do usuário.
- `POST /notificacoes/{id}/ler` — marca como lida.

## Health
- `GET /health` — `{status: ok}`.
