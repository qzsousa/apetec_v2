from typing import Optional
from sqlmodel import SQLModel, Field
from enum import Enum
from pydantic import EmailStr
from datetime import date, datetime


class CargoEnum(str, Enum):
    aluno = "aluno"
    professor = "professor"
    administrativo = "administrativo"
    cozinha = "cozinha"
    limpeza = "limpeza"
    seguranca = "segurança"


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


class ChamadoStatusEnum(str, Enum):
    em_aberto = "em_aberto"
    respondido = "respondido"
    finalizado = "finalizado"


class Usuario(SQLModel, table=True):
    cpf: str = Field(primary_key=True)
    nome: str
    telefone: str
    email: EmailStr = Field(index=True)
    turma_modulo: TurmaModuloEnum
    cargo: CargoEnum
    senha: str


class ItemStatusEnum(str, Enum):
    disponivel = "disponivel"
    entregue = "entregue"
    doado = "doado"


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    marca: str
    cor: str
    tipo: str
    tamanho: Optional[str] = None
    local_encontrado: str
    data_entrada: Optional[date] = None
    fotoUrl: Optional[str] = None
    status: ItemStatusEnum = Field(default=ItemStatusEnum.disponivel)
    data_saida: Optional[date] = None


class Chamado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str
    cor: str
    marca: str
    criterio_validacao: str
    data_perda: date
    local_perda: str
    status: ChamadoStatusEnum = Field(default=ChamadoStatusEnum.em_aberto)
    cpf_usuario_usuario: str = Field(foreign_key="usuario.cpf", index=True)
    id_item: Optional[int] = Field(default=None, foreign_key="item.id", index=True)
    data_resposta: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    entregue_por: Optional[str] = Field(default=None, foreign_key="secretaria.cpf")
    observacao_entrega: Optional[str] = None
    notificado: bool = Field(default=False)


class Secretaria(SQLModel, table=True):
    cpf: str = Field(primary_key=True)
    nome: str
    email: str = Field(index=True)
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
    email: str = Field(index=True)
    codigo: str
    expiracao: datetime
    usado: bool = Field(default=False)


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
    fotoUrl: Optional[str] = None
    status: Optional[ItemStatusEnum] = None
    data_saida: Optional[date] = None


class ChamadoUpdate(SQLModel):
    tipo: Optional[str] = None
    cor: Optional[str] = None
    marca: Optional[str] = None
    criterio_validacao: Optional[str] = None
    data_perda: Optional[date] = None
    local_perda: Optional[str] = None
    status: Optional[ChamadoStatusEnum] = None
    cpf_usuario: Optional[str] = None
    id_item: Optional[int] = None
    data_resposta: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    entregue_por: Optional[str] = None
    observacao_entrega: Optional[str] = None
    notificado: Optional[bool] = None


class LoginUsuario(SQLModel):
    cpf: str
    senha: str


class LoginSecretaria(SQLModel):
    cpf: str
    senha: str


class SolicitarRecuperacao(SQLModel):
    email: str


class VerificarCodigo(SQLModel):
    email: str
    codigo: str


class ResetarSenha(SQLModel):
    email: str
    codigo: str
    nova_senha: str


class UsuarioPublic(SQLModel):
    cpf: str
    nome: str
    telefone: str
    email: EmailStr
    turma_modulo: TurmaModuloEnum
    cargo: CargoEnum


class SecretariaPublic(SQLModel):
    cpf: str
    nome: str
    email: str
    telefone: str
