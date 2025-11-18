from datetime import date, datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, TEXT, Index
import re

def to_snake(name: str) -> str:
    # Coloca _ antes de transições de minúscula→maiúscula, e entre blocos de maiúsculas
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    return s.lower()


class _BaseModel(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
    is_active: bool = Field(default=True)

    @classmethod
    def get_snake_case_name(cls):
        return to_snake(cls.__name__)

class Area(_BaseModel, table=True):
    nome: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'administrativo', 'comercial'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="area")


class Cargo(_BaseModel, table=True):
    nome: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'estagiário', 'analista'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="cargo")


class Funcao(_BaseModel, table=True):
    nome: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'profissional', 'gestor'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="funcao")


class Localidade(_BaseModel, table=True):
    nome: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'brasília', 'recife'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="localidade")


class TempoEmpresa(_BaseModel, table=True):
    __tablename__ = "tempo_empresa"
    descricao: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'menos de 1 ano', 'entre 1 e 2 anos'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="tempo_empresa")


class Genero(_BaseModel, table=True):
    nome: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'masculino', 'feminino', 'outro'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="genero")


class Geracao(_BaseModel, table=True):
    nome: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="E.g., 'geração z', 'geração y'",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="geracao")


class OrganizationalUnit(_BaseModel, table=True):
    __tablename__ = "organizational_unit"
    nome: str = Field(max_length=255, index=True)
    level_name: str = Field(
        max_length=100,
        index=True,
        description="E.g., 'n0_empresa', 'n1_diretoria', 'n4_area'",
    )
    parent_id: Optional[int] = Field(
        default=None, foreign_key="organizational_unit.id", index=True
    )
    parent: Optional["OrganizationalUnit"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs=dict(remote_side="OrganizationalUnit.id"),
    )
    children: List["OrganizationalUnit"] = Relationship(back_populates="parent")
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="org_unit")




class Participante(_BaseModel, table=True):
    nome: str = Field(max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    email_corporativo: str = Field(
        max_length=255,
        index=True,
        unique=True,
        description="Main unique identifier for an employee",
    )
    respostas: List["RespostaPesquisa"] = Relationship(back_populates="participante")




class RespostaPesquisa(_BaseModel, table=True):
    __tablename__ = "resposta_pesquisa"
    data_resposta: date = Field(
        index=True,
        description="Date of the survey response, indexed for time-series analysis",
    )
    participante_id: int = Field(foreign_key="participante.id", index=True)
    area_id: int = Field(foreign_key="area.id", index=True)
    cargo_id: int = Field(foreign_key="cargo.id", index=True)
    funcao_id: int = Field(foreign_key="funcao.id", index=True)
    localidade_id: int = Field(foreign_key="localidade.id", index=True)
    tempo_empresa_id: int = Field(foreign_key="tempo_empresa.id", index=True)
    genero_id: int = Field(foreign_key="genero.id", index=True)
    geracao_id: int = Field(foreign_key="geracao.id", index=True)
    org_unit_id: int = Field(
        foreign_key="organizational_unit.id",
        index=True,
        description="Links to the lowest-level unit (e.g., n4_area) for this response",
    )
    participante: Participante = Relationship(back_populates="respostas")
    area: Area = Relationship(back_populates="respostas")
    cargo: Cargo = Relationship(back_populates="respostas")
    funcao: Funcao = Relationship(back_populates="respostas")
    localidade: Localidade = Relationship(back_populates="respostas")
    tempo_empresa: TempoEmpresa = Relationship(back_populates="respostas")
    genero: Genero = Relationship(back_populates="respostas")
    geracao: Geracao = Relationship(back_populates="respostas")
    org_unit: OrganizationalUnit = Relationship(back_populates="respostas")
    interesse_cargo_score: Optional[int] = Field(default=None)
    contribuicao_score: Optional[int] = Field(default=None)
    aprendizado_desenvolvimento_score: Optional[int] = Field(default=None)
    feedback_score: Optional[int] = Field(default=None)
    interacao_gestor_score: Optional[int] = Field(default=None)
    clareza_carreira_score: Optional[int] = Field(default=None)
    expectativa_permanencia_score: Optional[int] = Field(default=None)
    enps_score: Optional[int] = Field(default=None)
    interesse_cargo_comment: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    contribuicao_comment: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    aprendizado_desenvolvimento_comment: Optional[str] = Field(
        default=None, sa_column=Column(TEXT)
    )
    feedback_comment: Optional[str] = Field(default=None, sa_column=Column(TEXT))
    interacao_gestor_comment: Optional[str] = Field(
        default=None, sa_column=Column(TEXT)
    )
    clareza_carreira_comment: Optional[str] = Field(
        default=None, sa_column=Column(TEXT)
    )
    expectativa_permanencia_comment: Optional[str] = Field(
        default=None, sa_column=Column(TEXT)
    )
    enps_comment: Optional[str] = Field(
        default=None, sa_column=Column("aberta_enps_comment", TEXT)
    )




    class Config:
        table_args = (
            Index("idx_area_data", "area_id", "data_resposta"),
            Index("idx_cargo_data", "cargo_id", "data_resposta"),
            Index("idx_localidade_data", "localidade_id", "data_resposta"),
            Index("idx_org_unit_data", "org_unit_id", "data_resposta"),
            Index("idx_participante_data", "participante_id", "data_resposta"),
        )

