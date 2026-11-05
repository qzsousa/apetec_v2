# Funcionalidades — Apetec

## Autenticação e usuários
- Cadastro de aluno com validação de CPF e senha forte.
- Login JWT para aluno e secretaria.
- Recuperação de senha por e-mail (código de 6 dígitos, expira em 15 min).
- Confirmação de e-mail no cadastro.
- Perfil do usuário e edição de dados.
- Reset de senha por secretaria.

## Itens (encontrados)
- Cadastro pela secretaria com foto (Supabase Storage).
- Status: disponível / entregue / doado.
- Listagem com filtros (tipo, cor, local, status) e paginação.
- Catálogo público para alunos (itens disponíveis).
- Reivindicação de item pelo aluno (cria chamado vinculado).
- Expiração/doação automática de itens não reclamados há 90 dias.

## Chamados (perdidos)
- Abertura pelo aluno com descrição e foto opcional.
- Status: em aberto / respondido / finalizado.
- Listagem com filtros e paginação.
- Matching automático com itens encontrados (score).
- Notificações por e-mail e in-app ao aluno.
- Chat/comentários por chamado (aluno ↔ secretaria).
- Vínculo item↔chamado pela secretaria.
- Geração de código de retirada.
- Entrega com validação do código.
- Feedback pós-entrega (nota 1–5 + comentário).

## Notificações
- In-app (sino/lista) para alunos e secretaria.
- E-mail (Resend) em eventos-chave.

## Relatórios e gestão (secretaria)
- Métricas: total, disponíveis, entregues, doados, taxa de devolução.
- Chamados por status.
- Itens não reclamados há +30 dias.
- Exportação CSV (itens e chamados).
- Auditoria de ações.

## Etiquetas
- Geração de QR code com dados do aluno para colar em objetos.

## Frontend
- Dashboard do aluno (novo chamado, meus chamados, itens encontrados, notificações, perfil + QR).
- Dashboard da secretaria (chamados, itens, relatórios, reset de senha).
- Modais de ações, chat e sugestões de itens.
