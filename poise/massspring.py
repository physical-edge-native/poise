"""A mass-spring network used as a physical reservoir.

Point masses in a plane are joined by nonlinear springs and dampers. Some masses are fixed; the
input is applied as a horizontal force to some of the free masses. The state that a readout sees is
the length of every spring.

Determinism across operating systems
------------------------------------
The trajectory is meant to be the same bit for bit on Linux, macOS and Windows. Everything that
feeds the trajectory therefore uses only IEEE 754 operations that are correctly rounded on every
platform: elementwise ``+``, ``-``, ``*``, ``/`` and ``sqrt`` on float64 arrays, one operation per
NumPy call (so no compiler can fuse a multiply and an add). In particular:

- random parameters come from ``Generator.random`` (an integer scaled by a power of two) and are
  mapped to a range with separate NumPy calls, not with ``Generator.uniform`` (whose C expression a
  compiler may contract into a fused multiply-add);
- no transcendental function (``exp``, ``log``, ``sin`` ...) and no ``**`` is used;
- forces on each mass are summed in a fixed order with elementwise additions, not with library
  reductions (``sum``, ``dot``, ``add.at``) whose order or vectorisation may differ between builds.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class NetworkParams:
    """Parameters of a random network. Ranges are (low, high), drawn uniformly."""

    n_masses: int = 30
    n_neighbours: int = 3  # each mass is joined to its nearest masses (pairs are not repeated)
    n_fixed: int = 4  # the masses with the smallest x are fixed
    input_fraction: float = 0.2  # fraction of the free masses that receive the input force
    k1: tuple[float, float] = (1.0, 100.0)  # linear spring coefficient
    k3: tuple[float, float] = (1.0, 200.0)  # cubic spring coefficient
    d1: tuple[float, float] = (1.0, 10.0)  # linear damping coefficient
    d3: tuple[float, float] = (1.0, 10.0)  # cubic damping coefficient
    input_weight: tuple[float, float] = (-1.0, 1.0)  # input force per unit input, per input mass
    mass: float = 1.0
    dt: float = 1e-3  # time step of the simulation, in seconds
    steps_per_sample: int = 20  # simulation steps per input sample (input held constant)


@dataclass(frozen=True)
class Network:
    params: NetworkParams
    pos0: np.ndarray  # (n, 2) rest positions
    spring_i: np.ndarray  # (s,) first mass of each spring
    spring_j: np.ndarray  # (s,) second mass of each spring
    rest_length: np.ndarray  # (s,)
    k1: np.ndarray
    k3: np.ndarray
    d1: np.ndarray
    d3: np.ndarray
    free: np.ndarray  # (n,) 1.0 for free masses, 0.0 for fixed ones
    input_weight: np.ndarray  # (n,) force per unit input; 0.0 for masses without input
    # incidence in a fixed order: for mass m, column c names a spring and the sign of its force on m
    inc_spring: np.ndarray  # (n, c) spring index, or s (a dummy spring with zero force)
    inc_sign: np.ndarray  # (n, c) +1.0, -1.0 or 0.0

    @property
    def n_springs(self) -> int:
        return int(self.spring_i.shape[0])


def _uniform(rng: np.random.Generator, bounds: tuple[float, float], size: int) -> np.ndarray:
    low, high = bounds
    r = rng.random(size)
    return np.add(np.multiply(r, high - low), low)


def make_network(seed: int, params: NetworkParams | None = None) -> Network:
    """Build a random network from a seed. The same seed gives the same network on every platform."""
    p = params or NetworkParams()
    rng = np.random.default_rng(seed)
    n = p.n_masses
    pos0 = rng.random((n, 2))

    # Pairwise squared distances, elementwise only.
    dx = np.subtract(pos0[:, None, 0], pos0[None, :, 0])
    dy = np.subtract(pos0[:, None, 1], pos0[None, :, 1])
    d2 = np.add(np.multiply(dx, dx), np.multiply(dy, dy))
    pairs: set[tuple[int, int]] = set()
    for a in range(n):
        order = np.argsort(d2[a], kind="stable")
        for b in order[1 : 1 + p.n_neighbours]:
            pairs.add((min(a, int(b)), max(a, int(b))))
    ordered = sorted(pairs)
    spring_i = np.array([a for a, _ in ordered], dtype=np.int64)
    spring_j = np.array([b for _, b in ordered], dtype=np.int64)
    s = len(ordered)
    rest_length = np.sqrt(d2[spring_i, spring_j])

    k1 = _uniform(rng, p.k1, s)
    k3 = _uniform(rng, p.k3, s)
    d1 = _uniform(rng, p.d1, s)
    d3 = _uniform(rng, p.d3, s)

    by_x = np.argsort(pos0[:, 0], kind="stable")
    free = np.ones(n)
    free[by_x[: p.n_fixed]] = 0.0
    free_idx = np.flatnonzero(free)
    n_input = max(1, int(round(p.input_fraction * len(free_idx))))
    chosen = np.sort(rng.permutation(free_idx)[:n_input])
    input_weight = np.zeros(n)
    input_weight[chosen] = _uniform(rng, p.input_weight, n_input)

    lists: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for k, (a, b) in enumerate(ordered):
        lists[a].append((k, 1.0))  # force on a: +f along the unit vector from a to b
        lists[b].append((k, -1.0))
    c = max(len(x) for x in lists)
    inc_spring = np.full((n, c), s, dtype=np.int64)
    inc_sign = np.zeros((n, c))
    for m, items in enumerate(lists):
        for col, (k, sign) in enumerate(items):
            inc_spring[m, col] = k
            inc_sign[m, col] = sign

    return Network(p, pos0, spring_i, spring_j, rest_length, k1, k3, d1, d3, free, input_weight,
                   inc_spring, inc_sign)


def simulate(net: Network, inputs: np.ndarray) -> np.ndarray:
    """Drive the network with one input value per sample and return spring lengths per sample.

    Each input value is held for ``steps_per_sample`` steps of semi-implicit Euler (velocity first,
    then position with the new velocity). The lengths are read at the end of each sample.
    Returns an array of shape (len(inputs), n_springs).
    """
    p = net.params
    dt = p.dt
    dt_over_m = dt / p.mass
    pos = net.pos0.copy()
    vel = np.zeros_like(pos)
    free2 = np.stack([net.free, net.free], axis=1)
    si, sj = net.spring_i, net.spring_j
    out = np.empty((len(inputs), net.n_springs))
    n_cols = net.inc_spring.shape[1]
    zero = np.zeros(1)

    for t, u in enumerate(np.asarray(inputs, dtype=np.float64)):
        fx_in = np.multiply(net.input_weight, u)
        for _ in range(p.steps_per_sample):
            ex = np.subtract(pos[sj, 0], pos[si, 0])
            ey = np.subtract(pos[sj, 1], pos[si, 1])
            length = np.sqrt(np.add(np.multiply(ex, ex), np.multiply(ey, ey)))
            ux = np.divide(ex, length)
            uy = np.divide(ey, length)
            stretch = np.subtract(length, net.rest_length)
            dvx = np.subtract(vel[sj, 0], vel[si, 0])
            dvy = np.subtract(vel[sj, 1], vel[si, 1])
            rate = np.add(np.multiply(dvx, ux), np.multiply(dvy, uy))  # rate of change of length
            s3 = np.multiply(np.multiply(stretch, stretch), stretch)
            r3 = np.multiply(np.multiply(rate, rate), rate)
            f = np.add(np.add(np.multiply(net.k1, stretch), np.multiply(net.k3, s3)),
                       np.add(np.multiply(net.d1, rate), np.multiply(net.d3, r3)))
            # tension f > 0 pulls mass i towards j and mass j towards i
            fsx = np.concatenate([np.multiply(f, ux), zero])
            fsy = np.concatenate([np.multiply(f, uy), zero])
            fx = fx_in.copy()
            fy = np.zeros_like(fx)
            for col in range(n_cols):
                k = net.inc_spring[:, col]
                sg = net.inc_sign[:, col]
                fx = np.add(fx, np.multiply(fsx[k], sg))
                fy = np.add(fy, np.multiply(fsy[k], sg))
            force = np.stack([fx, fy], axis=1)
            vel = np.multiply(np.add(vel, np.multiply(force, dt_over_m)), free2)
            pos = np.add(pos, np.multiply(vel, dt))
        ex = np.subtract(pos[sj, 0], pos[si, 0])
        ey = np.subtract(pos[sj, 1], pos[si, 1])
        out[t] = np.sqrt(np.add(np.multiply(ex, ex), np.multiply(ey, ey)))
    return out
