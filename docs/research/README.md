# Research notes

Written by an AI assistant during a scheduled night run on 2026-11-28. These notes survey earlier work and
analyse the simulated bodies. Measurements whose setup is fixed before measuring live in `docs/design/`.
The numbers below are copied from those records. This page adds no new measurements.

## The notes

| Note | What it covers |
|---|---|
| [`2026-11-26-prior-work.md`](2026-11-26-prior-work.md) | Earlier work on soft and compliant bodies used for computation (Hauser et al. 2011, Nakajima et al.), the tasks and baselines they used, and how they differ from poise's |
| [`2026-11-27-spring-nonlinear-range.md`](2026-11-27-spring-nonlinear-range.md) | How far the springs are stretched under the task inputs, and how small the cubic (nonlinear) forces are |
| [`2026-11-27-input-scale-validity.md`](2026-11-27-input-scale-validity.md) | Up to which input scale the model stays physically valid and the 1 ms time step stays accurate |
| [`2026-11-27-sensing-resolution.md`](2026-11-27-sensing-resolution.md) | How finely a sensor would need to measure deformation to see the signals a readout uses |
| [`2026-11-28-network-modes.md`](2026-11-28-network-modes.md) | Decay times and frequencies of the two networks, linearised at rest |

## Measured results so far

Two random mass-spring networks (seed 1) and several baselines. Each row uses the same linear readout, the
same inputs and the same train/test split. Sources: `docs/design/2026-11-26-mass-spring-tasks.md`,
`2026-11-27-delayed-input-baseline.md` and `2026-11-27-hauser-network.md`.

| Readout on | Useful features | Memory capacity, delays 1–30 (higher is better) | NARMA2 error (lower is better) |
|---|---|---|---|
| current input only | 1 | 0.03 | 0.401 |
| first network (each mass joined to its 5 nearest) | 84 of 87 springs | **5.74** | **0.347** |
| network with the settings of Hauser et al. 2011 | 77 | 3.23 | 0.396 |
| last 87 inputs (D87) | 87 | 30.00 | 0.156 |
| last K inputs, K chosen by validation (D-val) | ≤ 87 | 30.00 | 0.153 (K = 8) |
| products up to degree 3 of the last L inputs (P3) | ≤ 83 | 5.03 | 0.004 (L = 6) |

Memory capacity measures how well a linear readout can recall past inputs. NARMA2 is a benchmark that needs
a nonlinear combination of past inputs. Three of the first network's 87 springs join fixed masses and never
change, so it has 84 useful features (erratum, #37).

## What has been found

1. **The bodies hold a fading trace of past inputs**, which the current input alone does not have. That is
   the property a physical reservoir relies on.
2. **On these tasks, a short window of past inputs does better than either body.** The window does better on
   memory by construction. On NARMA2 the linear window gets an error of 0.153 and the cubic window 0.004,
   against 0.347 and 0.396 for the bodies. This is a negative result for the bodies, and it is reported as
   such.
3. **At the input scale used in the tasks, both bodies are almost linear.** Their cubic forces are 1e-7 to
   1e-5 of the linear ones (median). This explains why they add little nonlinearity. The cubic terms start
   to matter at about 10 times the input, and the model stops being valid between 10 and 30 times.
4. **The two networks behave differently.** The first is mostly lightly damped oscillators at 1–2.5 Hz. The
   one with the Hauser settings is mostly overdamped, with many slow decays and 20 modes that die out within
   one 20 ms sample. These differences match their memory curves.
5. **The signals are small.** Spring lengths fluctuate by about 0.1 %. A real deformation sensor would need
   to resolve about 0.01 % strain if a real body deformed this little.

All of this comes from one seed of each network, one input scale and one sampling interval.

## Open questions and where they are tracked

- Information processing capacity: how much of each body's capacity is memory and how much is nonlinear
  (#13).
- The same measurements at input scales 1, 2, 5 and 10, with a validity rule fixed in advance (#34; waits
  for #13).
- The soft foot for erg, the next body (#21), and prior work on legged robots (#20).
- Which simulator and reproducibility rule the soft body will use (#15; waits for #21).
