import hashlib

import numpy as np
import pytest

from poise import massspring, tasks

# Reference values computed on Linux (x86-64). CI checks them on Linux, macOS and Windows.
# See docs/design/2026-11-26-mass-spring-tasks.md, section "Checks".
NETWORK_SHA256 = "d7d3bb541fdfc9dec273b4040b4378226625793319c28038f6ac991a9151a4fc"
TRAJECTORY_SHA256 = "b66f9186f3f08c2ade7ef5b80a47a1dd414ac342b5f69f8ee3fd7b1998eb87a3"
SCORES = {
    "mc_body": 5.736325785851501,
    "mc_baseline": 0.03194992468007571,
    "narma2_body": 0.347045119859554,
    "narma2_baseline": 0.4012218301465552,
}
SCORE_RTOL = 1e-7


@pytest.fixture(scope="module")
def net():
    return massspring.make_network(tasks.NETWORK_SEED)


def _sha(*arrays):
    return hashlib.sha256(np.concatenate([np.ascontiguousarray(a, dtype=np.float64).ravel() for a in arrays]).tobytes()).hexdigest()


def test_network_is_bit_exact(net):
    assert _sha(net.pos0, net.k1, net.k3, net.d1, net.d3, net.input_weight) == NETWORK_SHA256


def test_trajectory_is_bit_exact(net):
    u = tasks.uniform_inputs(tasks.MC_INPUT_SEED, -1.0, 1.0, n=200)
    assert _sha(massspring.simulate(net, u)) == TRAJECTORY_SHA256


def test_same_seed_same_result_twice(net):
    u = tasks.uniform_inputs(5, -1.0, 1.0, n=50)
    a = massspring.simulate(net, u)
    b = massspring.simulate(massspring.make_network(tasks.NETWORK_SEED), u)
    assert np.array_equal(a, b)


def test_network_has_no_floppy_modes(net):
    # Springs resist only changes of length. If the free masses could move without changing any
    # length (to first order), parts of the body would drift instead of keeping a memory of the input.
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
    lengths = massspring.simulate(net, np.zeros(1000), pos_init=pos)
    start = np.abs(lengths[0] - net.rest_length).max()
    end = np.abs(lengths[-1] - net.rest_length).max()
    assert end < 0.01 * start


def test_scores_match_reference(net):
    r = tasks.run_all(lambda u: massspring.simulate(net, u))
    got = {
        "mc_body": r.mc_body.total,
        "mc_baseline": r.mc_baseline.total,
        "narma2_body": r.narma2_body,
        "narma2_baseline": r.narma2_baseline,
    }
    for key, ref in SCORES.items():
        assert got[key] == pytest.approx(ref, rel=SCORE_RTOL), key
