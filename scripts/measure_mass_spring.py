"""Print the memory capacity and NARMA2 scores of the mass-spring network and of the baseline.

Usage: uv run python scripts/measure_mass_spring.py
Setup and reasons: docs/design/2026-11-26-mass-spring-tasks.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse  # noqa: E402

import numpy as np  # noqa: E402

from poise import baselines, ipc, massspring, tasks  # noqa: E402


def print_ipc(net) -> None:
    """Information processing capacity (docs/design/2026-11-27-information-processing-capacity.md)."""
    u, us = ipc.inputs()
    print("information processing capacity (held-out, thresholded), by degree:")
    rows = [
        ("current input only", tasks.input_only(u)),
        ("D87", baselines.delay_line(u, baselines.D_FULL)),
        ("P3, window 6", baselines.polynomial_window(u, 6)),
        ("body, amplitude 1", massspring.simulate(net, u)),
    ]
    for name, feats in rows:
        c = ipc.capacity(feats, u, us)
        print(f"  {name:20s} " + "  ".join(f"d{d} {v:8.4f}" for d, v in c.by_degree.items())
              + f"   total {c.total:8.4f}   eps {c.epsilon:.2e}")
    for a in ipc.AMPLITUDES:
        if a == 1.0:
            continue
        c = ipc.capacity(massspring.simulate(net, np.multiply(u, a)), u, us)
        print(f"  {'body, amplitude ' + str(a):20s} " + "  ".join(f"d{d} {v:8.4f}" for d, v in c.by_degree.items())
              + f"   total {c.total:8.4f}   eps {c.epsilon:.2e}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ipc", action="store_true", help="also measure information processing capacity (slow)")
    args = parser.parse_args()
    net = massspring.make_network(tasks.NETWORK_SEED)
    r = tasks.run_all(lambda u: massspring.simulate(net, u))
    print(f"network: {net.params.n_masses} masses, {net.n_springs} springs (seed {tasks.NETWORK_SEED})")
    print(f"memory capacity   body {r.mc_body.total:.6f}   baseline {r.mc_baseline.total:.6f}")
    print("  per delay (body):    " + " ".join(f"{x:.3f}" for x in r.mc_body.per_delay))
    print("  per delay (baseline):" + " ".join(f"{x:.3f}" for x in r.mc_baseline.per_delay))
    print(f"NARMA2 NMSE        body {r.narma2_body:.6f}   baseline {r.narma2_baseline:.6f}")
    b = baselines.run_all()
    print("delayed-input baselines (docs/design/2026-11-27-delayed-input-baseline.md):")
    print(f"memory capacity   D87 {b.mc_d87.total:.6f}   D-val {b.mc_dval.total:.6f}   P3 {b.mc_p3.total:.6f}")
    print("  D-val chosen K per delay: " + " ".join(str(x) for x in b.mc_dval.chosen))
    print("  P3 chosen L per delay:    " + " ".join(str(x) for x in b.mc_p3.chosen))
    print("  per delay (D87):  " + " ".join(f"{x:.3f}" for x in b.mc_d87.per_delay))
    print("  per delay (P3):   " + " ".join(f"{x:.3f}" for x in b.mc_p3.per_delay))
    print(f"NARMA2 NMSE        D87 {b.narma2_d87:.6f}   D-val {b.narma2_dval.test_score:.6f} (K={b.narma2_dval.param})"
          f"   P3 {b.narma2_p3.test_score:.6f} (L={b.narma2_p3.param})")
    if args.ipc:
        print_ipc(net)


if __name__ == "__main__":
    main()
