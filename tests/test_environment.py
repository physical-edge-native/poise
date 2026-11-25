import numpy as np

import poise


def test_package_imports():
    assert poise.__doc__


def test_numpy_float64_is_deterministic():
    # The simulations rely on NumPy float64; the same computation must give the same bits.
    rng_a = np.random.default_rng(0)
    rng_b = np.random.default_rng(0)
    a = rng_a.standard_normal(1000)
    b = rng_b.standard_normal(1000)
    assert a.dtype == np.float64
    assert np.array_equal(a, b)
