from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from app.models import Item, ItemUpdate, ItemStatusEnum, Chamado, ChamadoStatusEnum, Usuario, Secretaria, Notificacao, AuditLog
from app.database import get_session
from sqlmodel import Session, select
from datetime import date, datetime, timedelta
from app.auth import get_usuario_atual, exigir_secretaria, is_secretaria
from app.audit import registrar_auditoria
from app.supabase_storage import upload_file
import uuid
import os

router = APIRouter(prefix="/item", tags=["Item"])


def _score_item_chamado(item: Item, chamado: Chamado) -> int:
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
def cadastrar_item(item: Item, session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    item.data_entrada = date.today()
    item.status = ItemStatusEnum.disponivel
    session.add(item)
    session.commit()
    session.refresh(item)

    # notificar chamados abertos com match
    try:
        chamados = session.exec(select(Chamado).where(Chamado.status == ChamadoStatusEnum.em_aberto)).all()
        api_key = os.getenv("RESEND_API_KEY")
        for ch in chamados:
            if _score_item_chamado(item, ch) >= 30:
                usuario_db = session.get(Usuario, ch.cpf_usuario_usuario)
                if usuario_db and usuario_db.email and api_key:
                    import resend
                    resend.api_key = api_key
                    try:
                        resend.Emails.send({
                            "from": "onboarding@resend.dev",
                            "to": usuario_db.email,
                            "subject": "Possível item encontrado - Apetec",
                            "html": f"<p>Olá {usuario_db.nome},</p><p>Cadastramos um item que pode ser o seu: <strong>{item.tipo} {item.marca} ({item.cor})</strong>.</p><p>Local: {item.local_encontrado}</p><p>Abra um chamado ou procure a secretaria.</p>",
                        })
                    except Exception:
                        pass
                notif = Notificacao(cpf_usuario=ch.cpf_usuario_usuario, tipo="item_encontrado", mensagem=f"Item compatível cadastrado: {item.tipo} {item.marca}")
                session.add(notif)
                session.commit()
    except Exception:
        pass

    registrar_auditoria(session, "secretaria", "secretaria", "cadastrar_item", "item", item.id)
    return item


@router.get("/")
def listar_itens(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = Query(None),
    cor: Optional[str] = Query(None),
    local: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    _: dict = Depends(exigir_secretaria),
):
    from typing import Optional
    stmt = select(Item)
    if tipo:
        stmt = stmt.where(Item.tipo.contains(tipo))
    if cor:
        stmt = stmt.where(Item.cor.contains(cor))
    if local:
        stmt = stmt.where(Item.local_encontrado.contains(local))
    if status:
        stmt = stmt.where(Item.status == status)
    stmt = stmt.offset(skip).limit(limit)
    return session.exec(stmt).all()


@router.get("/disponiveis")
def listar_disponiveis(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = Query(None),
    cor: Optional[str] = Query(None),
    local: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    usuario: dict = Depends(get_usuario_atual),
):
    from typing import Optional
    stmt = select(Item).where(Item.status == ItemStatusEnum.disponivel)
    if tipo:
        stmt = stmt.where(Item.tipo.contains(tipo))
    if cor:
        stmt = stmt.where(Item.cor.contains(cor))
    if local:
        stmt = stmt.where(Item.local_encontrado.contains(local))
    stmt = stmt.offset(skip).limit(limit)
    return session.exec(stmt).all()


@router.get("/{id}")
def buscar_item(id: int, session: Session = Depends(get_session), _: dict = Depends(get_usuario_atual)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@router.put("/{id}")
def atualizar_dados_item(dados: ItemUpdate, id: int, session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    dados_novos = dados.model_dump(exclude_unset=True)
    item.sqlmodel_update(dados_novos)
    session.commit()
    session.refresh(item)
    registrar_auditoria(session, "secretaria", "secretaria", "atualizar_item", "item", item.id)
    return item


@router.delete("/{id}", status_code=204)
def deletar_item(id: int, session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    session.delete(item)
    session.commit()
    registrar_auditoria(session, "secretaria", "secretaria", "deletar_item", "item", id)
    return None


@router.post("/{id}/foto", status_code=200)
async def upload_foto_item(id: int, file: UploadFile = File(...), session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lstrip(".").lower()
    allowed = {"png", "jpg", "jpeg", "webp", "gif"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Extensao nao permitida. Use png, jpg, jpeg, webp ou gif.")
    content = await file.read()
    max_size = 5 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Maximo 5MB.")
    if not ext:
        ext = "bin"
    path = "itens/" + str(id) + "/" + uuid.uuid4().hex + "." + ext
    try:
        url = upload_file(content, file.content_type or "application/octet-stream", path)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha no upload: {e}")
    item.fotoUrl = url
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post("/{id}/reivindicar", status_code=201)
def reivindicar_item(id: int, session: Session = Depends(get_session), usuario: dict = Depends(get_usuario_atual)):
    if is_secretaria(usuario):
        raise HTTPException(status_code=403, detail="Secretaria não pode reivindicar")
    item = session.get(Item, id)
    if not item or item.status != ItemStatusEnum.disponivel:
        raise HTTPException(status_code=404, detail="Item não disponível")
    chamado = Chamado(
        tipo=item.tipo,
        cor=item.cor,
        marca=item.marca,
        criterio_validacao="reivindicado pelo aluno",
        data_perda=item.data_entrada or date.today(),
        local_perda=item.local_encontrado,
        status=ChamadoStatusEnum.em_aberto,
        cpf_usuario_usuario=usuario["sub"],
        id_item=item.id,
    )
    session.add(chamado)
    session.commit()
    session.refresh(chamado)

    # notificar secretaria
    try:
        api_key = os.getenv("RESEND_API_KEY")
        secs = session.exec(select(Secretaria)).all()
        if api_key:
            import resend
            resend.api_key = api_key
            for sec in secs:
                try:
                    resend.Emails.send({
                        "from": "onboarding@resend.dev",
                        "to": sec.email,
                        "subject": "Item reivindicado - Apetec",
                        "html": f"<p>O item {item.tipo} {item.marca} ({item.cor}) foi reivindicado por um aluno (CPF {usuario['sub']}).</p><p>Valide na secretaria.</p>",
                    })
                except Exception:
                    pass
        for sec in secs:
            notif = Notificacao(cpf_usuario=sec.cpf, tipo="reivindicacao", mensagem=f"Item {item.tipo} reivindicado por aluno {usuario['sub']}")
            session.add(notif)
        session.commit()
    except Exception:
        pass

    registrar_auditoria(session, "usuario", usuario["sub"], "reivindicar_item", "item", item.id)
    return chamado


@router.post("/expirar", status_code=200)
def expirar_itens(session: Session = Depends(get_session), _: dict = Depends(exigir_secretaria)):
    limite = date.today() - timedelta(days=90)
    itens = session.exec(select(Item).where(Item.status == ItemStatusEnum.disponivel)).all()
    count = 0
    for it in itens:
        if it.data_entrada and it.data_entrada < limite:
            it.status = ItemStatusEnum.doado
            it.data_saida = date.today()
            session.add(it)
            count += 1
    session.commit()
    registrar_auditoria(session, "secretaria", "secretaria", "expirar_itens", "item", None, f"{count} itens doados")
    return {"doado": count}