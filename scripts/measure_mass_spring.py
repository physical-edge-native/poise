"""Print the memory capacity and NARMA2 scores of the mass-spring network and of the baseline.

Usage: uv run python scripts/measure_mass_spring.py
Setup and reasons: docs/design/2026-11-26-mass-spring-tasks.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from poise import massspring, tasks  # noqa: E402


def main() -> None:
    net = massspring.make_network(tasks.NETWORK_SEED)
    r = tasks.run_all(lambda u: massspring.simulate(net, u))
    print(f"network: {net.params.n_masses} masses, {net.n_springs} springs (seed {tasks.NETWORK_SEED})")
    print(f"memory capacity   body {r.mc_body.total:.6f}   baseline {r.mc_baseline.total:.6f}")
    print("  per delay (body):    " + " ".join(f"{x:.3f}" for x in r.mc_body.per_delay))
    print("  per delay (baseline):" + " ".join(f"{x:.3f}" for x in r.mc_baseline.per_delay))
    print(f"NARMA2 NMSE        body {r.narma2_body:.6f}   baseline {r.narma2_baseline:.6f}")


if __name__ == "__main__":
    main()
