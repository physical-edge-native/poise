"""Information processing capacity (Dambre et al. 2012, Sci. Rep. 2:514), evaluated on held-out data.

See docs/design/2026-11-27-information-processing-capacity.md for the setup and the reasons.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations

import numpy as np

from . import readout, tasks

WASHOUT = 200
N_TRAIN = 10_000
N_TEST = 10_000
INPUT_SEED = tasks.MC_INPUT_SEED
SURROGATE_SEED = 99
DEGREE_WINDOWS = {1: 60, 2: 20, 3: 10}  # delays 0 .. window-1 for functions of that degree
AMPLITUDES = (0.25, 0.5, 1.0, 2.0, 4.0)


def run_length() -> int:
    return WASHOUT + N_TRAIN + N_TEST


def legendre(order: int, x: np.ndarray) -> np.ndarray:
    if order == 1:
        return x
    if order == 2:
        return (3.0 * x * x - 1.0) / 2.0
    if order == 3:
        return (5.0 * x * x * x - 3.0 * x) / 2.0
    raise ValueError(order)


# A function is a tuple of (order, delay) pairs; its degree is the sum of the orders.
Function = tuple[tuple[int, int], ...]


def functions() -> list[Function]:
    out: list[Function] = []
    w1, w2, w3 = DEGREE_WINDOWS[1], DEGREE_WINDOWS[2], DEGREE_WINDOWS[3]
    out += [((1, k),) for k in range(w1)]
    out += [((2, k),) for k in range(w2)]
    out += [((1, i), (1, j)) for i, j in combinations(range(w2), 2)]
    out += [((3, k),) for k in range(w3)]
    out += [((2, i), (1, j)) for i, j in permutations(range(w3), 2)]
    out += [((1, i), (1, j), (1, l)) for i, j, l in combinations(range(w3), 3)]
    return out


def degree(f: Function) -> int:
    return sum(order for order, _ in f)


def _delayed(u: np.ndarray, k: int) -> np.ndarray:
    return u if k == 0 else np.concatenate([np.zeros(k), u[:-k]])


def targets(u: np.ndarray, funcs: list[Function]) -> np.ndarray:
    u = np.asarray(u, dtype=np.float64)
    cols = []
    for f in funcs:
        col = np.ones_like(u)
        for order, k in f:
            col = col * legendre(order, _delayed(u, k))
        cols.append(col)
    return np.stack(cols, axis=1)


def _split(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return a[WASHOUT : WASHOUT + N_TRAIN], a[WASHOUT + N_TRAIN : WASHOUT + N_TRAIN + N_TEST]


def _squared_correlations(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    y = y - y.mean(axis=0)
    p = p - p.mean(axis=0)
    num = (y * p).sum(axis=0) ** 2
    den = (y * y).sum(axis=0) * (p * p).sum(axis=0)
    return np.where(den > 0.0, num / np.where(den > 0.0, den, 1.0), 0.0)


def raw_capacities(features: np.ndarray, target_matrix: np.ndarray) -> np.ndarray:
    """Test-part squared correlation of each target column with its ridge reconstruction."""
    f_train, f_test = _split(np.asarray(features, dtype=np.float64))
    y_train, y_test = _split(target_matrix)
    model = readout.fit(f_train, y_train)
    return _squared_correlations(y_test, model.predict(f_test))


@dataclass(frozen=True)
class Capacity:
    epsilon: float
    per_function: np.ndarray  # thresholded capacities, in the order of functions()
    by_degree: dict[int, float]

    @property
    def total(self) -> float:
        return float(sum(self.by_degree.values()))


def capacity(features: np.ndarray, u: np.ndarray, u_surrogate: np.ndarray) -> Capacity:
    funcs = functions()
    real = raw_capacities(features, targets(u, funcs))
    surrogate = raw_capacities(features, targets(u_surrogate, funcs))
    eps = float(surrogate.max())
    kept = np.where(real > eps, real, 0.0)
    degrees = np.array([degree(f) for f in funcs])
    by_degree = {d: float(kept[degrees == d].sum()) for d in sorted(set(degrees.tolist()))}
    return Capacity(eps, kept, by_degree)


def inputs() -> tuple[np.ndarray, np.ndarray]:
    n = run_length()
    return (tasks.uniform_inputs(INPUT_SEED, -1.0, 1.0, n=n), tasks.uniform_inputs(SURROGATE_SEED, -1.0, 1.0, n=n))
