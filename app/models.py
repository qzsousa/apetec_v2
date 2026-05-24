from typing import Optional #define se o campo é obrigatório ou não
from sqlmodel import SQLModel, Field #field define a regra do campo, ou seja, se ele é pk, valor padrão, tamanho minimo
from datetime import date # importa a date


#classe para criar a tabela de usuarios na database
class Usuario(SQLModel, table=True):  #table=true para o SQLModel confirmar que é uma tabela realmente e não um schema de validação
    rm: int = Field(primary_key=True) 
    nome: str 
    telefone: str
    email: str
    turma_modulo: str
    senha: str

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # isso diz: "o id é opcional no momento de criar, mas o banco vai preencher automaticamente"
    marca: str 
    cor: str
    tipo: str
    tamanho: Optional[str] = None
    local_encontrado: str 
    data_entrada: Optional[date] = None # ele preenche automaticamente a data


class Chamado (SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str
    cor: str
    marca: str
    criterio_validacao: str
    data_perda: date
    local_perda: str
    status: str
    rm_usuario: int = Field(foreign_key="usuario.rm")
    id_item: Optional[int] = Field(default=None, foreign_key="item.id")

class Secretaria(SQLModel, table=True):
    cpf: str = Field(primary_key=True)
    nome: str
    email: str
    telefone: str
    senha: str

class UsuarioUpdate(SQLModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    turma_modulo: Optional[str] = None

class ItemUpdate(SQLModel):
    marca: Optional[str] = None
    cor: Optional[str] = None
    tipo: Optional[str] = None
    tamanho: Optional[str] = None
    local_encontrado: Optional[str] = None
    data_entrada: Optional[date] = None

class ChamadoUpdate(SQLModel):
    tipo: Optional[str] = None
    cor: Optional[str] = None
    marca: Optional[str] = None
    criterio_validacao: Optional[str] = None
    data_perda: Optional[date] = None
    local_perda: Optional[str] = None
    status: Optional[str] = None
    rm_usuario: Optional[int] = None
    id_item: Optional[int] = None

class LoginUsuario(SQLModel):
    rm: int
    senha: str

class LoginSecretaria(SQLModel):
    cpf: str
    senha: str