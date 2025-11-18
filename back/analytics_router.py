from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from models import RespostaPesquisa, Area, Cargo, TempoEmpresa, Participante
from analytics_stats import stats_basic, percentiles, iqr
from main import get_session
from transformers import pipeline
import re
from collections import Counter



router = APIRouter(prefix="/analytics", tags=["analytics"])


sentiment_model = pipeline(
    "sentiment-analysis",
    model="lipaoMai/bert-sentiment-model-portuguese"
)


SCORE_FIELDS = [
    "interesse_cargo_score",
    "contribuicao_score",
    "aprendizado_desenvolvimento_score",
    "feedback_score",
    "interacao_gestor_score",
    "clareza_carreira_score",
    "expectativa_permanencia_score",
    "enps_score",
]


def fetch_respostas(session: Session, extra_filters: Dict[str, Optional[int]] = None):
    q = select(RespostaPesquisa)
    if extra_filters:
        for k, v in extra_filters.items():
            if v is None:
                continue
            col = getattr(RespostaPesquisa, k, None)
            if col is not None:
                q = q.where(col == v)
    rows = session.exec(q).all()
    return rows


def collect_scores_from_respostas(respostas: List[RespostaPesquisa], field: str) -> List[float]:
    vals = []
    for r in respostas:
        v = getattr(r, field, None)
        if v is None:
            continue
        try:
            vals.append(float(v))
        except Exception:
            continue
    return vals


# -----------------------
# COMPANY LEVEL ENDPOINTS
# -----------------------
@router.get("/company/employees_per_area")
def company_employees_per_area(
    session: Session = Depends(get_session),
    cargo_id: Optional[int] = Query(None),
    area_id: Optional[int] = Query(None),
    localidade_id: Optional[int] = Query(None),
    geracao_id: Optional[int] = Query(None),
    tempo_empresa_id: Optional[int] = Query(None)
):
    area_q = select(Area)
    if area_id:
        area_q = area_q.where(Area.id == area_id)
    areas = session.exec(area_q).all()
    result = []
    for a in areas:
        q = select(func.count(RespostaPesquisa.id)).where(RespostaPesquisa.area_id == a.id)
        if cargo_id:
            q = q.where(RespostaPesquisa.cargo_id == cargo_id)
        if localidade_id:
            q = q.where(RespostaPesquisa.localidade_id == localidade_id)
        if geracao_id:
            q = q.where(RespostaPesquisa.geracao_id == geracao_id)
        if tempo_empresa_id:
            q = q.where(RespostaPesquisa.tempo_empresa_id == tempo_empresa_id)
        cnt = session.exec(q).one()
        result.append({"area_id": a.id, "area_nome": a.nome, "count": cnt})
    return result


@router.get("/company/average_feedback")
def company_average_feedback(
    session: Session = Depends(get_session),
    cargo_id: Optional[int] = Query(None),
    area_id: Optional[int] = Query(None),
    localidade_id: Optional[int] = Query(None),
    geracao_id: Optional[int] = Query(None),
    tempo_empresa_id: Optional[int] = Query(None)
):
    filters = {
        "cargo_id": cargo_id,
        "area_id": area_id,
        "localidade_id": localidade_id,
        "geracao_id": geracao_id,
        "tempo_empresa_id": tempo_empresa_id,
    }
    respostas = fetch_respostas(session, filters)
    out: Dict[str, Any] = {}
    for field in SCORE_FIELDS:
        vals = collect_scores_from_respostas(respostas, field)
        out[field] = stats_basic(vals)
    return out


@router.get("/company/enps_distribution")
def company_enps_distribution(
    session: Session = Depends(get_session),
    cargo_id: Optional[int] = Query(None),
    area_id: Optional[int] = Query(None),
    localidade_id: Optional[int] = Query(None),
    geracao_id: Optional[int] = Query(None),
    tempo_empresa_id: Optional[int] = Query(None)
):
    filters = {
        "cargo_id": cargo_id,
        "area_id": area_id,
        "localidade_id": localidade_id,
        "geracao_id": geracao_id,
        "tempo_empresa_id": tempo_empresa_id,
    }
    respostas = fetch_respostas(session, filters)
    enps_vals = collect_scores_from_respostas(respostas, "enps_score")
    hist: Dict[int, int] = {}
    for v in enps_vals:
        key = int(v)
        hist[key] = hist.get(key, 0) + 1
    total = len(enps_vals)
    detratores = sum(1 for v in enps_vals if v <= 6)
    neutros = sum(1 for v in enps_vals if 7 <= v <= 8)
    promotores = sum(1 for v in enps_vals if v >= 9)

    def pct(x):
        return round((x / total) * 100, 2) if total else 0.0

    return {
        "histogram_by_score": hist,
        "total": total,
        "detratores": {"count": detratores, "pct": pct(detratores)},
        "neutros": {"count": neutros, "pct": pct(neutros)},
        "promotores": {"count": promotores, "pct": pct(promotores)},
    }


