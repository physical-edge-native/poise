import numpy as np
import pytest

from poise import baselines

# Reference values computed on Linux (x86-64); CI checks them on Linux, macOS and Windows.
# See docs/design/2026-11-27-delayed-input-baseline.md, section "Checks".
SCORE_RTOL = 1e-7
REF = {
    "mc_d87": 29.999999999998902,
    "mc_dval": 29.999999999999797,
    "mc_p3": 5.033688777767198,
    "narma2_d87": 0.1558478061525174,
    "narma2_dval": 0.15346734063989997,
    "narma2_p3": 0.004071695121506007,
}
REF_CHOSEN = {
    "mc_dval": (1, 2, 4, 4, 8, 8, 8, 8, 16, 16, 16, 16, 16, 16, 16, 16) + (32,) * 14,
    "mc_p3": (2, 3, 4, 5, 6, 2, 3, 4, 1, 1, 1, 1, 1, 3, 6, 5, 6, 5, 6, 6, 2, 3, 1, 4, 5, 6, 2, 6, 4, 4),
    "narma2_dval": 8,
    "narma2_p3": 6,
}


def test_delay_line_values():
    u = np.array([1.0, 2.0, 3.0, 4.0])
    f = baselines.delay_line(u, 2)
    assert f.shape == (4, 3)
    assert np.array_equal(f, [[1, 0, 0], [2, 1, 0], [3, 2, 1], [4, 3, 2]])


def test_polynomial_window_values_and_counts():
    u = np.array([2.0, 3.0])
    f = baselines.polynomial_window(u, 2)
    # window at t=1: (u(t), u(t-1)) = (3, 2)
    # degree 1: 3, 2; degree 2: 9, 6, 4; degree 3: 27, 18, 12, 8
    assert np.array_equal(f[1], [3, 2, 9, 6, 4, 27, 18, 12, 8])
    assert [baselines.n_polynomial_features(n) for n in range(1, 7)] == [3, 9, 19, 34, 55, 83]
    assert baselines.n_polynomial_features(max(baselines.P_CHOICES)) <= 87


def test_choice_prefers_shorter_on_tie():
    u = np.random.default_rng(0).random(3200)
    target = u.copy()
    # Every parameter gives the same features, hence exactly the same validation score.
    c = baselines.choose_and_test(lambda p: u[:, None], (3, 1, 2), target, lambda a, b: 1.0, True)
    assert c.param == 3  # the first in the given order wins a tie; the choices are listed shortest first


def test_choice_treats_rounding_level_differences_as_a_tie():
    u = np.random.default_rng(0).random(3200)
    scores = iter([1.0, 1.0 + 2e-16, 1.0 + 4e-16])  # validation scores of params 1, 2, 3, then the test score
    c = baselines.choose_and_test(lambda p: u[:, None], (1, 2, 3), u, lambda a, b: next(scores, 0.5), True)
    assert c.param == 1


@pytest.fixture(scope="module")
def results():
    return baselines.run_all()


def test_baseline_scores_match_reference(results):
    got = {
        "mc_d87": results.mc_d87.total,
        "mc_dval": results.mc_dval.total,
        "mc_p3": results.mc_p3.total,
        "narma2_d87": results.narma2_d87,
        "narma2_dval": results.narma2_dval.test_score,
        "narma2_p3": results.narma2_p3.test_score,
    }
    for key, ref in REF.items():
        assert got[key] == pytest.approx(ref, rel=SCORE_RTOL), key


def test_chosen_window_lengths_match_reference(results):
    assert results.mc_dval.chosen == REF_CHOSEN["mc_dval"]
    assert results.mc_p3.chosen == REF_CHOSEN["mc_p3"]
    assert results.narma2_dval.param == REF_CHOSEN["narma2_dval"]
    assert results.narma2_p3.param == REF_CHOSEN["narma2_p3"]
