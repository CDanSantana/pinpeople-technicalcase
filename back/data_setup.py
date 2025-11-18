import csv
from datetime import datetime
from sqlalchemy import Engine, select
from sqlmodel import Session
from models import (
    Area, Cargo, Funcao, Localidade, TempoEmpresa, Genero, Geracao,
    OrganizationalUnit, Participante, RespostaPesquisa
)

def get_or_create(session, model, lookup: dict, defaults: dict = None, cache=None):
    defaults = defaults or {}
    cache = cache if cache is not None else {}
    key = (model.__tablename__, tuple(sorted(lookup.items())))
    if key in cache:
        return cache[key]
    query = select(model)
    for field, value in lookup.items():
        query = query.where(getattr(model, field) == value)
    instance = session.exec(query).scalars().first()
    if instance:
        cache[key] = instance
        return instance
    params = {**lookup, **defaults}
    instance = model(**params)
    session.add(instance)
    session.flush()   # garante .id sem commit
    cache[key] = instance
    return instance


def get_or_create_org_unit(session, name, level, parent, cache):
    parent_id = parent.id if parent else None
    key = ("org_unit", name, level, parent_id)
    if key in cache:
        return cache[key]
    query = (
        select(OrganizationalUnit)
        .where(OrganizationalUnit.nome == name)
        .where(OrganizationalUnit.level_name == level)
        .where(OrganizationalUnit.parent_id == parent_id)
    )
    unit = session.exec(query).scalars().first()
    if not unit:
        unit = OrganizationalUnit(
            nome=name,
            level_name=level,
            parent_id=parent_id
        )
        session.add(unit)
        session.flush()
    cache[key] = unit
    return unit


def load_data(engine: Engine):
    with Session(engine) as session:
        cache = {
            "Area": {},
            "Cargo": {},
            "Funcao": {},
            "Localidade": {},
            "TempoEmpresa": {},
            "Genero": {},
            "Geracao": {},
            "Participante": {},
            "OrgUnit": {}
        }
        with open('./data.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            total = 0
            for row in reader:
                total += 1
                participante = get_or_create(
                    session,
                    Participante,
                    lookup={"email_corporativo": row["email_corporativo"].strip()},
                    defaults={
                        "nome": row["nome"].strip(),
                        "email": row.get("email") or None
                    },
                    cache=cache["Participante"]
                )
                area = get_or_create(session, Area,
                    lookup={"nome": row["area"].strip()},
                    cache=cache["Area"]
                )
                cargo = get_or_create(session, Cargo,
                    lookup={"nome": row["cargo"].strip()},
                    cache=cache["Cargo"]
                )
                funcao = get_or_create(session, Funcao,
                    lookup={"nome": row["funcao"].strip()},
                    cache=cache["Funcao"]
                )
                localidade = get_or_create(session, Localidade,
                    lookup={"nome": row["localidade"].strip()},
                    cache=cache["Localidade"]
                )
                tempo_empresa = get_or_create(session, TempoEmpresa,
                    lookup={"descricao": row["tempo_de_empresa"].strip()},
                    cache=cache["TempoEmpresa"]
                )
                genero = get_or_create(session, Genero,
                    lookup={"nome": row["genero"].strip()},
                    cache=cache["Genero"]
                )
                geracao = get_or_create(session, Geracao,
                    lookup={"nome": row["geracao"].strip()},
                    cache=cache["Geracao"]
                )
                parent = None
                for level in [
                    "n0_empresa",
                    "n1_diretoria",
                    "n2_gerencia",
                    "n3_coordenacao",
                    "n4_area"
                ]:
                    name = row[level].strip()
                    if name:
                        parent = get_or_create_org_unit(
                            session, name, level, parent, cache=cache["OrgUnit"]
                        )
                org_unit = parent
                resposta = RespostaPesquisa(
                    data_resposta=datetime.strptime(
                        row["Data da Resposta"], "%d/%m/%Y"
                    ).date(),
                    participante_id=participante.id,
                    area_id=area.id,
                    cargo_id=cargo.id,
                    funcao_id=funcao.id,
                    localidade_id=localidade.id,
                    tempo_empresa_id=tempo_empresa.id,
                    genero_id=genero.id,
                    geracao_id=geracao.id,
                    org_unit_id=org_unit.id if org_unit else None,
                    interesse_cargo_score=int(row["Interesse no Cargo"]) if row["Interesse no Cargo"] else None,
                    contribuicao_score=int(row["Contribuição"]) if row["Contribuição"] else None,
                    aprendizado_desenvolvimento_score=int(row["Aprendizado e Desenvolvimento"]) if row["Aprendizado e Desenvolvimento"] else None,
                    feedback_score=int(row["Feedback"]) if row["Feedback"] else None,
                    interacao_gestor_score=int(row["Interação com Gestor"]) if row["Interação com Gestor"] else None,
                    clareza_carreira_score=int(row["Clareza sobre Possibilidades de Carreira"]) if row["Clareza sobre Possibilidades de Carreira"] else None,
                    expectativa_permanencia_score=int(row["Expectativa de Permanência"]) if row["Expectativa de Permanência"] else None,
                    enps_score=int(row["eNPS"]) if row["eNPS"] else None,
                    interesse_cargo_comment=row["Comentários - Interesse no Cargo"] or None,
                    contribuicao_comment=row["Comentários - Contribuição"] or None,
                    aprendizado_desenvolvimento_comment=row["Comentários - Aprendizado e Desenvolvimento"] or None,
                    feedback_comment=row["Comentários - Feedback"] or None,
                    interacao_gestor_comment=row["Comentários - Interação com Gestor"] or None,
                    clareza_carreira_comment=row["Comentários - Clareza sobre Possibilidades de Carreira"] or None,
                    expectativa_permanencia_comment=row["Comentários - Expectativa de Permanência"] or None,
                    enps_comment=row["[Aberta] eNPS"] or None
                )
                session.add(resposta)
            session.commit()