@router.get("/company/tenure_distribution")
def company_tenure_distribution(
    session: Session = Depends(get_session),
    cargo_id: Optional[int] = Query(None),
    area_id: Optional[int] = Query(None),
    localidade_id: Optional[int] = Query(None),
    geracao_id: Optional[int] = Query(None),
    tempo_empresa_id: Optional[int] = Query(None)
):
    tempo_q = select(TempoEmpresa)
    if tempo_empresa_id:
        tempo_q = tempo_q.where(TempoEmpresa.id == tempo_empresa_id)
    tempos = session.exec(tempo_q).all()
    out = []
    for t in tempos:
        q = select(func.count(RespostaPesquisa.id)).where(RespostaPesquisa.tempo_empresa_id == t.id)
        if cargo_id:
            q = q.where(RespostaPesquisa.cargo_id == cargo_id)
        if area_id:
            q = q.where(RespostaPesquisa.area_id == area_id)
        if localidade_id:
            q = q.where(RespostaPesquisa.localidade_id == localidade_id)
        if geracao_id:
            q = q.where(RespostaPesquisa.geracao_id == geracao_id)
        cnt = session.exec(q).one()
        out.append({"tempo_empresa_id": t.id, "descricao": t.descricao, "count": cnt})
    return out



COMMENT_TOPIC_MAP = {
        "interesse_cargo": ("interesse_cargo_score", "interesse_cargo_comment"),
        "contribuicao": ("contribuicao_score", "contribuicao_comment"),
        "aprendizado": ("aprendizado_desenvolvimento_score", "aprendizado_desenvolvimento_comment"),
        "feedback": ("feedback_score", "feedback_comment"),
        "interacao_gestor": ("interacao_gestor_score", "interacao_gestor_comment"),
        "clareza_carreira": ("clareza_carreira_score", "clareza_carreira_comment"),
        "expectativa_permanencia": ("expectativa_permanencia_score", "expectativa_permanencia_comment"),
        "enps": ("enps_score", "enps_comment"), # O 'aberta_enps_comment' é o alias no model
}
VALID_COMMENT_TOPICS = list(COMMENT_TOPIC_MAP.keys())

@router.get("/company/comments")
def get_enps_comments(
    session: Session = Depends(get_session),
    score_min: Optional[int] = Query(None),
    score_max: Optional[int] = Query(None),
    cargo_id: Optional[int] = Query(None),
    area_id: Optional[int] = Query(None),
    localidade_id: Optional[int] = Query(None),
    geracao_id: Optional[int] = Query(None),
    tempo_empresa_id: Optional[int] = Query(None),
    topic: str = Query(..., enum=VALID_COMMENT_TOPICS)
):
    try:
        score_col_name, comment_col_name = COMMENT_TOPIC_MAP[topic]
    except KeyError:
        raise HTTPException(status_code=400, detail="Tópico inválido")
    score_col = getattr(RespostaPesquisa, score_col_name)
    comment_col = getattr(RespostaPesquisa, comment_col_name)
    q = select(
        comment_col, 
        score_col, 
        RespostaPesquisa.participante_id,
        RespostaPesquisa.area_id
    )
    if cargo_id:
        q = q.where(RespostaPesquisa.cargo_id == cargo_id)
    if area_id:
        q = q.where(RespostaPesquisa.area_id == area_id)
    if localidade_id:
        q = q.where(RespostaPesquisa.localidade_id == localidade_id)
    if geracao_id:
        q = q.where(RespostaPesquisa.geracao_id == geracao_id)
    if tempo_empresa_id:
        q = q.where(RespostaPesquisa.tempo_empresa_id == tempo_empresa_id)
    if score_min is not None:
        q = q.where(score_col >= score_min)
    if score_max is not None:
        q = q.where(score_col <= score_max)
    q = q.where(comment_col != None).where(comment_col != "-")
    results = session.exec(q).all()
    formatted_comments = [
        {
            "comment": row[0],
            "score": row[1],
            "participante_id": row[2],
            "area_id": row[3]
        }
        for row in results
    ]
    return {
        "topic": topic,
        "filters": {
            "score_min": score_min,
            "score_max": score_max,
            "area_id": area_id,
            "cargo_id": cargo_id,
            "localidade_id": localidade_id,
            "geracao_id": geracao_id,
            "tempo_empresa_id": tempo_empresa_id
        },
        "count": len(formatted_comments),
        "comments": formatted_comments
    }



