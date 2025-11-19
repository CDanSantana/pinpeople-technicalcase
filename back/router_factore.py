from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import SQLModel, Session, select
from typing import Type, Optional, List, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql import Select
from sqlalchemy import and_, func, or_
from sqlalchemy import Date, DateTime
from sqlalchemy.orm.attributes import InstrumentedAttribute
from datetime import datetime, date
from pydantic import BaseModel, create_model
from typing import List


def parse_value_for_column(column: InstrumentedAttribute, raw_value: str):
    python_type = None
    try:
        python_type = column.property.columns[0].type.python_type
    except:
        pass
    if isinstance(raw_value, list):
        return [parse_value_for_column(column, v) for v in raw_value]
    if python_type is date:
        try:
            return date.fromisoformat(raw_value)
        except:
            pass
    if python_type is datetime:
        try:
            return datetime.fromisoformat(raw_value)
        except:
            pass
    if raw_value.isdigit():
        return int(raw_value)
    try:
        return float(raw_value)
    except:
        pass
    return raw_value


def resolve_relation_path(model: Type[SQLModel], path: List[str]):
    """
    Resolve uma cadeia como ["localidade", "nome"].
    Retorna: (último_modelo, coluna_sqlalchemy, lista_de_jinhas)
    """
    current_model = model
    joins = []
    for i, attr in enumerate(path):
        mapper = current_model.__mapper__

        if attr in mapper.relationships:
            rel: RelationshipProperty = mapper.relationships[attr]
            joins.append(rel)
            current_model = rel.mapper.class_
        else:
            column = getattr(current_model, attr, None)
            if column is None:
                return None, None, None
            return current_model, column, joins
    return None, None, None


def build_operator(column, op: str, raw_value: str):
    if op == "between":
        parts = raw_value.split(",")
        if len(parts) != 2:
            return None
        start = parse_value_for_column(column, parts[0])
        end = parse_value_for_column(column, parts[1])
        return column.between(start, end)

    if op == "in":
        raw_list = raw_value.split(",")
        value = parse_value_for_column(column, raw_list)
    else:
        value = parse_value_for_column(column, raw_value)

    operators = {
        "eq": lambda c, v: c == v,
        "ne": lambda c, v: c != v,
        "gt": lambda c, v: c > v,
        "gte": lambda c, v: c >= v,
        "lt": lambda c, v: c < v,
        "lte": lambda c, v: c <= v,
        "cts": lambda c, v: c.contains(v),
        "sts": lambda c, v: c.startswith(v),
        "eds": lambda c, v: c.endswith(v),
        "in": lambda c, v: c.in_(v),
    }

    if op not in operators:
        return None

    return operators[op](column, value)


def create_crud_router(
    *,
    model: Type[SQLModel],
    prefix: str,
    session_dep,
    allowed_filters: Optional[List[str]] = None,
    auth,
):
    router = APIRouter(prefix=prefix, tags=[model.__name__])

    PaginatedResponseModel = create_model(
        f"Paginated{model.__name__}Response",
        page=(int, ...),
        page_size=(int, ...),
        total=(int, ...),
        items=(List[model], ...),
    )

    @router.get("-raw/", response_model=List[model])
    def list_items(
        request: Request,
        session: Session = Depends(session_dep),
        limit: int = Query(999, ge=1),
        offset: int = Query(0, ge=0),
        order_by: Optional[str] = "id",
        order: str = Query("asc", pattern="^(asc|desc)$"),
        #current_user=Depends(auth.get_current_active_user_dependency()),
    ):
        query = select(model)
        joins_made = set()

        params = dict(request.query_params)
        reserved = {"limit", "offset", "order_by", "order"}
        filters = {k: v for k, v in params.items() if k not in reserved}

        for raw_key, value in filters.items():
            if "__" in raw_key:
                field_path, op = raw_key.split("__", 1)
            else:
                field_path, op = raw_key, "eq"

            path = field_path.split(".")
            base_field = path[0]

            if allowed_filters and base_field not in allowed_filters:
                continue

            final_model, column, joins = resolve_relation_path(model, path)
            if column is None:
                continue

            for rel in joins:
                if rel not in joins_made:
                    query = query.join(rel.mapper.class_)
                    joins_made.add(rel)

            condition = build_operator(column, op, value)
            if condition is not None:
                query = query.where(condition)

        if order_by and hasattr(model, order_by):
            col = getattr(model, order_by)
            if order == "desc":
                col = col.desc()
            query = query.order_by(col)

        query = query.limit(limit).offset(offset)

        return session.exec(query).all()

    @router.get("/", response_model=PaginatedResponseModel)
    def list_items(
        request: Request,
        session: Session = Depends(session_dep),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        order_by: Optional[str] = "id",
        order: str = Query("asc", pattern="^(asc|desc)$"),
        #current_user=Depends(auth.get_current_active_user_dependency()),
    ):
        offset = (page - 1) * page_size

        query = select(model)
        joins_made = set()

        params = dict(request.query_params)
        reserved = {"page", "page_size", "order_by", "order"}
        filters = {k: v for k, v in params.items() if k not in reserved}

        for raw_key, value in filters.items():
            if "__" in raw_key:
                field_path, op = raw_key.split("__", 1)
            else:
                field_path, op = raw_key, "eq"

            path = field_path.split(".")
            base_field = path[0]

            if allowed_filters and base_field not in allowed_filters:
                continue

            final_model, column, joins = resolve_relation_path(model, path)
            if column is None:
                continue

            for rel in joins:
                if rel not in joins_made:
                    query = query.join(rel.mapper.class_)
                    joins_made.add(rel)

            condition = build_operator(column, op, value)
            if condition is not None:
                query = query.where(condition)

        if order_by and hasattr(model, order_by):
            col = getattr(model, order_by)
            if order == "desc":
                col = col.desc()
            query = query.order_by(col)

        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        items = session.exec(query.limit(page_size).offset(offset)).all()

        return PaginatedResponseModel(
            page=page,
            page_size=page_size,
            total=total,
            items=items,
        )

    @router.post("/", response_model=model)
    def create_item(
        data: model,
        session: Session = Depends(session_dep),
        #current_user = Depends(auth.get_current_active_user_dependency()), # type: ignore
    ):
        obj = model(**data.model_dump(exclude_unset=True))
        session.add(obj)
        try:
            session.commit()
            session.refresh(obj)
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Violação de integridade.")
        return obj

    @router.get("/{item_id}", response_model=model)
    def get_item(
        item_id: int,
        session: Session = Depends(session_dep),
        #current_user = Depends(auth.get_current_active_user_dependency()), # type: ignore
    ):
        obj = session.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return obj

    @router.put("/{item_id}", response_model=model)
    def update_item(
        item_id: int,
        data: model,
        session: Session = Depends(session_dep),
        #current_user = Depends(auth.get_current_active_user_dependency()), # type: ignore
    ):
        obj = session.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(obj, k, v)
        try:
            session.add(obj)
            session.commit()
            session.refresh(obj)
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=400, detail="Violação de integridade.")
        return obj

    @router.delete("/{item_id}")
    def delete_item(
        item_id: int,
        session: Session = Depends(session_dep),
        #current_user = Depends(auth.get_current_active_user_dependency()), # type: ignore
    ):
        obj = session.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        session.delete(obj)
        session.commit()
        return {"status": "ok"}

    return router
