from datetime import datetime, timedelta
import os
import random
import resend
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import LoginUsuario, LoginSecretaria, ResetarSenha, TokenRecuperacao, Usuario, Secretaria, SolicitarRecuperacao, VerificarCodigo
from app.auth import verificar_senha, criar_token, hash_senha


router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login/usuario")
def login_usuario(login_data: LoginUsuario, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, login_data.cpf)
    if not usuario or not verificar_senha(login_data.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = criar_token({"sub": str(usuario.cpf), "tipo": "usuario"})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login/secretaria")
def login_secretaria(login_data: LoginSecretaria, session: Session = Depends(get_session)):
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

    token = TokenRecuperacao(email=dados.email, codigo=codigo, expiracao=expiracao)
    session.add(token)
    session.commit()

    # Envia o e-mail com Resend
    resend.api_key = os.getenv("RESEND_API_KEY")
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": dados.email,
        "subject": "Recuperação de senha — Apetec",
        "html": f"<p>Seu código de recuperação é: <strong>{codigo}</strong></p><p>Válido por 15 minutos.</p>"
    })

    return {"mensagem": "Código enviado para o e-mail"}

@router.post("/verificar-codigo")
def verificar_codigo(dados: VerificarCodigo, session: Session = Depends(get_session)):
    token = session.exec(
        select(TokenRecuperacao).where(
            TokenRecuperacao.email == dados.email,
            TokenRecuperacao.codigo == dados.codigo,
            TokenRecuperacao.usado == False
        )
    ).first()

    if not token:
        raise HTTPException(status_code=400, detail="Código inválido")
    if token.expiracao < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")

    return {"valido": True}

@router.post("/resetar-senha")
def resetar_senha(dados: ResetarSenha, session: Session = Depends(get_session)):
    token = session.exec(
        select(TokenRecuperacao).where(
            TokenRecuperacao.email == dados.email,
            TokenRecuperacao.codigo == dados.codigo,
            TokenRecuperacao.usado == False
        )
    ).first()

    if not token:
        raise HTTPException(status_code=400, detail="Código inválido")
    if token.expiracao < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")

    usuario = session.exec(select(Usuario).where(Usuario.email == dados.email)).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.senha = hash_senha(dados.nova_senha)
    token.usado = True
    session.add(usuario)
    session.add(token)
    session.commit()

    return {"mensagem": "Senha resetada com sucesso"}