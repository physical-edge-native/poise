# Information processing capacity of the mass-spring network

Date: 2026-11-27. Issue: #13. Decided by the maintainer (measure information processing capacity, #11); the
details were chosen by an AI assistant, which also wrote this record. The setup and the expectations were
written and committed **before** any capacity was computed; the results are added at the end.

## Why

The mass-spring network has memory (memory capacity 5.74 over delays 1–30) but helped little on NARMA2, and a
short delay line with cubic products did far better (#12). One explanation is that the network behaves mostly
linearly: its damping and cubic spring terms are much weaker than in Hauser et al. (2011)
(`docs/research/2026-11-26-prior-work.md`). Information processing capacity (J. Dambre, D. Verstraeten,
B. Schrauwen, S. Massar, *Scientific Reports* 2:514, 2012, DOI 10.1038/srep00514) measures, for a whole set of
functions of past inputs, how well a linear readout of the state reconstructs each one. Summed by degree, it
separates linear memory (degree 1) from nonlinear processing (degrees 2 and 3).

## Setup

- **Input**: independent values uniform in [−1, 1] (seed 2, as for memory capacity), longer run: 200 samples
  discarded, then 10,000 for training and 10,000 for testing.
- **Body**: the network of `2026-11-26-mass-spring-tasks.md` (seed 1, 87 springs), unchanged.
- **Functions** (targets): products of normalised Legendre polynomials of past inputs,
  `P1(x) = x`, `P2(x) = (3x² − 1)/2`, `P3(x) = (5x³ − 3x)/2`, which are orthogonal for this input:
  - degree 1: `P1(u(t−k))`, k = 0 … 59 (60 functions);
  - degree 2: `P2(u(t−k))` and `P1(u(t−i))·P1(u(t−j))` (i < j), within k, i, j = 0 … 19 (210 functions);
  - degree 3: `P3(u(t−k))`, `P2(u(t−i))·P1(u(t−j))` (i ≠ j), `P1·P1·P1` (i < j < l), within 0 … 9
    (220 functions).
- **Capacity of one function**: the squared correlation, on the test part, between the function and the
  readout's reconstruction. The readout is the same ridge regression as everywhere in poise (standardised
  features plus a constant, penalty `1e-6 × training samples`), fitted on the training part. This is
  Dambre et al.'s capacity (1 − normalised error) evaluated on held-out data instead of the training data.
- **Threshold against finite data**: a readout fitted to an unrelated target still reaches a small positive
  test score by chance. For every function, the same capacity is computed with the target built from an
  **independent input sequence** (seed 99) instead of the real one. The threshold ε is the largest of these
  surrogate capacities over all 490 functions. Capacities at or below ε count as zero.
- **Totals**: sum of capacities per degree and overall. For independent inputs the total over all functions is
  at most the number of linearly independent features, here 87 (Dambre et al. 2012). Only the 490 listed
  functions are measured, so totals are lower bounds.
- **Same measure for the baselines** of #12, as checks of the method: the current input alone, D87
  (`u(t) … u(t−86)`), and P3 with window 6.
- **Input amplitude** (in the measurement script, not in the tests): the body's capacities by degree with the
  input scaled by 0.25, 0.5, 1, 2 and 4 (the input force grows with the scale).

## What is expected before measuring

- Checks of the method: the current input alone gives capacity 1 for `P1(u(t))` and about 0 elsewhere; D87
  gives degree-1 capacity close to 60 (all measured delays) and nonlinear capacity about 0; P3 with window 6
  gives capacity close to 1 for every function of degree ≤ 3 within delays 0 … 5 (6 + 21 + 56 = 83 of them that
  are in the measured set) and about 0 outside.
- The body: most of its capacity at degree 1; degree 2 and 3 small; the total well below 87. With larger input
  amplitudes, degree 2 and 3 grow at the expense of degree 1 (the springs' cubic terms are excited more).

## Checks

- Unit tests: the Legendre functions are orthogonal on uniform input (sample means close to 0 and to the known
  variances); the function list has 60 + 210 + 220 entries without duplicates.
- The capacities of the baselines and of the body for the fixed seeds are stored in the tests and compared on
  Linux, macOS and Windows with a relative tolerance of 1e-7 for totals (same reason as before: BLAS and LAPACK
  round differently), and ε likewise.

## Results

Measured on 2026-11-27 with `uv run python scripts/measure_mass_spring.py --ipc`. Nothing in the setup above
was changed after measuring. The tests store the values for the baselines and for the body at amplitude 1.

| Features | Degree 1 | Degree 2 | Degree 3 | Total | ε |
|---|---|---|---|---|---|
| current input only (1) | 1.001 | 0.001 | 0.002 | 1.004 | 7.7e-4 |
| D87, `u(t) … u(t−86)` (87) | 60.000 | 0 | 0 | 60.000 | 8.3e-4 |
| P3, window 6 (83) | 6.000 | 21.000 | 56.002 | 83.002 | 8.4e-4 |
| **body, amplitude 1 (87)** | **9.176** | **2.046** | **0.004** | **11.226** | 6.5e-4 |
| body, amplitude 0.25 | 10.022 | 1.537 | 0.004 | 11.563 | 7.4e-4 |
| body, amplitude 0.5 | 9.712 | 1.816 | 0.004 | 11.532 | 6.7e-4 |
| body, amplitude 2 | 8.361 | 1.940 | 0.004 | 10.306 | 6.5e-4 |
| body, amplitude 4 | 7.410 | 1.096 | 0.004 | 8.510 | 8.2e-4 |

Against the expectations written before measuring:

- **Checks of the method held.** The input alone, D87 and P3 give the capacities their construction implies (1,
  60 and 83). The small values above ε that should be 0 (about 0.001–0.002 in total for the input alone) show
  what the threshold lets through by chance: the threshold is the largest of 490 surrogate values from one
  independent input, so a few chance values a little above it remain.
- **The body is mostly linear, as expected**: 9.2 of its 11.2 at degree 1, 2.0 at degree 2, and essentially
  **nothing at degree 3** (0.004, the chance level). Its total, 11.2, uses about 13 % of the 84 useful
  features' possible capacity (three of the 87 springs never change; see the erratum below): the spring
  lengths are strongly dependent on each other.
- **The expectation about amplitude did not hold.** Larger inputs did not move capacity from degree 1 to
  degrees 2 and 3: degree 3 stayed at chance level at every amplitude, degree 2 peaked near amplitude 1 and fell
  at 4, and the total fell from 11.6 to 8.5. The cubic spring terms do not show up as degree-3 capacity in this
  network at these amplitudes.
- This explains the NARMA2 result of #12: the target depends on `u(t)³` and on products of past values, and the
  body has no degree-3 capacity and little degree-2 capacity, while P3 has them by construction.
- Not shown: why the cubic terms do not produce degree-3 capacity (weak damping and cubic coefficients compared
  with Hauser et al. 2011 are one candidate; #14 measures a network with that paper's settings), and how the
  capacity spreads over delays (only totals by degree are reported here).

## Note on the feature count (2026-11-28, #37)

After this record's setup was written, an erratum (#37, in `2026-11-26-mass-spring-tasks.md`) found that three
of the body's 87 springs join two fixed masses and never change length, so the body has **84 useful features**.
The setup above still says 87 where it states the bound and the table's feature count; the bound for the body is
84. The measured capacities do not change (constant features add nothing to a linear readout).
