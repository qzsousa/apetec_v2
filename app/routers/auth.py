from datetime import datetime, timedelta
import os
import random
import hashlib
import hmac
import resend
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database import get_session
from app.models import LoginUsuario, LoginSecretaria, ResetarSenha, TokenRecuperacao, Usuario, Secretaria, SolicitarRecuperacao, VerificarCodigo, Notificacao
from app.auth import verificar_senha, criar_token, hash_senha
from app.cpf import normalizar_cpf


router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _hash_codigo(codigo: str) -> str:
    return hashlib.sha256(codigo.encode()).hexdigest()


@router.post("/login/usuario")
def login_usuario(login_data: LoginUsuario, session: Session = Depends(get_session)):
    login_data.cpf = normalizar_cpf(login_data.cpf)
    usuario = session.get(Usuario, login_data.cpf)
    if not usuario or not verificar_senha(login_data.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"sub": str(usuario.cpf), "tipo": "usuario"})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login/secretaria")
def login_secretaria(login_data: LoginSecretaria, session: Session = Depends(get_session)):
    login_data.cpf = normalizar_cpf(login_data.cpf)
    secretaria = session.get(Secretaria, login_data.cpf)
    if not secretaria or not verificar_senha(login_data.senha, secretaria.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"sub": secretaria.cpf, "tipo": "secretaria"})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/recuperar-senha")
def recuperar_senha(dados: SolicitarRecuperacao, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    codigo = str(random.randint(100000, 999999))
    expiracao = datetime.utcnow() + timedelta(minutes=15)

    token = TokenRecuperacao(email=dados.email, codigo=_hash_codigo(codigo), expiracao=expiracao)
    session.add(token)
    session.commit()

    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="Serviço de e-mail indisponível")
    resend.api_key = api_key
    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": dados.email,
            "subject": "Recuperação de senha - Apetec",
            "html": f"<p>Seu código de recuperação é: <strong>{codigo}</strong></p><p>Válido por 15 minutos.</p>"
        })
    except Exception:
        raise HTTPException(status_code=502, detail="Falha ao enviar e-mail")

    return {"mensagem": "Código enviado para o e-mail"}


@router.post("/verificar-codigo")
def verificar_codigo(dados: VerificarCodigo, session: Session = Depends(get_session)):
    codigo_hash = _hash_codigo(dados.codigo)
    token = session.exec(
        select(TokenRecuperacao).where(
            TokenRecuperacao.email == dados.email,
            TokenRecuperacao.codigo == codigo_hash,
            TokenRecuperacao.usado == False,
        )
    ).first()

    if not token:
        raise HTTPException(status_code=400, detail="Código inválido")
    if token.expiracao < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")

    return {"valido": True}


@router.post("/resetar-senha")
def resetar_senha(dados: ResetarSenha, session: Session = Depends(get_session)):
    codigo_hash = _hash_codigo(dados.codigo)
    token = session.exec(
        select(TokenRecuperacao).where(
            TokenRecuperacao.email == dados.email,
            TokenRecuperacao.codigo == codigo_hash,
            TokenRecuperacao.usado == False,
        )
    ).first()

    if not token:
        raise HTTPException(status_code=400, detail="Código inválido")
    if token.expiracao < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")

    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    confirms = [v for v in (dados.confirmar_senha, dados.senha_confirmacao, dados.confirm_password) if v is not None]
    for c in confirms:
        if c != dados.nova_senha:
            raise HTTPException(status_code=400, detail="As senhas não coincidem")

    usuario.senha = hash_senha(dados.nova_senha)
    token.usado = True
    session.add(usuario)
    session.add(token)
    session.commit()

    return {"mensagem": "Senha resetada com sucesso"}


@router.get("/confirmar-email")
def confirmar_email(token: str, session: Session = Depends(get_session)):
    usuario = session.exec(select(Usuario).where(Usuario.token_confirmacao == token)).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Token inválido")
    usuario.email_confirmado = True
    usuario.token_confirmacao = None
    session.add(usuario)
    session.commit()
    return {"mensagem": "E-mail confirmado com sucesso"}


class SetupSecretariaIn(BaseModel):
    cpf: str = "47266774896"
    nome: str = "Pablo Nascimento Vieira de Sousa"
    email: str = "nascpablo1709@gmail.com"
    telefone: str = "11952437282"
    senha: str | None = None


@router.post("/setup/secretaria")
def criar_secretaria(
    dados: SetupSecretariaIn | None = None,
    session: Session = Depends(get_session),
    x_setup_key: str | None = Header(default=None, alias="X-Setup-Key"),
):
    setup_key = os.getenv("SETUP_KEY")
    if not setup_key:
        raise HTTPException(status_code=403, detail="Rota desativada")
    if not x_setup_key or not hmac.compare_digest(x_setup_key, setup_key):
        raise HTTPException(status_code=403, detail="Chave inválida")

    senha = (dados.senha if dados and dados.senha else os.getenv("SECRETARIA_SENHA"))
    if not senha:
        raise HTTPException(status_code=400, detail="Senha obrigatória (body.senha ou SECRETARIA_SENHA)")

    cpf = dados.cpf if dados else "47266774896"
    nome = dados.nome if dados else "Pablo Nascimento Vieira de Sousa"
    email = dados.email if dados else "nascpablo1709@gmail.com"
    telefone = dados.telefone if dados else "11952437282"

    existente = session.get(Secretaria, cpf)
    if existente:
        existente.nome = nome
        existente.email = email
        existente.telefone = telefone
        existente.senha = hash_senha(senha)
        session.add(existente)
        session.commit()
        return {"mensagem": "Secretaria atualizada com sucesso!"}

    secretaria = Secretaria(
        cpf=cpf,
        nome=nome,
        email=email,
        telefone=telefone,
        senha=hash_senha(senha),
    )
    session.add(secretaria)
    session.commit()
    return {"mensagem": "Secretaria criada com sucesso!"}
