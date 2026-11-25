"""Benchmark tasks for reservoirs: memory capacity and NARMA2.

Both tasks compare the network (features = spring lengths) with a baseline (features = the current
input alone), using the same readout, split and targets. See docs/design/2026-11-26-mass-spring-tasks.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import readout

WASHOUT = 200
N_TRAIN = 2000
N_TEST = 1000
MAX_DELAY = 30


def run_length() -> int:
    return WASHOUT + N_TRAIN + N_TEST


def uniform_inputs(seed: int, low: float, high: float, n: int | None = None) -> np.ndarray:
    n = run_length() if n is None else n
    r = np.random.default_rng(seed).random(n)
    return np.add(np.multiply(r, high - low), low)


def narma2_target(u: np.ndarray) -> np.ndarray:
    """Return y with y[t] = y(t+1) of NARMA2 driven by u[t], i.e. the value predicted at time t."""
    y_prev, y = 0.0, 0.0
    out = np.empty(len(u))
    for t, ut in enumerate(u):
        y_next = 0.4 * y + 0.4 * y * y_prev + 0.6 * ut * ut * ut + 0.1
        out[t] = y_next
        y_prev, y = y, y_next
    return out


def _split(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    train = a[WASHOUT : WASHOUT + N_TRAIN]
    test = a[WASHOUT + N_TRAIN : WASHOUT + N_TRAIN + N_TEST]
    return train, test


def squared_correlation(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denom = float(np.dot(a, a) * np.dot(b, b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) ** 2 / denom)


def nmse(target: np.ndarray, prediction: np.ndarray) -> float:
    return float(np.mean((prediction - target) ** 2) / np.var(target))


@dataclass(frozen=True)
class MemoryCapacity:
    total: float
    per_delay: tuple[float, ...]  # delays 1 .. MAX_DELAY


def memory_capacity(features: np.ndarray, u: np.ndarray, max_delay: int = MAX_DELAY) -> MemoryCapacity:
    """Sum over delays k of the squared correlation between u(t-k) and its reconstruction (test part).

    Requires WASHOUT >= max_delay so every target u(t-k) exists.
    """
    assert WASHOUT >= max_delay
    f_train, f_test = _split(features)
    scores = []
    for k in range(1, max_delay + 1):
        delayed = np.concatenate([np.zeros(k), u[:-k]])
        y_train, y_test = _split(delayed)
        model = readout.fit(f_train, y_train)
        scores.append(squared_correlation(y_test, model.predict(f_test)))
    return MemoryCapacity(float(sum(scores)), tuple(scores))


def narma2_nmse(features: np.ndarray, u: np.ndarray) -> float:
    y = narma2_target(u)
    f_train, f_test = _split(features)
    y_train, y_test = _split(y)
    model = readout.fit(f_train, y_train)
    return nmse(y_test, model.predict(f_test))


def input_only(u: np.ndarray) -> np.ndarray:
    """Baseline features: the current input alone."""
    return np.asarray(u, dtype=np.float64)[:, None]


@dataclass(frozen=True)
class Results:
    mc_body: MemoryCapacity
    mc_baseline: MemoryCapacity
    narma2_body: float
    narma2_baseline: float


NETWORK_SEED = 1
MC_INPUT_SEED = 2
NARMA2_INPUT_SEED = 3


def run_all(simulate: Callable[[np.ndarray], np.ndarray]) -> Results:
    """Run both tasks with a body (``simulate(u) -> features``) and with the baseline."""
    u_mc = uniform_inputs(MC_INPUT_SEED, -1.0, 1.0)
    u_na = uniform_inputs(NARMA2_INPUT_SEED, 0.0, 0.5)
    return Results(
        mc_body=memory_capacity(simulate(u_mc), u_mc),
        mc_baseline=memory_capacity(input_only(u_mc), u_mc),
        narma2_body=narma2_nmse(simulate(u_na), u_na),
        narma2_baseline=narma2_nmse(input_only(u_na), u_na),
    )
