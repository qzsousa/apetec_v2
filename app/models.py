from typing import Optional #define se o campo é obrigatório ou não
from sqlmodel import SQLModel, Field #field define a regra do campo, ou seja, se ele é pk, valor padrão, tamanho minimo
from enum import Enum #enum é para criar um tipo de dado com opções pré-definidas
from pydantic import EmailStr #valida se o campo é um email válido
from datetime import date, datetime # importa a date



class CargoEnum(str, Enum):
    aluno         = "aluno"
    professor     = "professor"
    administrativo = "administrativo"
    cozinha       = "cozinha"
    limpeza       = "limpeza"
    seguranca     = "segurança"

class TurmaModuloEnum(str, Enum):
    turma_1dsa = "1 DS A"
    turma_1dsb = "1 DS B"
    turma_2dsa = "2 DS A"
    turma_2dsb = "2 DS B"
    turma_3dsa = "3 DS A"
    turma_3dsb = "3 DS B"
    turma_1adma = "1 ADM A"
    turma_1admb = "1 ADM B"
    turma_2adma = "2 ADM A"
    turma_2admb = "2 ADM B"
    turma_3adma = "3 ADM A"
    turma_3admb = "3 ADM B"
    modulo_adm = "Módular ADM"
    modulo_ds = "Módular DS"

#classe para criar a tabela de usuarios na database
class Usuario(SQLModel, table=True):  #table=true para o SQLModel confirmar que é uma tabela realmente e não um schema de validação
    cpf: str = Field(primary_key=True) 
    nome: str 
    telefone: str
    email: EmailStr
    turma_modulo: TurmaModuloEnum
    cargo: CargoEnum
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
    cpf_usuario_usuario: str = Field(foreign_key="usuario.cpf")
    id_item: Optional[int] = Field(default=None, foreign_key="item.id")

class Secretaria(SQLModel, table=True):
    cpf: str = Field(primary_key=True)
    nome: str
    email: str
    telefone: str
    senha: str

class UsuarioCreate(SQLModel):
    cpf: str
    nome: str
    telefone: str
    email: EmailStr
    turma_modulo: str
    cargo: CargoEnum
    senha: str

class TokenRecuperacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str                          # e-mail do usuário
    codigo: str                         # 6 dígitos gerados
    expiracao: datetime                 # agora + 15 minutos
    usado: bool = Field(default=False)  # True após uso, para invalidar

class UsuarioUpdate(SQLModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    turma_modulo: Optional[str] = None
    senha: Optional[str] = None

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
    cpf_usuario: Optional[str] = None
    id_item: Optional[int] = None

class LoginUsuario(SQLModel):
    cpf: str
    senha: str

class LoginSecretaria(SQLModel):
    cpf: str
    senha: str

class TokenRecuperacao(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  # adiciona essa linha
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    codigo: str
    expiracao: datetime
    usado: bool = Field(default=False)

class SolicitarRecuperacao(SQLModel):
    email: str

class VerificarCodigo(SQLModel):
    email: str
    codigo: str

class ResetarSenha(SQLModel):
    email: str
    codigo: str
    nova_senha: str