from app.models import AuditLog
from app.database import get_session
from sqlmodel import Session
from datetime import datetime


def registrar_auditoria(session: Session, ator_tipo: str, ator_cpf: str, acao: str, entidade: str, entidade_id=None, detalhes=None):
    try:
        log = AuditLog(ator_tipo=ator_tipo, ator_cpf=ator_cpf, acao=acao, entidade=entidade, entidade_id=str(entidade_id) if entidade_id is not None else None, detalhes=detalhes)
        session.add(log)
        session.commit()
    except Exception:
        pass