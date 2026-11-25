import numpy as np

from poise import readout, tasks


def test_narma2_recurrence():
    u = np.array([0.1, 0.2, 0.3])
    y = tasks.narma2_target(u)
    y1 = 0.6 * 0.1**3 + 0.1
    y2 = 0.4 * y1 + 0.4 * y1 * 0.0 + 0.6 * 0.2**3 + 0.1
    y3 = 0.4 * y2 + 0.4 * y2 * y1 + 0.6 * 0.3**3 + 0.1
    assert np.allclose(y, [y1, y2, y3], rtol=0, atol=1e-15)


def test_readout_recovers_a_linear_map():
    rng = np.random.default_rng(0)
    x = rng.random((500, 3))
    y = x @ np.array([2.0, -1.0, 0.5]) + 3.0
    model = readout.fit(x, y)
    assert np.allclose(model.predict(x), y, atol=1e-4)


def test_memory_capacity_of_a_perfect_delay_line():
    # Features that are exactly u(t-1) .. u(t-3) recall those delays fully and nothing else.
    u = tasks.uniform_inputs(11, -1.0, 1.0)
    feats = np.stack([np.concatenate([np.zeros(k), u[:-k]]) for k in (1, 2, 3)], axis=1)
    mc = tasks.memory_capacity(feats, u, max_delay=5)
    assert np.allclose(mc.per_delay[:3], 1.0, atol=1e-9)
    assert max(mc.per_delay[3:]) < 0.02


def test_baseline_has_almost_no_memory():
    u = tasks.uniform_inputs(12, -1.0, 1.0)
    mc = tasks.memory_capacity(tasks.input_only(u), u)
    assert mc.total < 0.1
