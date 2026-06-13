from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import LoginUsuario, LoginSecretaria, Usuario, Secretaria
from app.auth import verificar_senha, criar_token

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

