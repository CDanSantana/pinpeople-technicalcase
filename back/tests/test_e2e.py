import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from main import app, engine, create_db_and_tables
from sqlmodel import Session
from models import Area, Cargo, TempoEmpresa, Participante, RespostaPesquisa


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}


def test_create_area(client):
    payload = {"nome": "Teste de Área"}
    r = client.post("/area/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["nome"] == "Teste de Área"
    assert data["id"] is not None


def test_get_area(client):
    r = client.get("/area/1")
    assert r.status_code == 200
    assert r.json()["nome"] != None


def test_update_area(client):
    r = client.put("/area/1", json={"nome": "administrativo"})
    assert r.status_code == 200
    assert r.json()["nome"] == "administrativo"


def test_list_area(client):
    r = client.get("/area/?page=1&page_size=10")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert isinstance(data["items"], list)


def test_filter_area_contains(client):
    r = client.get("/area/?nome__cts=adm")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert "adm" in items[0]["nome"]


def test_area_not_found(client):
    r = client.get("/area/9999")
    assert r.status_code == 404


def test_delete_area(client):
    r = client.delete("/area/6/")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    r2 = client.get("/area/6")
    assert r2.status_code == 404


def test_list_raw_area(client):
    r = client.get("/area-raw/?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


#------------------------------
# testes para analytics
#------------------------------

def test_company_employees_per_area(client):
    r = client.get("/analytics/company/employees_per_area")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert r.json()[0]["count"] >= 1


def test_company_average_feedback(client):
    r = client.get("/analytics/company/average_feedback")
    assert r.status_code == 200
    assert "feedback_score" in r.json()


def test_company_enps_distribution(client):
    r = client.get("/analytics/company/enps_distribution")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert "histogram_by_score" in data


def test_company_comments(client):
    r = client.get("/analytics/company/comments?topic=feedback")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    assert data["comments"][0]["comment"] == "A comunicação sobre desempenho é clara."


def test_area_scores(client):
    r = client.get("/analytics/area/1/scores")
    assert r.status_code == 200
    assert "scores" in r.json()


def test_area_enps(client):
    r = client.get("/analytics/area/1/enps")
    assert r.status_code == 200
    assert "total" in r.json()


def test_employee_profile(client):
    r = client.get("/analytics/employee/1/profile")
    assert r.status_code == 200
    data = r.json()
    assert data["participante"]["id"] == 1
    assert data["responses_count"] >= 1


def test_employee_comparison(client):
    r = client.get("/analytics/employee/1/comparison")
    assert r.status_code == 200
    data = r.json()
    assert "employee_avgs" in data
    assert "company_avgs" in data
    assert "area_avgs" in data