@router.get("/company/sentiments")
def get_sentiment_analysis(
    session: Session = Depends(get_session),
    cargo_id: Optional[int] = Query(None),
    area_id: Optional[int] = Query(None),
    localidade_id: Optional[int] = Query(None),
    geracao_id: Optional[int] = Query(None),
    tempo_empresa_id: Optional[int] = Query(None),
    topic: str = Query(..., enum=VALID_COMMENT_TOPICS)
):
    try:
        score_col_name, comment_col_name = COMMENT_TOPIC_MAP[topic]
    except KeyError:
        raise HTTPException(status_code=400, detail="Tópico inválido")

    comment_col = getattr(RespostaPesquisa, comment_col_name)

    q = select(
        comment_col,
        RespostaPesquisa.participante_id,
        RespostaPesquisa.area_id,
        RespostaPesquisa.cargo_id
    )

    if cargo_id:
        q = q.where(RespostaPesquisa.cargo_id == cargo_id)
    if area_id:
        q = q.where(RespostaPesquisa.area_id == area_id)
    if localidade_id:
        q = q.where(RespostaPesquisa.localidade_id == localidade_id)
    if geracao_id:
        q = q.where(RespostaPesquisa.geracao_id == geracao_id)
    if tempo_empresa_id:
        q = q.where(RespostaPesquisa.tempo_empresa_id == tempo_empresa_id)

    q = q.where(comment_col != None).where(comment_col != "-")

    rows = session.exec(q).all()

    if not rows:
        return {
            "topic": topic,
            "count": 0,
            "message": "Nenhum comentário encontrado com esses filtros."
        }

    comments = [row[0] for row in rows]
    sentiments = sentiment_model(comments)

    enriched = []
    for row, s in zip(rows, sentiments):
        enriched.append({
            "comment": row[0],
            "participante_id": row[1],
            "area_id": row[2],
            "cargo_id": row[3],
            "sentiment": {
                "label": s["label"].lower(),
                "score": float(s["score"])
            }
        })

    total = len(enriched)
    pos = sum(1 for r in enriched if r["sentiment"]["label"] == "positive")
    neg = sum(1 for r in enriched if r["sentiment"]["label"] == "negative")
    neu = sum(1 for r in enriched if r["sentiment"]["label"] == "neutral")

    ranking_area = {}
    for r in enriched:
        area = r["area_id"]
        ranking_area.setdefault(area, {"positive": 0, "negative": 0, "neutral": 0})
        ranking_area[area][r["sentiment"]["label"]] += 1

    ranking_cargo = {}
    for r in enriched:
        cargo = r["cargo_id"]
        ranking_cargo.setdefault(cargo, {"positive": 0, "negative": 0, "neutral": 0})
        ranking_cargo[cargo][r["sentiment"]["label"]] += 1

    words_pos = []
    words_neg = []

    def tokenize(txt):
        return re.findall(r"\b\w{4,}\b", txt.lower())

    for r in enriched:
        tokens = tokenize(r["comment"])
        if r["sentiment"]["label"] == "positive":
            words_pos.extend(tokens)
        elif r["sentiment"]["label"] == "negative":
            words_neg.extend(tokens)

    top_positive_terms = [w for w, _ in Counter(words_pos).most_common(15)]
    top_negative_terms = [w for w, _ in Counter(words_neg).most_common(15)]

    return {
        "topic": topic,
        "filters": {
            "area_id": area_id,
            "cargo_id": cargo_id,
            "localidade_id": localidade_id,
            "geracao_id": geracao_id,
            "tempo_empresa_id": tempo_empresa_id
        },
        "count": total,
        "sentiment_summary": {
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "positive_pct": pos / total,
            "negative_pct": neg / total,
            "neutral_pct": neu / total,
        },
        "ranking": {
            "by_area": ranking_area,
            "by_cargo": ranking_cargo
        },
        "themes": {
            "top_positive_terms": top_positive_terms,
            "top_negative_terms": top_negative_terms
        },
        "comments": enriched
    }

# -----------------------
# AREA LEVEL ENDPOINTS
# -----------------------
@router.get("/area/{area_id}/scores")
def area_scores(area_id: int, session: Session = Depends(get_session)):
    respostas = fetch_respostas(session, {"area_id": area_id})
    if not respostas:
        raise HTTPException(status_code=404, detail="Área sem respostas ou não encontrada")

    out: Dict[str, Any] = {}
    for field in SCORE_FIELDS:
        vals = collect_scores_from_respostas(respostas, field)
        out[field] = stats_basic(vals)
    return {"area_id": area_id, "scores": out}


