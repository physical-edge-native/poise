"""Tests of the network with the settings of Hauser et al. (2011).

See docs/design/2026-11-27-hauser-network.md, section "Checks".
"""

import hashlib

import numpy as np
import pytest

from poise import massspring, tasks

# Reference values computed on Linux (x86-64). CI checks them on Linux, macOS and Windows.
NETWORK_SHA256 = "8f60b053e35c3f4f4af705c744b4af95eb28ca1d5c53a140221da2acd006d28f"
TRAJECTORY_SHA256 = "579f45c661ba467c863db71fc7688e61e760f22b1f174ea9e9a9152074d8ee99"
SCORES = {
    "mc_body": 3.228324915875822,
    "narma2_body": 0.3957055297466249,
}
SCORE_RTOL = 1e-7


@pytest.fixture(scope="module")
def net():
    return massspring.make_hauser_network(tasks.NETWORK_SEED)


def _sha(*arrays):
    return hashlib.sha256(np.concatenate([np.ascontiguousarray(a, dtype=np.float64).ravel() for a in arrays]).tobytes()).hexdigest()


def _int_points(pos):
    return [(int(x * 2**53), int(y * 2**53)) for x, y in pos]


def _orient(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def _hull_size(pts):
    """Number of points on the convex hull (exact; collinear points on an edge are not counted)."""
    pts = sorted(pts)
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and _orient(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and _orient(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return len(lower) + len(upper) - 2


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_triangulation_counts(seed):
    pos = np.random.default_rng(seed).random((30, 2))
    n, h = 30, _hull_size(_int_points(pos))
    assert len(massspring.delaunay_triangles(pos)) == 2 * n - 2 - h
    assert len(massspring.delaunay_edges(pos)) == 3 * n - 3 - h


def test_springs_do_not_cross(net):
    pts = _int_points(net.pos0)
    edges = list(zip(net.spring_i.tolist(), net.spring_j.tolist()))
    for x, (a, b) in enumerate(edges):
        for c, d in edges[x + 1 :]:
            if len({a, b, c, d}) < 4:
                continue
            o1 = _orient(pts[a], pts[b], pts[c])
            o2 = _orient(pts[a], pts[b], pts[d])
            o3 = _orient(pts[c], pts[d], pts[a])
            o4 = _orient(pts[c], pts[d], pts[b])
            assert not (o1 * o2 < 0 and o3 * o4 < 0), ((a, b), (c, d))


def test_triangulation_of_a_square_with_centre():
    # Four corners and a centre: the centre is joined to every corner, plus the four sides.
    pos = np.array([[0.0, 0.0], [0.5, 0.0], [0.0, 0.5], [0.5, 0.5], [0.25, 0.25]])
    assert massspring.delaunay_edges(pos) == [(0, 1), (0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]


def test_exp_basic_matches_numpy():
    x = np.linspace(0.0, 2.0 * np.log(10.0), 10001)
    assert np.max(np.abs(massspring.exp_basic(x) / np.exp(x) - 1.0)) < 1e-14


def test_settings(net):
    p = net.params
    assert p.n_masses == 30
    assert net.free.sum() == 28
    by_x = np.argsort(net.pos0[:, 0])
    assert net.free[by_x[0]] == 0.0 and net.free[by_x[-1]] == 0.0
    assert np.count_nonzero(net.input_weight) == 6
    for arr, (lo, hi) in [(net.k1, p.k1), (net.d1, p.d1), (net.k3, p.k3), (net.d3, p.d3)]:
        assert lo <= arr.min() and arr.max() <= hi


def test_log_uniform_draws_are_log_uniform():
    # Half of the draws of a log-uniform variable in [1, 100] fall below 10.
    v = massspring._log_uniform(np.random.default_rng(0), (1.0, 100.0), 20000)
    assert abs(np.mean(v < 10.0) - 0.5) < 0.02


def test_network_is_bit_exact(net):
    assert _sha(net.pos0, net.k1, net.k3, net.d1, net.d3, net.input_weight,
                net.spring_i.astype(np.float64), net.spring_j.astype(np.float64)) == NETWORK_SHA256


def test_trajectory_is_bit_exact(net):
    u = tasks.uniform_inputs(tasks.MC_INPUT_SEED, -1.0, 1.0, n=200)
    assert _sha(massspring.simulate(net, u)) == TRAJECTORY_SHA256


def test_network_has_no_floppy_modes(net):
    n = net.params.n_masses
    rigidity = np.zeros((net.n_springs, 2 * n))
    for k, (a, b) in enumerate(zip(net.spring_i, net.spring_j)):
        e = net.pos0[b] - net.pos0[a]
        e = e / np.linalg.norm(e)
        rigidity[k, 2 * a : 2 * a + 2] = -e
        rigidity[k, 2 * b : 2 * b + 2] = e
    cols = np.concatenate([[2 * m, 2 * m + 1] for m in np.flatnonzero(net.free)])
    sub = rigidity[:, cols]
    assert np.linalg.matrix_rank(sub) == sub.shape[1]


def test_rest_without_input_stays_exactly_at_rest(net):
    lengths = massspring.simulate(net, np.zeros(100))
    assert np.array_equal(lengths, np.broadcast_to(net.rest_length, lengths.shape))


def test_released_network_comes_to_rest(net):
    rng = np.random.default_rng(7)
    pos = net.pos0 + (rng.random(net.pos0.shape) - 0.5) * 0.02 * net.free[:, None]
    # Slower than the first network: springs with weak k1 and strong d1 relax with time constants of
    # about 15 s (measured), so the check runs for 60 s (3000 samples) and asks for 2 %.
    lengths = massspring.simulate(net, np.zeros(3000), pos_init=pos)
    start = np.abs(lengths[0] - net.rest_length).max()
    end = np.abs(lengths[-1] - net.rest_length).max()
    assert end < 0.02 * start


def test_scores_match_reference(net):
    r = tasks.run_all(lambda u: massspring.simulate(net, u))
    got = {"mc_body": r.mc_body.total, "narma2_body": r.narma2_body}
    for key, ref in SCORES.items():
        assert got[key] == pytest.approx(ref, rel=SCORE_RTOL), key
