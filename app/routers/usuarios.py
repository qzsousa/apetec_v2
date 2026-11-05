import re

from fastapi import APIRouter, Depends, HTTPException, Query
from app.models import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioPublic, Notificacao, AuditLog
from app.database import get_session
from sqlmodel import Session, select
from app.auth import hash_senha, get_usuario_atual, is_secretaria
from app.audit import registrar_auditoria
import os, uuid, hashlib

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def senha_valida(senha: str) -> bool:
    return (
        len(senha) >= 8 and
        bool(re.search(r'[A-Z]', senha)) and
        bool(re.search(r'[0-9]', senha)) and
        bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', senha))
    )


def cpf_valido(cpf: str) -> bool:
    return bool(re.fullmatch(r'\d{11}', cpf))


@router.get("/")
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    usuario_atual: dict = Depends(get_usuario_atual),
):
    if not is_secretaria(usuario_atual):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    usuarios = session.exec(select(Usuario).offset(skip).limit(limit)).all()
    return [UsuarioPublic(**u.model_dump(exclude={"senha"})) for u in usuarios]


@router.get("/me")
def meu_perfil(session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    cpf = usuario_atual["sub"]
    usuario = session.get(Usuario, cpf)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UsuarioPublic(**usuario.model_dump(exclude={"senha"}))


@router.get("/{cpf}")
def buscar_usuario(cpf: str, session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not (is_secretaria(usuario_atual) or usuario_atual.get("sub") == cpf):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    usuario = session.get(Usuario, cpf)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UsuarioPublic(**usuario.model_dump(exclude={"senha"}))


@router.post("/", status_code=201)
def cadastrar_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    if not cpf_valido(usuario.cpf):
        raise HTTPException(status_code=400, detail="CPF inválido (11 dígitos)")
    if session.get(Usuario, usuario.cpf):
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    if not senha_valida(usuario.senha):
        raise HTTPException(status_code=400, detail="A senha não atende aos requisitos mínimos")
    db_usuario = Usuario(**usuario.model_dump())
    db_usuario.senha = hash_senha(db_usuario.senha)
    token = uuid.uuid4().hex
    db_usuario.token_confirmacao = token
    db_usuario.email_confirmado = False
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)

    # enviar email de confirmacao
    try:
        api_key = os.getenv("RESEND_API_KEY")
        if api_key:
            import resend
            resend.api_key = api_key
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": db_usuario.email,
                "subject": "Confirme seu e-mail - Apetec",
                "html": f"<p>Olá {db_usuario.nome},</p><p>Clique no link para confirmar seu e-mail:</p><p><a href='http://localhost:8000/auth/confirmar-email?token={token}'>Confirmar e-mail</a></p>",
            })
    except Exception:
        pass

    registrar_auditoria(session, "usuario", usuario.cpf, "cadastrar_usuario", "usuario", usuario.cpf)
    return UsuarioPublic(**db_usuario.model_dump(exclude={"senha"}))


@router.put("/{cpf}")
def atualizar_dados_usuario(dados: UsuarioUpdate, cpf: str, session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not (is_secretaria(usuario_atual) or usuario_atual.get("sub") == cpf):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    usuario = session.get(Usuario, cpf)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if dados.senha:
        dados.senha = hash_senha(dados.senha)
    dados_novos = dados.model_dump(exclude_unset=True)
    usuario.sqlmodel_update(dados_novos)
    session.commit()
    session.refresh(usuario)
    registrar_auditoria(session, "usuario" if usuario_atual.get("sub") == cpf else "secretaria", usuario_atual.get("sub"), "atualizar_usuario", "usuario", cpf)
    return UsuarioPublic(**usuario.model_dump(exclude={"senha"}))


@router.delete("/{cpf}", status_code=204)
def deletar_usuario(cpf: str, session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not (is_secretaria(usuario_atual) or usuario_atual.get("sub") == cpf):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    usuario = session.get(Usuario, cpf)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(usuario)
    session.commit()
    registrar_auditoria(session, "secretaria" if is_secretaria(usuario_atual) else "usuario", usuario_atual.get("sub"), "deletar_usuario", "usuario", cpf)
    return None