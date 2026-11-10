from collections.abc import Sequence

import numpy as np
import pandas as pd


def filter_data(
    data: pd.DataFrame,
    kinds: Sequence[str],
    duration_range: tuple[float, float],
    waiting_range: tuple[float, float],
) -> pd.DataFrame:
    """Return rows matching the selected eruption types and measurement ranges."""
    mask = (
        data["kind"].isin(kinds)
        & data["duration"].between(*duration_range)
        & data["waiting"].between(*waiting_range)
    )
    return data.loc[mask].copy()


def fit_linear_regression(data: pd.DataFrame) -> tuple[float, float, float]:
    """Fit duration from waiting time and return slope, intercept, and R-squared."""
    waiting = data["waiting"].to_numpy(dtype=float)
    duration = data["duration"].to_numpy(dtype=float)
    if len(data) < 2 or np.unique(waiting).size < 2:
        raise ValueError("회귀 예측에는 서로 다른 대기 시간이 두 개 이상 필요합니다.")

    slope, intercept = np.polyfit(waiting, duration, 1)
    residual_sum_squares = float(np.square(duration - (slope * waiting + intercept)).sum())
    total_sum_squares = float(np.square(duration - duration.mean()).sum())
    if np.isclose(total_sum_squares, 0.0):
        r_squared = 1.0 if np.isclose(residual_sum_squares, 0.0) else 0.0
    else:
        r_squared = 1.0 - residual_sum_squares / total_sum_squares
    return float(slope), float(intercept), float(r_squared)
