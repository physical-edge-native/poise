import numpy as np
import pytest

from poise import baselines, ipc, massspring, tasks

# Reference values computed on Linux (x86-64); CI checks them on Linux, macOS and Windows.
# See docs/design/2026-11-27-information-processing-capacity.md, section "Checks".
RTOL, ATOL = 1e-7, 1e-12
REF = {
    "input": (0.0007681620876990817, {1: 1.0009630394808076, 2: 0.0008158195302232899, 3: 0.0019585779257684055}),
    "d87": (0.0008347649291115696, {1: 59.9999999999996, 2: 0.0, 3: 0.0}),
    "p3": (0.000837964149790555, {1: 5.999999999929631, 2: 20.99999999999971, 3: 56.001996224535176}),
    "body": (0.0006481406932699486, {1: 9.175943162355116, 2: 2.0457702513773492, 3: 0.004343041657336484}),
}


def test_function_list():
    f = ipc.functions()
    assert len(f) == len(set(f)) == 490
    assert [sum(1 for x in f if ipc.degree(x) == d) for d in (1, 2, 3)] == [60, 210, 220]


def test_legendre_orthogonal_on_uniform_input():
    x = np.random.default_rng(0).random(400_000) * 2.0 - 1.0
    p = [ipc.legendre(n, x) for n in (1, 2, 3)]
    for i in range(3):
        for j in range(i + 1, 3):
            assert abs(np.mean(p[i] * p[j])) < 5e-3
    # variances 1/(2n+1) for n = 1, 2, 3
    assert np.allclose([np.mean(q * q) for q in p], [1 / 3, 1 / 5, 1 / 7], atol=3e-3)


@pytest.fixture(scope="module")
def data():
    u, us = ipc.inputs()
    net = massspring.make_network(tasks.NETWORK_SEED)
    return {
        "input": (tasks.input_only(u), u, us),
        "d87": (baselines.delay_line(u, baselines.D_FULL), u, us),
        "p3": (baselines.polynomial_window(u, 6), u, us),
        "body": (massspring.simulate(net, u), u, us),
    }


@pytest.mark.parametrize("name", list(REF))
def test_capacities_match_reference(data, name):
    c = ipc.capacity(*data[name])
    eps, by_degree = REF[name]
    assert c.epsilon == pytest.approx(eps, rel=RTOL, abs=ATOL)
    for d, v in by_degree.items():
        assert c.by_degree[d] == pytest.approx(v, rel=RTOL, abs=ATOL), (name, d)
