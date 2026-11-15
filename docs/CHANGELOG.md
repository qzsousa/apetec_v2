# Atualizações e Novidades — Apetec

Documento com as funcionalidades recentemente adicionadas/atualizadas, acompanhadas de capturas de tela.

## 1. Matching automático e notificações
- Score de compatibilidade entre chamados e itens (tipo, cor, marca, local, data).
- Notificações por e-mail e in-app ao aluno quando item compatível é cadastrado.
- Sugestões de itens no modal de ações da secretaria.

![Modal de Ações](../screenshots/modal_padronizado.png)

## 2. Vínculo e entrega com código de retirada
- Secretaria vincula item ao chamado; gera código de 6 dígitos.
- Entrega exige código de retirada + confirmação de identidade.
- Notificação ao aluno quando item pronto para retirada.

![Chat/Modal](../screenshots/chat_padronizado.png)

## 3. Chat por chamado
- Conversa aluno ↔ secretaria vinculada ao chamado.
- Notificação in-app ao receber mensagem.

![Chat padronizado](../screenshots/chat_padronizado.png)

## 4. Catálogo de itens para alunos
- Alunos visualizam itens encontrados disponíveis.
- Reivindicação de item ("É meu") cria chamado vinculado e notifica secretaria.
- Filtros por tipo/cor.

![Itens Encontrados](../screenshots/itens_encontrados.png)

## 5. Notificações in-app
- Lista de notificações do usuário.
- Marcar como lida.

![Notificações](../screenshots/notificacoes.png)

## 6. Relatórios e métricas (secretaria)
- Total de itens, disponíveis, entregues, doados, taxa de devolução.
- Chamados por status, itens não reclamados (+30 dias).
- Exportação CSV (itens e chamados).
- Expiração/doação de itens (+90 dias).

![Relatórios](../screenshots/secretaria_relatorios.png)

## 7. Auditoria
- Registro de ações (criar item, chamado, vínculo, entrega, feedback, etc.) com ator e timestamp.
- Endpoint `/secretaria/auditoria`.

## 8. Feedback pós-entrega
- Aluno avalia atendimento (nota 1–5 + comentário) após entrega.

![Meus Chamados](../screenshots/meus_chamados.png)

## 9. Etiquetas/QR para objetos
- Geração de QR code com dados do aluno para colar em objetos.

![Perfil + QR](../screenshots/perfil_qr.png)

## 10. Confirmação de e-mail e validação de CPF
- Cadastro exige CPF válido (11 dígitos).
- E-mail de confirmação enviado no cadastro.

## 11. Padronização visual dos modais
- Modais de ações, chat e confirmações alinhados ao tema (fundo marrom, acento amarelo, blur, Crimson Pro).

![Modal Padronizado](../screenshots/modal_padronizado.png)
![Aluno Padronizado](../screenshots/aluno_padronizado.png)

## 12. Upload de fotos
- Foto no item encontrado e no chamado (até 5MB, png/jpg/jpeg/webp/gif).

## 13. Paginação e filtros avançados
- skip/limit e filtros por tipo, cor, local, status nas listagens.

## 14. Documentação
- README reestruturado.
- Pasta `docs/` com arquitetura, API, funcionalidades e screenshots.

---

Screenshots completos em `screenshots/`.
