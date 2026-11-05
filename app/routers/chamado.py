from fastapi import APIRouter, Depends, HTTPException, Query
from app.models import Chamado, ChamadoUpdate, ChamadoStatusEnum, Item, ItemStatusEnum, Usuario, Mensagem, MensagemCreate
from app.database import get_session
from sqlmodel import Session, select
from datetime import datetime
from app.auth import exigir_secretaria, get_usuario_atual, is_secretaria
import os

router = APIRouter(prefix="/chamados", tags=["Chamados"])


def _score(item: Item, chamado: Chamado) -> int:
    s = 0
    if item.tipo and chamado.tipo and item.tipo.lower() == chamado.tipo.lower():
        s += 40
    elif item.tipo and chamado.tipo and (chamado.tipo.lower() in item.tipo.lower() or item.tipo.lower() in chamado.tipo.lower()):
        s += 20
    if item.cor and chamado.cor and item.cor.lower() == chamado.cor.lower():
        s += 20
    if item.marca and chamado.marca and item.marca.lower() == chamado.marca.lower():
        s += 15
    if item.local_encontrado and chamado.local_perda:
        a, b = item.local_encontrado.lower(), chamado.local_perda.lower()
        if a in b or b in a:
            s += 15
    if item.data_entrada and chamado.data_perda:
        try:
            delta = abs((item.data_entrada - chamado.data_perda).days)
            if delta <= 7:
                s += max(0, 10 - delta)
        except Exception:
            pass
    return s


@router.post("/", status_code=201)
def cadastrar_chamado(chamado: Chamado, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    chamado.cpf_usuario_usuario = usuario["sub"]
    chamado.status = ChamadoStatusEnum.em_aberto
    chamado.data_perda = datetime.strptime(str(chamado.data_perda), "%Y-%m-%d").date()
    session.add(chamado)
    session.commit()
    session.refresh(chamado)
    return chamado


@router.get("/")
def listar_chamados(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    usuario: dict = Depends(get_usuario_atual),
):
    if is_secretaria(usuario):
        chamados = session.exec(select(Chamado).offset(skip).limit(limit)).all()
    else:
        cpf = usuario["sub"]
        chamados = session.exec(
            select(Chamado).where(Chamado.cpf_usuario_usuario == cpf).offset(skip).limit(limit)
        ).all()
    return chamados


@router.get("/{id}")
def buscar_chamado(id: int, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if not (is_secretaria(usuario) or str(chamado.cpf_usuario_usuario) == str(usuario.get("sub"))):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    return chamado


@router.get("/{id}/sugestoes")
def sugestoes_item(id: int, session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    itens = session.exec(select(Item).where(Item.status == ItemStatusEnum.disponivel)).all()
    scored = []
    for it in itens:
        sc = _score(it, chamado)
        if sc >= 30:
            scored.append((sc, it))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"score": sc, "item": it} for sc, it in scored]


@router.put("/{id}")
def atualizar_chamado(dados: ChamadoUpdate, id: int, session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    chamado.sqlmodel_update(dados.model_dump(exclude_unset=True))
    session.commit()
    session.refresh(chamado)
    return chamado


@router.post("/{id}/vincular", status_code=200)
def vincular_item(id: int, payload: dict, session: Session = Depends(get_session), usuario: dict = Depends(exigir_secretaria)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    id_item = payload.get("id_item")
    if id_item is None:
        raise HTTPException(status_code=400, detail="id_item obrigatório")
    item = session.get(Item, id_item)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if item.status != ItemStatusEnum.disponivel:
        raise HTTPException(status_code=400, detail="Item indisponível")
    chamado.id_item = item.id
    chamado.status = ChamadoStatusEnum.respondido
    chamado.data_resposta = datetime.utcnow()
    chamado.notificado = False
    obs = payload.get("observacao")
    if obs:
        chamado.observacao_entrega = obs
    session.add(chamado)
    session.commit()
    session.refresh(chamado)

    # notificação por email
    try:
        usuario_db = session.get(Usuario, chamado.cpf_usuario_usuario)
        if usuario_db and usuario_db.email:
            api_key = os.getenv("RESEND_API_KEY")
            if api_key:
                import resend
                resend.api_key = api_key
                resend.Emails.send({
                    "from": "onboarding@resend.dev",
                    "to": usuario_db.email,
                    "subject": "Item encontrado - Apetec",
                    "html": f"<p>Olá {usuario_db.nome},</p><p>Encontramos um item que pode ser seu: <strong>{item.tipo} {item.marca} ({item.cor})</strong>.</p><p>Local: {item.local_encontrado}</p><p>Retire na secretaria. Critério de validação: {chamado.criterio_validacao}</p>",
                })
                chamado.notificado = True
                session.add(chamado)
                session.commit()
    except Exception:
        pass

    return chamado


@router.post("/{id}/entregar", status_code=200)
def entregar_item(id: int, payload: dict, session: Session = Depends(get_session), usuario: dict = Depends(exigir_secretaria)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if chamado.status != ChamadoStatusEnum.respondido or not chamado.id_item:
        raise HTTPException(status_code=400, detail="Chamado não possui item vinculado")
    item = session.get(Item, chamado.id_item)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    confirmado = payload.get("confirmado", False)
    if not confirmado:
        raise HTTPException(status_code=400, detail="Confirmação de identidade obrigatória")
    chamado.status = ChamadoStatusEnum.finalizado
    chamado.data_entrega = datetime.utcnow()
    chamado.entregue_por = usuario["sub"]
    obs = payload.get("observacao")
    if obs:
        chamado.observacao_entrega = obs
    item.status = ItemStatusEnum.entregue
    item.data_saida = datetime.utcnow().date()
    session.add(chamado)
    session.add(item)
    session.commit()
    session.refresh(chamado)
    return chamado


@router.get("/{id}/mensagens")
def listar_mensagens(id: int, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if not (is_secretaria(usuario) or str(chamado.cpf_usuario_usuario) == str(usuario.get("sub"))):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    msgs = session.exec(select(Mensagem).where(Mensagem.id_chamado == id).order_by(Mensagem.criado_em)).all()
    return msgs


@router.post("/{id}/mensagens", status_code=201)
def enviar_mensagem(id: int, dados: MensagemCreate, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    if not (is_secretaria(usuario) or str(chamado.cpf_usuario_usuario) == str(usuario.get("sub"))):
        raise HTTPException(status_code=403, detail="Usuário sem permissão")
    tipo = "secretaria" if is_secretaria(usuario) else "usuario"
    msg = Mensagem(id_chamado=id, autor_tipo=tipo, autor_cpf=usuario["sub"], texto=dados.texto)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg


@router.delete("/{id}", status_code=204)
def deletar_chamado(id: int, session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    chamado = session.get(Chamado, id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    session.delete(chamado)
    session.commit()
