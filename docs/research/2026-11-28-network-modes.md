# Decay times and frequencies of the two mass-spring networks

Date: 2026-11-28. Issue: #39. Written by an AI assistant during a scheduled night run. This is a research
note. It analyses the simulated bodies only. **No task score was computed**, and nothing here changes the
measurements in `docs/design/`.

## Question

At the input scale used in the tasks, both networks behave almost linearly: the cubic forces are 1e-7 to 1e-5
of the linear ones (`2026-11-27-spring-nonlinear-range.md`, #30). A linear body is fully described by its
**modes**. Each mode decays with a time constant τ and may oscillate at a frequency f. These numbers set how
long a body can hold a trace of past input. How do the first network and the network with the settings of
Hauser et al. 2011 (`docs/design/2026-11-27-hauser-network.md`) compare, and how do their time scales relate
to the 20 ms sampling interval and to the measured memory-capacity curves?

## Method

Each network (seed 1) is linearised at rest. Each spring contributes `k1·b·bᵀ` to the stiffness matrix and
`d1·b·bᵀ` to the damping matrix, where b is the direction of the spring placed at its two masses' coordinates.
The cubic terms have zero slope at rest and drop out. Only the free masses are kept. The eigenvalues λ of the
first-order system `[[0, I], [−K/m, −D/m]]` give τ = −1/Re λ, f = |Im λ| / 2π, and the damping ratio
−Re λ / |λ| for oscillating modes. The script is at the end.

This describes small motions around rest. It says nothing about the input weights, that is, which modes the
input actually excites.

## Results

| | First network | Hauser settings |
|---|---|---|
| Free masses × 2 directions × (position, velocity) | 104 eigenvalues | 112 eigenvalues |
| All modes decay (largest Re λ) | yes (−0.0066 /s) | yes (−0.035 /s) |
| Decay time τ: shortest / median / longest | 0.022 s / 0.17 s / 152 s | 0.003 s / 0.30 s / 28 s |
| Modes with τ > 0.02 s (one sample) | 104 (all) | 92 |
| Modes with τ > 0.6 s (30 samples, the longest delay in memory capacity) | 19 | 44 |
| Modes with τ > 2 s | 8 | 21 |
| Oscillating modes | 88 of 104 | 40 of 112 |
| Frequency of oscillating modes: median / highest | 1.3 Hz / 2.5 Hz | 0.44 Hz / 1.6 Hz |
| Damping ratio of oscillating modes: median / lowest | 0.46 / 0.02 | 0.63 / 0.27 |
| Fastest mode, \|λ\| × 1 ms step | 0.046 | 0.30 |

The five slowest decay times are 152, 152, 5.9, 5.9 and 4.8 s for the first network, and 28, 20, 17, 13 and
12 s for the Hauser settings.

## Findings

1. **The first network is mostly a set of lightly damped oscillators.** 88 of its 104 modes oscillate, at about
   1–2.5 Hz. One oscillating pair decays in about 150 s, with a damping ratio of 0.02. This fits its
   memory-capacity curve, which is high at short delays and still 0.12 at delay 30 (0.6 s).
2. **The network with the Hauser settings is mostly overdamped.** Only 40 of 112 modes oscillate. Its strong
   linear damping (`d1` log-uniform up to 100) turns many modes into pure decays, and many are slow: 44 modes
   outlast 0.6 s and 21 outlast 2 s. This fits two earlier observations: its flat memory-capacity curve (0.26 at
   delay 1, between 0.06 and 0.12 from delay 10 to 30; PR #29), and its slow relaxation after release, with a time
   constant of about 15 s (the same record). Slow, non-oscillating decays smear past inputs together. They keep
   a trace for a long time but separate individual delays poorly.
3. **20 of the 112 modes of the Hauser-style network decay within one sample** (τ < 20 ms). The readout sees the
   body only once every 20 ms, so these modes cannot carry information from one sample to the next. The body has
   fewer useful degrees of freedom than its size suggests. The first network has no such modes.
4. **The 1 ms step is fine for the first network but less so for the Hauser settings.** For the fastest mode,
   |λ| × step is 0.046 for the first network and 0.30 for the Hauser settings. Both are well inside the range
   where the explicit step stays stable (it fails at about 2), so the simulation does not blow up. But a mode
   that loses 30 % per step is computed only coarsely. Since that mode decays within a few milliseconds and the
   step-halving check of #32 changed lengths by less than 0.1 % of the largest stretch, this matters little for
   what the readout sees.
5. **For a soft foot**, this suggests the time scales of a body should be compared with the time scale of the
   task before measuring anything. A body whose modes are much faster than the sampling interval, or much slower
   than the time window the task needs, has little to offer a linear readout. erg's gait timing is not used here:
   it was not checked, and it belongs to erg and to the soft-foot design work (#21).

## Suggestion (not a decision)

When a soft-foot model exists, compute the same table first, before any task, and record its decay times and
frequencies next to the sampling interval and the gait period in the design record.

## Script

```python
import numpy as np
from poise import massspring as m

def eigenvalues(net):
    n = net.params.n_masses
    K = np.zeros((2*n, 2*n)); D = np.zeros((2*n, 2*n))
    for a, b, k1, d1 in zip(net.spring_i, net.spring_j, net.k1, net.d1):
        e = net.pos0[b] - net.pos0[a]; e = e / np.linalg.norm(e)
        B = np.zeros(2*n); B[2*a:2*a+2] = -e; B[2*b:2*b+2] = e
        K += k1 * np.outer(B, B); D += d1 * np.outer(B, B)
    f = np.concatenate([[2*i, 2*i+1] for i in np.flatnonzero(net.free)])
    K, D = K[np.ix_(f, f)], D[np.ix_(f, f)]
    N, mass = len(f), net.params.mass
    A = np.block([[np.zeros((N, N)), np.eye(N)], [-K / mass, -D / mass]])
    return np.linalg.eigvals(A)

for name, net in [("first", m.make_network(1)), ("hauser", m.make_hauser_network(1))]:
    lam = eigenvalues(net)
    tau = -1 / lam.real
    print(name, np.sort(tau)[-5:], np.sum(tau > 0.02), np.sum(tau > 0.6), np.sum(np.abs(lam.imag) > 1e-9))
```
