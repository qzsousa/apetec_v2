from fastapi import APIRouter, Depends, HTTPException
from app.models import Item, ItemUpdate
from app.database import get_session
from sqlmodel import Session, select
from datetime import date

router = APIRouter(prefix="/item", tags=["Item"])

# cadastra item na database
@router.post("/", status_code = 201)
def cadastrar_item(item: Item, session: Session = Depends(get_session)): #adcionar item na table item na database
    item.data_entrada = date.today()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

#lista os itens da table item
@router.get("/")
def listar_itens (session: Session = Depends(get_session)): # listar todos os itens importando dados da database
    itens = session.exec(select(Item)).all()
    return itens

#busca item pelo ID
@router.get("/{id}")
def buscar_item(id: int, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@router.put("/{id}")
def atualizar_dados_item(dados: ItemUpdate, id: int, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    dados_novos = dados.model_dump(exclude_unset=True)
    item.sqlmodel_update(dados_novos)
    session.commit()
    session.refresh(item)
    return item

@router.delete("/{id}", status_code=204)
def deletar_item(id: int, session: Session = Depends(get_session)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    session.delete(item)
    session.commit()
    