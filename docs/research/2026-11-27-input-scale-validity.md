# Up to which input scale the mass-spring model stays valid

Date: 2026-11-27. Issue: #32. Written by an AI assistant during a scheduled night run. This is a research
note that measures physical quantities of the simulations only. **No task score was computed**, and nothing
here changes the measurements in `docs/design/`.

## Question

`2026-11-27-spring-nonlinear-range.md` (#30) found that at the input scale used in the tasks, both networks
stay almost linear, and that the cubic terms matter only at larger scales. Before any measurement over input
scale, two things need checking:

1. **Validity.** The model has point masses and springs, with no contact or volume. If a spring shrinks
   towards zero length, the model no longer describes a plausible body.
2. **Time step.** Stronger inputs mean faster motion and stiffer cubic terms. Is the semi-implicit Euler
   step of 1 ms (`docs/design/2026-11-26-mass-spring-tasks.md`) still fine enough?

## Method

For each network (seed 1: the first network, and the network with the settings of Hauser et al. 2011 from
PR #29) and each task input (memory capacity: uniform in [−1, 1], seed 2; NARMA2: uniform in [0, 0.5],
seed 3), the first 1200 samples (24 s) were simulated with the input multiplied by 1, 3, 10 and 30. Two
quantities were recorded:

- the **shortest spring length relative to its rest length**, over all springs and samples (end of each
  sample);
- the **step check**: the same run with a 0.5 ms step (40 steps per sample instead of 20), and the largest
  difference in any spring length between the two runs after the first 200 samples. This difference is
  divided by the largest stretch in the run. Halving the step only shows whether the result has converged,
  not the absolute error, but a large change means the 1 ms step is too coarse.

Only the first 1200 samples were used, to keep the run short. The full runs (3200 samples) may reach slightly
shorter springs. The script is at the end and needs the code of PR #29 (commit `b96788e`) for the second
network.

## Results

| Network | Input | Scale | Shortest spring / rest length | Length change when the step is halved (fraction of largest stretch) |
|---|---|---|---|---|
| first | memory capacity | ×1 | 0.94 | 2.9e-3 |
| first | memory capacity | ×3 | 0.80 | 3.4e-3 |
| first | memory capacity | ×10 | 0.52 | 3.8e-3 |
| first | memory capacity | ×30 | 0.23 | **0.12** |
| first | NARMA2 | ×1 | 0.97 | 5.2e-4 |
| first | NARMA2 | ×3 | 0.86 | 5.0e-4 |
| first | NARMA2 | ×10 | 0.49 | 4.0e-4 |
| first | NARMA2 | ×30 | 0.41 | 1.7e-3 |
| Hauser settings | memory capacity | ×1 | 0.93 | 9.7e-4 |
| Hauser settings | memory capacity | ×3 | 0.80 | 8.9e-4 |
| Hauser settings | memory capacity | ×10 | 0.42 | 9.4e-4 |
| Hauser settings | memory capacity | ×30 | **0.06** | 8.7e-3 |
| Hauser settings | NARMA2 | ×1 | 0.89 | 1.0e-4 |
| Hauser settings | NARMA2 | ×3 | 0.64 | 4.9e-4 |
| Hauser settings | NARMA2 | ×10 | 0.52 | 3.9e-4 |
| Hauser settings | NARMA2 | ×30 | 0.19 | 6.6e-4 |

All runs stayed finite (no numerical blow-up).

## Findings

1. **Up to ×10, the model is valid and the 1 ms step is fine.** The shortest spring keeps at least 42 % of
   its rest length. Halving the step changes the lengths by at most 0.4 % of the largest stretch.
2. **At ×30 the model reaches its limits.** In the network with the Hauser settings, one spring shrinks to
   6 % of its rest length under the memory-capacity input, so the body nearly collapses there. In the first
   network the result depends on the step: halving it changes the lengths by 12 % of the largest stretch, so
   1 ms is too coarse for that run. The other two runs at ×30 look acceptable, but a measurement should apply
   one rule to all of them.
3. **Even at ×1, single springs are compressed by 3–11 %**, although the median stretch is about 0.1 %
   (#30). So the largest deformations are rare and come from a few springs. Which springs these are, and
   which input sequences cause them, was not checked.
4. Together with #30: the cubic terms start to matter at around ×10, and the model stops being trustworthy
   somewhere between ×10 and ×30. So a measurement over input scale has a usable window of about one order of
   magnitude above the current inputs, not more.

## Suggestion for a later measurement (not a decision)

If a measurement over input scale is opened, these could be fixed in its design record before measuring:

- scales 1, 2, 5 and 10 (inside the range checked here), the same for both networks;
- a validity rule checked on the full run: every spring keeps at least 25 % of its rest length, and halving
  the step changes the lengths by less than 1 % of the largest stretch; runs that break the rule are reported
  as invalid, not scored;
- larger scales only with a smaller step, and only if the rule holds.

Whether to open such a measurement is for the coordinator or the maintainer to decide. It stays inside
poise's current scope (mass-spring network, linear readout only, no change to the body).

## Script

```python
import dataclasses
import numpy as np
from poise import massspring as m, tasks

N = 1200
def halved(net):
    p = dataclasses.replace(net.params, dt=net.params.dt / 2, steps_per_sample=net.params.steps_per_sample * 2)
    return dataclasses.replace(net, params=p)

for name, net in [("first", m.make_network(1)), ("hauser", m.make_hauser_network(1))]:
    for task, (lo, hi, seed) in {"MC": (-1, 1, 2), "NARMA2": (0, .5, 3)}.items():
        u = tasks.uniform_inputs(seed, lo, hi)[:N]
        for sc in (1, 3, 10, 30):
            us = np.multiply(u, sc)
            L, L2 = m.simulate(net, us), m.simulate(halved(net), us)
            stretch = np.abs(L - net.rest_length)[200:]
            err = np.abs(L - L2)[200:]
            print(name, task, sc, np.min(L / net.rest_length), err.max() / stretch.max())
```
