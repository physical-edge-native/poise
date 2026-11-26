"""Baselines without a body: linear readouts on windows of past inputs.

See docs/design/2026-11-27-delayed-input-baseline.md. All baselines use the same readout, split and
targets as the body (``poise.tasks``); window lengths are chosen on the training part only.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement
from typing import Callable, Sequence

import numpy as np

from . import readout, tasks

D_FULL = 86  # D87: u(t) .. u(t-86), as many features as the body has springs
D_CHOICES = (0, 1, 2, 4, 8, 16, 32, 64, 86)  # D-val: K in u(t) .. u(t-K)
P_CHOICES = (1, 2, 3, 4, 5, 6)  # P3: window length L
P_DEGREE = 3
N_FIT = 1500  # validation: fit on the first N_FIT training samples, score on the rest


def delay_line(u: np.ndarray, k_max: int) -> np.ndarray:
    """Features u(t), u(t-1), ..., u(t-k_max); values before the start are 0."""
    u = np.asarray(u, dtype=np.float64)
    cols = [u] + [np.concatenate([np.zeros(d), u[:-d]]) for d in range(1, k_max + 1)]
    return np.stack(cols, axis=1)


def polynomial_window(u: np.ndarray, length: int, degree: int = P_DEGREE) -> np.ndarray:
    """All monomials of degree 1..degree of u(t), ..., u(t-length+1), with repetition."""
    window = delay_line(u, length - 1)
    cols = []
    for d in range(1, degree + 1):
        for idx in combinations_with_replacement(range(length), d):
            col = window[:, idx[0]]
            for j in idx[1:]:
                col = np.multiply(col, window[:, j])
            cols.append(col)
    return np.stack(cols, axis=1)


def n_polynomial_features(length: int, degree: int = P_DEGREE) -> int:
    return sum(len(list(combinations_with_replacement(range(length), d))) for d in range(1, degree + 1))


def _fit_score(f_fit, y_fit, f_eval, y_eval, score: Callable[[np.ndarray, np.ndarray], float]) -> float:
    model = readout.fit(f_fit, y_fit)
    return score(y_eval, model.predict(f_eval))


@dataclass(frozen=True)
class Choice:
    param: int
    test_score: float


def choose_and_test(
    make_features: Callable[[int], np.ndarray],
    params: Sequence[int],
    target: np.ndarray,
    score: Callable[[np.ndarray, np.ndarray], float],
    higher_is_better: bool,
) -> Choice:
    """Pick the parameter by validation inside the training part, refit on it, score on the test part.

    On an exact tie the earlier (shorter) parameter wins.
    """
    y_train, y_test = tasks._split(target)
    best_param, best_val = None, None
    for p in params:
        f_train, _ = tasks._split(make_features(p))
        val = _fit_score(f_train[:N_FIT], y_train[:N_FIT], f_train[N_FIT:], y_train[N_FIT:], score)
        better = best_val is None or (val > best_val if higher_is_better else val < best_val)
        if better:
            best_param, best_val = p, val
    f_train, f_test = tasks._split(make_features(best_param))
    return Choice(best_param, _fit_score(f_train, y_train, f_test, y_test, score))


def _delayed_target(u: np.ndarray, k: int) -> np.ndarray:
    return np.concatenate([np.zeros(k), u[:-k]])


@dataclass(frozen=True)
class SelectedMemoryCapacity:
    total: float
    per_delay: tuple[float, ...]
    chosen: tuple[int, ...]  # chosen parameter per delay


def memory_capacity_selected(u, make_features, params, max_delay: int = tasks.MAX_DELAY) -> SelectedMemoryCapacity:
    cache = {p: make_features(p) for p in params}
    scores, chosen = [], []
    for k in range(1, max_delay + 1):
        c = choose_and_test(cache.__getitem__, params, _delayed_target(u, k), tasks.squared_correlation, True)
        scores.append(c.test_score)
        chosen.append(c.param)
    return SelectedMemoryCapacity(float(sum(scores)), tuple(scores), tuple(chosen))


def narma2_selected(u, make_features, params) -> Choice:
    cache = {p: make_features(p) for p in params}
    return choose_and_test(cache.__getitem__, params, tasks.narma2_target(u), tasks.nmse, False)


@dataclass(frozen=True)
class BaselineResults:
    mc_d87: tasks.MemoryCapacity
    mc_dval: SelectedMemoryCapacity
    mc_p3: SelectedMemoryCapacity
    narma2_d87: float
    narma2_dval: Choice
    narma2_p3: Choice


def run_all() -> BaselineResults:
    u_mc = tasks.uniform_inputs(tasks.MC_INPUT_SEED, -1.0, 1.0)
    u_na = tasks.uniform_inputs(tasks.NARMA2_INPUT_SEED, 0.0, 0.5)
    assert tasks.WASHOUT > D_FULL
    return BaselineResults(
        mc_d87=tasks.memory_capacity(delay_line(u_mc, D_FULL), u_mc),
        mc_dval=memory_capacity_selected(u_mc, lambda k: delay_line(u_mc, k), D_CHOICES),
        mc_p3=memory_capacity_selected(u_mc, lambda n: polynomial_window(u_mc, n), P_CHOICES),
        narma2_d87=tasks.narma2_nmse(delay_line(u_na, D_FULL), u_na),
        narma2_dval=narma2_selected(u_na, lambda k: delay_line(u_na, k), D_CHOICES),
        narma2_p3=narma2_selected(u_na, lambda n: polynomial_window(u_na, n), P_CHOICES),
    )
