from fastapi import APIRouter, Depends, HTTPException
from app.models import Chamado, ChamadoUpdate
from app.database import get_session
from sqlmodel import Session, select
from datetime import date, datetime
from app.auth import get_usuario_atual

router = APIRouter(prefix="/chamados", tags=["Chamados"])

#cadastra um novo chamado
@router.post("/", status_code=201)
def cadastrar_chamado(chamado: Chamado, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    chamado.cpf_usuario_usuario = usuario["sub"] #associa o chamado ao cpf do usuario logado
    chamado.status = "em_aberto" #pre-define todo chamado novo aberto como "em_aberto"
    chamado.data_perda = datetime.strptime(str(chamado.data_perda), "%Y-%m-%d").date() #converte a data str para date
    session.add(chamado)
    session.commit()
    session.refresh(chamado)
    return chamado

@router.get("/")
def listar_chamados(session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    cpf = usuario["sub"]
    chamados = session.exec(select(Chamado).where(Chamado.cpf_usuario_usuario == cpf)).all() # filtra somente os chamados do usuario logado 
    return chamados

@router.get("/{id}")
def buscar_chamado(id: int, session: Session = Depends(get_session)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado

@router.put("/{id}")
def atualizar_chamado(dados: ChamadoUpdate, id: int, session: Session = Depends(get_session)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    chamado.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.commit()
    session.refresh(chamado)
    return chamado

@router.delete("/{id}", status_code=204)
def deletar_chamado(id: int, session: Session = Depends(get_session)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    session.delete(chamado)
    session.commit()