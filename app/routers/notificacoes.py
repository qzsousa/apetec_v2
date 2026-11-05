from fastapi import APIRouter, Depends, HTTPException, Query
from app.models import Notificacao
from app.database import get_session
from sqlmodel import Session, select
from app.auth import get_usuario_atual

router = APIRouter(prefix="/notificacoes", tags=["Notificacoes"])


@router.get("/me")
def minhas_notificacoes(session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    cpf = usuario["sub"]
    notifs = session.exec(select(Notificacao).where(Notificacao.cpf_usuario == cpf).order_by(Notificacao.criado_em.desc())).all()
    return notifs


@router.post("/{id}/ler")
def marcar_lida(id: int, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    n = session.get(Notificacao, id)
    if not n:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    if str(n.cpf_usuario) != str(usuario["sub"]):
        raise HTTPException(status_code=403, detail="Sem permissão")
    n.lida = True
    session.add(n)
    session.commit()
    return n