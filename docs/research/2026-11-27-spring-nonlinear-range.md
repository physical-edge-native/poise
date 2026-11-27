# How far the mass-spring networks reach their nonlinear range

Date: 2026-11-27. Issue: #30. Written by an AI assistant during a scheduled night run. This is a research
note: it measures physical quantities of the simulations only. **No task score was computed** for any new
setting, and nothing here changes the measurements in `docs/design/`.

## Question

On NARMA2 (a benchmark that needs a nonlinear combination of past inputs), the first mass-spring network
(normalised error 0.347) and the network with the settings of Hauser et al. 2011 (0.396, PR #29) do little
better than a readout on the current input alone (0.401), while a cubic polynomial of the last six inputs
reaches 0.004 (`docs/design/2026-11-27-delayed-input-baseline.md`). Each spring's force is
`k1·s + k3·s³ + d1·r + d3·r³` (`s` = stretch, `r` = rate of change of length). If the input forces are too
small, `s` and `r` stay small and the cubic terms do nothing, so the body acts as an almost linear system.
How large are they under the task inputs?

## Method

For each network (seed 1) and each task input (memory capacity: uniform in [−1, 1], seed 2; NARMA2: uniform
in [0, 0.5], seed 3), the full run of 3200 samples was simulated with the input as used in the tasks (×1)
and multiplied by 10 and by 100. After the 200 discarded samples, over all springs and samples:

- relative stretch `|s| / rest length`;
- ratio of cubic to linear spring force, `k3·s² / k1`;
- ratio of cubic to linear damping force, `d3·r² / d1`, with `r` estimated from the change of length
  between samples (20 ms apart). This is a coarse estimate: it misses faster motion inside a sample.

The script (run with `PYTHONPATH=. uv run python <script>` on the branch of PR #29, commit `b96788e`, which
has `make_hauser_network`) is at the end.

## Results

Median / 99th percentile over springs and samples.

| Network | Input | Scale | Relative stretch | `k3·s²/k1` | `d3·r²/d1` |
|---|---|---|---|---|---|
| first | memory capacity | ×1 | 7.6e-4 / 2.0e-2 | 3.3e-8 / 4.3e-5 | 4.2e-7 / 5.1e-4 |
| first | memory capacity | ×10 | 8.4e-3 / 0.20 | 3.8e-6 / 9.6e-3 | 3.9e-5 / 5.0e-2 |
| first | memory capacity | ×100 | 6.8e-2 / 1.2 | 2.3e-4 / 0.32 | 2.1e-3 / 1.7 |
| first | NARMA2 | ×1 | 1.6e-3 / 4.1e-2 | 1.5e-7 / 5.0e-4 | 3.0e-8 / 3.6e-5 |
| first | NARMA2 | ×10 | 2.0e-2 / 0.60 | 2.2e-5 / 0.29 | 5.5e-6 / 4.7e-3 |
| first | NARMA2 | ×100 | 6.1e-2 / 2.1 | 2.0e-4 / 2.2 | 1.7e-4 / 0.21 |
| Hauser settings | memory capacity | ×1 | 1.3e-3 / 3.1e-2 | 8.1e-7 / 1.5e-3 | 3.9e-6 / 9.6e-3 |
| Hauser settings | memory capacity | ×10 | 1.4e-2 / 0.28 | 8.1e-5 / 0.14 | 3.7e-4 / 0.67 |
| Hauser settings | memory capacity | ×100 | 0.11 / 1.7 | 6.0e-3 / 1.8 | 2.4e-2 / 9.8 |
| Hauser settings | NARMA2 | ×1 | 9.1e-3 / 0.11 | 2.7e-5 / 5.7e-2 | 2.9e-7 / 6.7e-4 |
| Hauser settings | NARMA2 | ×10 | 8.6e-2 / 1.4 | 3.4e-3 / 1.7 | 4.3e-5 / 4.0e-2 |
| Hauser settings | NARMA2 | ×100 | 0.24 / 3.8 | 2.7e-2 / 10 | 2.7e-3 / 1.6 |

## Findings

1. **At the scale used in the tasks, both bodies are almost linear in their materials.** The cubic spring
   force is typically 10⁻⁷ to 10⁻⁵ of the linear one, and even in the most stretched 1 % of cases at most
   6 % (Hauser settings, NARMA2). The cubic dampers are smaller still. Springs stretch by about 0.1 % of
   their length (median). The stronger cubic coefficients of the Hauser settings (100–200 instead of
   1–200) raise the ratios by one to two orders of magnitude, but not into the nonlinear range.
2. **The remaining nonlinearity is geometric.** A spring length is the distance between two moving masses,
   a nonlinear function of their positions, and forces act along directions that turn as the body moves.
   With displacements of 0.1 % these effects are also small (second order in the displacement). So with
   the current inputs, the bodies offer a linear readout little beyond a linear filter of past inputs,
   which agrees with the NARMA2 results.
3. **Scaling the input by 10 reaches the cubic range only in the tails; by 100 the model breaks down.**
   At ×10 the 99th percentile of `k3·s²/k1` reaches 0.1–1.7, while the median stays small. At ×100 springs
   are stretched or compressed by more than their own length (relative stretch above 1). A spring
   compressed to zero length has no direction, and springs then pass through each other: the model has no
   contact or volume, so results in that range would describe a numerical model, not a plausible body.
   Somewhere between ×10 and ×30 is the range where the cubic terms matter and the model is still
   meaningful; this note does not narrow it further.
4. **NARMA2 inputs have a non-zero mean** (0.25), so they also pre-stretch the body statically; this is
   why NARMA2 stretches are larger than memory-capacity ones at the same scale.

## What a later measurement over input scale would need to fix before measuring

Only a suggestion; whether to measure it is a decision for an issue (in the design records' style, choices
written down before any score is computed):

- the scales to test, fixed in advance (for example 1, 3, 10, 30), with the same scale for every body and
  the same inputs given to the baselines (which are invariant to scale up to the standardisation of
  features, except P3, whose products are also only rescaled);
- a validity rule decided in advance, for example "no spring shorter than 10 % of its rest length at any
  step", with runs that break it reported as invalid instead of scored;
- that memory capacity is expected to fall as the body becomes nonlinear (the known trade-off between memory
  and nonlinearity in reservoirs; Dambre et al. 2012, cited in `2026-11-26-prior-work.md`), so both tasks and,
  once on main, the information processing capacity (#13) should be reported for every scale;
- that the time step may need checking at larger scales (stiffer effective springs); the semi-implicit Euler
  step of 1 ms should be confirmed stable, for example by halving it once.

Choosing a scale by the task score would be tuning the input to the task. Reporting every scale fixed in
advance is not.

## Script

```python
import numpy as np
from poise import massspring as m, tasks

def stats(net, u, scale):
    p = net.params
    L = m.simulate(net, np.multiply(u, scale))[tasks.WASHOUT:]
    s = L - net.rest_length
    rel = np.abs(s) / net.rest_length
    cubic = net.k3 * s**2 / net.k1
    r = np.diff(L, axis=0) / (p.dt * p.steps_per_sample)
    dratio = net.d3[None] * r**2 / net.d1[None]
    q = lambda a: (np.median(a), np.percentile(a, 99), a.max())
    return q(rel), q(cubic), q(dratio)

for name, net in [("first", m.make_network(1)), ("hauser", m.make_hauser_network(1))]:
    for task, (lo, hi, seed) in {"MC": (-1, 1, 2), "NARMA2": (0, .5, 3)}.items():
        u = tasks.uniform_inputs(seed, lo, hi)
        for sc in (1, 10, 100):
            print(name, task, sc, stats(net, u, sc))
```
