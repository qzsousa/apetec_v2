from fastapi import APIRouter, Depends, HTTPException
from app.models import Usuario, UsuarioCreate, UsuarioUpdate
from app.database import get_session
from sqlmodel import Session, select
from app.auth import hash_senha, get_usuario_atual



router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", status_code = 201) # cria usuario 
def cadastrar_usuario(usuario: UsuarioCreate, session: Session = Depends(get_session)):
    db_usuario = Usuario(**usuario.model_dump())
    db_usuario.senha = hash_senha(db_usuario.senha)
    session.add(db_usuario)
    session.commit()
    session.refresh(db_usuario)
    return db_usuario

@router.get("/")
def listar_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario)).all() # aqui ele executa a consulta para selecionar todos os usuarios da tabela Usuario e retorna uma lista de objetos Usuario, ou seja, ele retorna todos os usuarios cadastrados no banco de dados
    return usuarios

@router.get("/me")
def meu_perfil(session: Session = Depends(get_session), usuario_atual: dict = Depends(get_usuario_atual)):
    cpf = usuario_atual["sub"]
    print(f"CPF do token: '{cpf}'")
    usuario = session.get(Usuario, cpf)
    print(f"Usuario encontrado: {usuario}")
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.get("/{cpf}")
def buscar_usuario(cpf: str, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, cpf) # aqui ele busca o usuario pelo cpf, ou seja, ele procura o usuario com o cpf especificado e retorna o objeto Usuario correspondente, ou seja, ele retorna o usuario encontrado no banco de dados
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado") # aqui ele verifica se o usuario foi encontrado, ou seja, se o usuario for None, ele levanta uma exceção HTTPException com status code 404 e uma mensagem de detalhe "Usuário não encontrado", ou seja, ele infocpfa que o usuario não existe no banco de dados
    return usuario

@router.put("/{cpf}")
def atualizar_dados_usuario(dados: UsuarioUpdate, cpf: str, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, cpf) # aqui ele busca o usuario pelo cpf, ou seja, ele procura o usuario com o cpf especificado e retorna o objeto Usuario correspondente, ou seja, ele retorna o usuario encontrado no banco de dados
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado") # aqui ele verifica se o usuario foi encontrado, ou seja, se o usuario for None, ele levanta uma exceção HTTPException com status code 404 e uma mensagem de detalhe "Usuário não encontrado", ou seja, ele infocpfa que o usuario não existe no banco de dados
    if dados.senha:
        dados.senha = hash_senha(dados.senha) # aqui ele verifica se a senha foi enviada na requisição de atualização, ou seja, se o campo senha do objeto UsuarioUpdate for diferente de None, ele aplica a função hash_senha para criptografar a senha antes de atualizar o usuario no banco de dados, ou seja, ele garante que a senha seja armazenada de forma segura no banco de dados, mesmo que seja atualizada posteriormente
    dados_novos = dados.model_dump(exclude_unset=True) # aqui ele converte o objeto UsuarioUpdate em um dicionário, ou seja, ele pega os dados do objeto UsuarioUpdate e cria um dicionário com esses dados, excluindo os campos que não foram definidos (unset), ou seja, ele só inclui no dicionário os campos que foram realmente enviados na requisição de atualização
    usuario.sqlmodel_update(dados_novos) # aqui ele atualiza o objeto usuario com os dados do dicionário, ou seja, ele pega os dados do dicionário e atualiza os campos correspondentes do objeto usuario, ou seja, ele modifica o objeto usuario com os novos dados enviados na requisição de atualização
    session.commit()
    session.refresh(usuario) # aqui ele atualiza o objeto usuario com os dados do banco de dados, ou seja, se o banco de dados gerar um id automaticamente, ele vai atualizar o objeto usuario com esse id
    return usuario



@router.delete("/{cpf}", status_code=204)
def deletar_usuario(cpf: str, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, cpf)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    session.delete(usuario) # aqui ele marca o usuario para ser deletado, ou seja, ele prepara para remover o usuario do banco de dados, mas ainda não remove de fato
    session.commit()   # aqui ele conficpfa a remoção do usuario no banco de dados, ou seja, ele executa a operação de delete no banco de dados, removendo o usuario de fato