@router.get("/area/{area_id}/enps")
def area_enps(area_id: int, session: Session = Depends(get_session)):
    respostas = fetch_respostas(session, {"area_id": area_id})
    if not respostas:
        raise HTTPException(status_code=404, detail="Área sem respostas ou não encontrada")
    enps_vals = collect_scores_from_respostas(respostas, "enps_score")
    total = len(enps_vals)
    detratores = sum(1 for v in enps_vals if v <= 6)
    neutros = sum(1 for v in enps_vals if 7 <= v <= 8)
    promotores = sum(1 for v in enps_vals if v >= 9)
    def pct(x): return round((x / total) * 100, 2) if total else 0.0
    return {
        "total": total,
        "detratores": {"count": detratores, "pct": pct(detratores)},
        "neutros": {"count": neutros, "pct": pct(neutros)},
        "promotores": {"count": promotores, "pct": pct(promotores)},
    }


@router.get("/areas/summary")
def areas_summary(session: Session = Depends(get_session)):
    areas = session.exec(select(Area)).all()
    out = []
    for a in areas:
        respostas = fetch_respostas(session, {"area_id": a.id})
        total = len(respostas)
        averages = {}
        for f in SCORE_FIELDS:
            vals = collect_scores_from_respostas(respostas, f)
            averages[f] = stats_basic(vals).get("mean")
        out.append({"area_id": a.id, "area_nome": a.nome, "total_respostas": total, "averages": averages})
    return out


# -----------------------
# EMPLOYEE LEVEL ENDPOINTS
# -----------------------
@router.get("/employee/{participante_id}/profile")
def employee_profile(participante_id: int, session: Session = Depends(get_session)):
    participante = session.get(Participante, participante_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    q_latest = (
        select(RespostaPesquisa)
        .where(RespostaPesquisa.participante_id == participante_id)
        .order_by(RespostaPesquisa.data_resposta.desc())
    )
    latest_response = session.exec(q_latest).first()
    respostas = session.exec(select(RespostaPesquisa).where(RespostaPesquisa.participante_id == participante_id)).all()
    scores = {}
    for f in SCORE_FIELDS:
        vals = collect_scores_from_respostas(respostas, f)
        scores[f] = stats_basic(vals)
    demographics = {}
    if latest_response:
        area = session.get(Area, latest_response.area_id)
        cargo = session.get(Cargo, latest_response.cargo_id)
        tempo = session.get(TempoEmpresa, latest_response.tempo_empresa_id)
        demographics = {
            "area_nome": area.nome if area else None,
            "cargo_nome": cargo.nome if cargo else None,
            "tempo_empresa_descricao": tempo.descricao if tempo else None,
            "data_ultima_resposta": latest_response.data_resposta
        }
    return {
        "participante": {"id": participante.id, "nome": participante.nome, "email_corporativo": participante.email_corporativo},
        "responses_count": len(respostas),
        "demographics": demographics,
        "scores_stats": scores
    }


@router.get("/employee/{participante_id}/comparison")
def employee_comparison(participante_id: int, session: Session = Depends(get_session)):
    participante = session.get(Participante, participante_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    respostas_emp = session.exec(select(RespostaPesquisa).where(RespostaPesquisa.participante_id == participante_id)).all()
    if not respostas_emp:
        raise HTTPException(status_code=404, detail="Participante sem respostas")

    emp_avgs = {}
    for f in SCORE_FIELDS:
        vals = collect_scores_from_respostas(respostas_emp, f)
        emp_avgs[f] = stats_basic(vals).get("mean")

    latest = sorted(respostas_emp, key=lambda r: r.data_resposta or r.created_at, reverse=True)[0]
    area_id = latest.area_id

    respostas_all = fetch_respostas(session, {})
    company_avgs = {f: stats_basic(collect_scores_from_respostas(respostas_all, f)).get("mean") for f in SCORE_FIELDS}

    respostas_area = fetch_respostas(session, {"area_id": area_id})
    area_avgs = {f: stats_basic(collect_scores_from_respostas(respostas_area, f)).get("mean") for f in SCORE_FIELDS}

    return {
        "participante_id": participante_id,
        "employee_avgs": emp_avgs,
        "area_id": area_id,
        "area_avgs": area_avgs,
        "company_avgs": company_avgs,
    }
