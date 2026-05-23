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

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) # isso diz: "o id é opcional no momento de criar, mas o banco vai preencher automaticamente"
    marca: str 
    cor: str
    tamanho: Optional[str] = None
    local_encontrado: str 
    data_entrada: date

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
    id_item: int = Field(foreign_key="item.id")

class UsuarioUpdate(SQLModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    turma_modulo: Optional[str] = None
