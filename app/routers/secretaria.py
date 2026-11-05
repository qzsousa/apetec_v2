from fastapi import APIRouter, Depends, HTTPException
from app.models import Secretaria, SecretariaPublic, Item, ItemStatusEnum, Chamado, ChamadoStatusEnum, Usuario
from app.database import get_session
from sqlmodel import Session, select, func
from datetime import date, timedelta
from app.auth import get_usuario_atual, is_secretaria


router = APIRouter(prefix="/secretaria", tags=["Secretaria"])


@router.get("/me")
def meu_perfil(session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not is_secretaria(usuario_atual):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    cpf = usuario_atual["sub"]
    secretaria = session.get(Secretaria, cpf)
    if not secretaria:
        raise HTTPException(status_code=404, detail="Secretaria não encontrada")
    return SecretariaPublic(**secretaria.model_dump(exclude={"senha"}))


@router.get("/relatorio")
def relatorio(session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not is_secretaria(usuario_atual):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")

    itens = session.exec(select(Item)).all()
    chamados = session.exec(select(Chamado)).all()

    total_itens = len(itens)
    disponiveis = sum(1 for i in itens if i.status == ItemStatusEnum.disponivel)
    entregues = sum(1 for i in itens if i.status == ItemStatusEnum.entregue)
    doados = sum(1 for i in itens if i.status == ItemStatusEnum.doado)

    por_status = {}
    for c in chamados:
        por_status[c.status.value] = por_status.get(c.status.value, 0) + 1

    limite = date.today() - timedelta(days=30)
    nao_reclamados = [i for i in itens if i.status == ItemStatusEnum.disponivel and i.data_entrada and i.data_entrada < limite]

    taxa = (entregues / total_itens * 100) if total_itens else 0.0

    return {
        "total_itens": total_itens,
        "disponiveis": disponiveis,
        "entregues": entregues,
        "doados": doados,
        "taxa_devolucao": round(taxa, 2),
        "chamados_por_status": por_status,
        "total_chamados": len(chamados),
        "itens_nao_reclamados_30d": [{"id": i.id, "tipo": i.tipo, "marca": i.marca, "cor": i.cor, "data_entrada": str(i.data_entrada), "local": i.local_encontrado} for i in nao_reclamados],
    }
