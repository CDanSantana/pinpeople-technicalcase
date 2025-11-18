from typing import List, Optional, Dict, Any
import math
from statistics import mean, median, mode, StatisticsError, pvariance, pstdev


def safe_mode(values: List[float]) -> Optional[float]:
    try:
        return mode(values)
    except StatisticsError:
        return None


def percentiles(values: List[float], p: float) -> Optional[float]:
    if not values:
        return None
    vals = sorted(values)
    n = len(vals)
    if n == 1:
        return vals[0]
    # posição real
    rank = p * (n - 1)
    lo = int(math.floor(rank))
    hi = int(math.ceil(rank))
    if lo == hi:
        return vals[lo]
    frac = rank - lo
    return vals[lo] * (1 - frac) + vals[hi] * frac


def iqr(values: List[float]) -> Optional[float]:
    q1 = percentiles(values, 0.25)
    q3 = percentiles(values, 0.75)
    if q1 is None or q3 is None:
        return None
    return q3 - q1


def coef_variacao(values: List[float]) -> Optional[float]:
    if not values:
        return None
    m = mean(values)
    if m == 0:
        return None
    std = pstdev(values)  # desvio populacional
    return std / m


def stats_basic(values: List[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "mode": None,
            "min": None,
            "max": None,
            "p25": None,
            "p75": None,
            "iqr": None,
            "variance_pop": None,
            "stddev_pop": None,
            "coef_variacao": None,
        }

    vals = [float(v) for v in values]
    cnt = len(vals)
    m = mean(vals)
    md = median(vals)
    md_mode = safe_mode(vals)
    vmin = min(vals)
    vmax = max(vals)
    p25 = percentiles(vals, 0.25)
    p75 = percentiles(vals, 0.75)
    the_iqr = None
    if p25 is not None and p75 is not None:
        the_iqr = p75 - p25
    variance_pop = pvariance(vals)
    stddev_pop = pstdev(vals)
    cv = None
    if m != 0:
        cv = stddev_pop / m

    return {
        "count": cnt,
        "mean": m,
        "median": md,
        "mode": md_mode,
        "min": vmin,
        "max": vmax,
        "p25": p25,
        "p75": p75,
        "iqr": the_iqr,
        "variance_pop": variance_pop,
        "stddev_pop": stddev_pop,
        "coef_variacao": cv,
    }
