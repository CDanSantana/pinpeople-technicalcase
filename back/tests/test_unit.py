import pytest
from datetime import date, datetime
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from router_factore import (
    parse_value_for_column,
    build_operator,
    resolve_relation_path
)
from models import Area, Localidade
from sqlmodel import SQLModel, Field
from analytics_stats import (
    safe_mode,
    percentiles,
    iqr,
    coef_variacao,
    stats_basic
)


def test_parse_value_for_column_int():
    class MInt(SQLModel, table=True):
        x: int = Field(primary_key=True)

    col = MInt.x
    assert parse_value_for_column(col, "10") == 10


def test_parse_value_for_column_float():
    class MFloat(SQLModel, table=True):
        x: float = Field(primary_key=True)

    col = MFloat.x
    assert parse_value_for_column(col, "10.5") == 10.5


def test_parse_value_for_column_date():
    class MDate(SQLModel, table=True, extend_existing=True):
        x: date = Field(primary_key=True)

    col = MDate.x
    assert parse_value_for_column(col, "2024-01-02") == date(2024, 1, 2)


def test_parse_value_for_column_datetime():
    class MDateTime(SQLModel, table=True, extend_existing=True):
        x: datetime = Field(primary_key=True)

    col = MDateTime.x
    dt = parse_value_for_column(col, "2024-01-02T10:30:00")
    assert dt == datetime(2024, 1, 2, 10, 30, 0)


def test_build_operator_eq():
    class MEq(SQLModel, table=True, extend_existing=True):
        x: int = Field(primary_key=True)

    op = build_operator(MEq.x, "eq", "10")
    assert str(op) == str(MEq.x == 10)


def test_build_operator_between():
    class MBtn(SQLModel, table=True, extend_existing=True):
        x: int = Field(primary_key=True)

    op = build_operator(MBtn.x, "between", "5,10")
    assert str(op) == str(MBtn.x.between(5, 10))


def test_resolve_relation_path_valid():
    final_model, column, joins = resolve_relation_path(Area, ["respostas", "id"])
    assert column is not None
    assert len(joins) == 1


def test_resolve_relation_path_invalid():
    final_model, column, joins = resolve_relation_path(Area, ["foo", "bar"])
    assert column is None
    assert joins is None


def test_safe_mode_simple():
    assert safe_mode([1, 1, 2]) == 1


def test_safe_mode_no_mode():
    assert safe_mode([1, 2]) == 1


def test_percentiles_basic():
    vals = [10, 20, 30, 40]
    assert percentiles(vals, 0.0) == 10
    assert percentiles(vals, 1.0) == 40
    assert percentiles(vals, 0.5) == 25  # interpolado


def test_percentiles_empty():
    assert percentiles([], 0.5) is None


def test_percentiles_single_value():
    assert percentiles([10], 0.25) == 10


def test_iqr_basic():
    assert iqr([1, 2, 3, 4]) == pytest.approx(1.5)


def test_iqr_empty():
    assert iqr([]) is None


def test_coef_variacao_basic():
    vals = [10, 10, 10, 10]
    assert coef_variacao(vals) == 0


def test_coef_variacao_zero_mean():
    assert coef_variacao([0, 0, 0]) is None


def test_coef_variacao_empty():
    assert coef_variacao([]) is None


def test_stats_basic_complete():
    vals = [10, 20, 30]
    stats = stats_basic(vals)
    assert stats["count"] == 3
    assert stats["mean"] == 20
    assert stats["median"] == 20
    assert stats["mode"] in (10, 20, 30)  # qualquer um válido
    assert stats["min"] == 10
    assert stats["max"] == 30
    assert stats["p25"] == 15
    assert stats["p75"] == 25
    assert stats["iqr"] == 10
    assert stats["variance_pop"] == pytest.approx(66.666, rel=1e-2)
    assert stats["stddev_pop"] == pytest.approx(8.164, rel=1e-2)
    assert stats["coef_variacao"] == pytest.approx(0.408, rel=1e-2)


def test_stats_basic_empty():
    stats = stats_basic([])
    assert stats["count"] == 0
    assert stats["mean"] is None
    assert stats["iqr"] is None
    assert stats["coef_variacao"] is None
