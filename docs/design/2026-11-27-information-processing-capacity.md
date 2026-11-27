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

(Added after the measurements.)
