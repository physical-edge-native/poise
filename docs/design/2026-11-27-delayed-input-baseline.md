# Delayed-input baselines for the mass-spring measurements

Date: 2026-11-27. Issue: #12. Decided by the maintainer (add delayed-input baselines; the three variants
below); the details were chosen by an AI assistant, which also wrote this record. The setup was written
and committed **before** any of these baselines was measured; the results are added at the end.

## Why

The first measurements (`2026-11-26-mass-spring-tasks.md`) compared the mass-spring network with the same
linear readout applied to the current input alone. That baseline has no memory, so on memory capacity the
body wins almost by construction, and prior soft-body work used the same weak baseline
(`docs/research/2026-11-26-prior-work.md`). A readout on a window of past inputs (a tapped delay line)
answers two questions the input-only baseline cannot:

- how many past inputs the body is worth, as memory;
- whether the body adds anything beyond memory, by comparing with a delay line that also has explicit
  nonlinear (polynomial) features.

## Setup

Everything not listed here is the same as in `2026-11-26-mass-spring-tasks.md`: the inputs and seeds, the
tasks (memory capacity over delays 1–30; NARMA2 with the second-order system and inputs uniform in
[0, 0.5]), the split (200 discarded, 2000 training, 1000 test), the readout (ridge regression on
standardised features plus a constant, penalty `1e-6 × training samples`) and the scores.

Delay-line features at time `t` use `u(t), u(t−1), …`; the 200 discarded samples at the start are longer
than any window below, so every window in the training and test parts is complete.

Three baselines are added:

| Name | Features | Window length |
|---|---|---|
| **D87** | `u(t) … u(t−86)` (87 features) | fixed: equal to the number of body features (87 springs) |
| **D-val** | `u(t) … u(t−K)` | `K` chosen from {0, 1, 2, 4, 8, 16, 32, 64, 86} by validation |
| **P3** | all products of degree 1, 2 and 3 of `u(t) … u(t−L+1)` | `L` chosen from 1 … 6 by validation |

- **Validation** uses only the training part: fit on its first 1500 samples, score on its last 500
  (squared correlation for memory capacity, normalised mean squared error for NARMA2), pick the best
  length (the shorter one on an exact tie), then refit on the whole training part. The test part is never
  used to choose. For memory capacity the length is chosen separately for each delay.
- **P3** with `L = 6` has 6 + 21 + 56 = 83 features, fewer than the body's 87. Products include squares
  and cubes of the same input (monomials with repetition).

## What is expected before measuring

Written down so that the results can be checked against it:

- D87 contains `u(t−k)` itself for every delay up to 86, so its memory capacity over delays 1–30 should
  be close to 30, far above the body's 5.74. D-val should be similar.
- P3 can only recall delays shorter than its window (at most 5), so its memory capacity should be at most
  about 5.
- On NARMA2, which depends on `u(t)³` and on products of past outputs, the linear delay lines may do about
  as well as or better than the body; P3 has `u(t)³` explicitly and may do better than all others.

None of these outcomes would be a failure of the body or of the measurement; the measured differences,
including where the body is worse, are the result.

## Checks

- Scores of the new baselines are stored in the tests and compared on Linux, macOS and Windows with the
  same relative tolerance as before (1e-7) and the same reason (the readout uses BLAS and LAPACK, which
  round differently on different systems). The chosen window lengths are stored and must match exactly.
- Unit tests: the delay-line and polynomial features have the expected shape and values on a small input.

## Results

(Added after the measurements.)
