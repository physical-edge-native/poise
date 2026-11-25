"""Linear readout fitted by ridge regression."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

RIDGE_PER_SAMPLE = 1e-6  # penalty = RIDGE_PER_SAMPLE * number of training samples


@dataclass(frozen=True)
class Readout:
    mean: np.ndarray
    scale: np.ndarray
    weights: np.ndarray  # last entry is the constant term

    def predict(self, features: np.ndarray) -> np.ndarray:
        z = (features - self.mean) / self.scale
        return z @ self.weights[:-1] + self.weights[-1]


def fit(features: np.ndarray, target: np.ndarray, ridge_per_sample: float = RIDGE_PER_SAMPLE) -> Readout:
    """Fit a linear readout on standardised features plus a constant.

    Features with zero spread in the training part are kept but not scaled (their scale is 1).
    """
    features = np.asarray(features, dtype=np.float64)
    if features.ndim == 1:
        features = features[:, None]
    mean = features.mean(axis=0)
    scale = features.std(axis=0)
    scale = np.where(scale > 0.0, scale, 1.0)
    z = (features - mean) / scale
    x = np.hstack([z, np.ones((z.shape[0], 1))])
    lam = ridge_per_sample * x.shape[0]
    penalty = lam * np.eye(x.shape[1])
    penalty[-1, -1] = 0.0  # the constant term is not penalised
    w = np.linalg.solve(x.T @ x + penalty, x.T @ target)
    return Readout(mean, scale, w)
