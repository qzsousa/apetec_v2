from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.models import Secretaria, SecretariaPublic, Item, ItemStatusEnum, Chamado, ChamadoStatusEnum, Usuario, AuditLog, Notificacao
from app.database import get_session
from sqlmodel import Session, select
from datetime import date, timedelta
import csv, io
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

    por_status = {s.value: 0 for s in ChamadoStatusEnum}
    for c in chamados:
        por_status[c.status.value] = por_status.get(c.status.value, 0) + 1

    chamados_com_item = [c for c in chamados if c.id_item is not None]
    cruzamentos = []
    for c in chamados_com_item:
        item = session.get(Item, c.id_item)
        cruzamentos.append({
            "chamado_id": c.id,
            "status": c.status.value,
            "item_id": c.id_item,
            "item_tipo": item.tipo if item else None,
            "item_marca": item.marca if item else None,
            "item_cor": item.cor if item else None,
        })

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
        "chamados_em_aberto": por_status.get(ChamadoStatusEnum.em_aberto.value, 0),
        "chamados_respondidos": por_status.get(ChamadoStatusEnum.respondido.value, 0),
        "chamados_finalizados": por_status.get(ChamadoStatusEnum.finalizado.value, 0),
        "total_chamados": len(chamados),
        "chamados_com_item": len(chamados_com_item),
        "chamados_sem_item": len(chamados) - len(chamados_com_item),
        "cruzamentos": cruzamentos,
        "cruzamento": cruzamentos,
        "cruzamento_de_itens": cruzamentos,
        "itens_cruzados": cruzamentos,
        "itens_nao_reclamados_30d": [{"id": i.id, "tipo": i.tipo, "marca": i.marca, "cor": i.cor, "data_entrada": str(i.data_entrada), "local": i.local_encontrado} for i in nao_reclamados],
    }


@router.get("/auditoria")
def auditoria(skip: int = 0, limit: int = 100, session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not is_secretaria(usuario_atual):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    logs = session.exec(select(AuditLog).order_by(AuditLog.criado_em.desc()).offset(skip).limit(limit)).all()
    return logs


@router.get("/exportar/itens")
def exportar_itens(session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not is_secretaria(usuario_atual):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    itens = session.exec(select(Item)).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "tipo", "marca", "cor", "tamanho", "local_encontrado", "data_entrada", "status", "fotoUrl"])
    for i in itens:
        w.writerow([i.id, i.tipo, i.marca, i.cor, i.tamanho, i.local_encontrado, i.data_entrada, i.status, i.fotoUrl])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=itens.csv"})


@router.get("/exportar/chamados")
def exportar_chamados(session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    if not is_secretaria(usuario_atual):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    chamados = session.exec(select(Chamado)).all()
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "tipo", "marca", "cor", "local_perda", "data_perda", "status", "cpf_usuario", "id_item", "codigo_retirada"])
    for c in chamados:
        w.writerow([c.id, c.tipo, c.marca, c.cor, c.local_perda, c.data_perda, c.status, c.cpf_usuario_usuario, c.id_item, c.codigo_retirada])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=chamados.csv"})
