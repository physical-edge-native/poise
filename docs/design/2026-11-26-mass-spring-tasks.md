# First measurements: a mass-spring network with memory capacity and NARMA2

Date: 2026-11-26. Issue: #9. Decided by the maintainer (tasks, cross-platform checks); the details below
were chosen by an AI assistant, which also wrote this record. The setup was written and committed
**before** any task score was computed; the measured values are added at the end.

## Question for this step

Before a soft arm, settle the tasks, the measurements and the comparison on the smallest body that
behaves like a physical reservoir: does the state of a random mass-spring network, read with a linear
readout, hold more of the recent input (memory) and support a nonlinear task better than the same
readout applied to the current input alone?

No claim is made that the body is better than any other approach. The numbers below, next to the
baseline, are the result, including where the body does not help.

## Network

Implemented in `poise/massspring.py`, all parameters from one seed (`make_network(seed)`):

- 30 point masses of 1 kg placed uniformly at random in the unit square.
- Each mass is joined to its 3 nearest masses; a pair is joined once. Rest length = initial distance.
- Each spring has a nonlinear force along its length,
  `f = k1·s + k3·s³ + d1·r + d3·r³`, where `s` is the stretch (length − rest length) and `r` the rate
  of change of the length. Coefficients drawn uniformly: `k1` in [1, 100], `k3` in [1, 200],
  `d1` in [1, 10], `d3` in [1, 10]. This follows the kind of network used in the literature on
  compliant bodies as reservoirs (Hauser et al., 2011); the values are our own choice and were **not**
  checked against that paper.
- The 4 masses with the smallest x are fixed.
- 20 % of the free masses (5 masses) receive the input as a horizontal force `w·u(t)`, with a weight
  `w` per mass drawn uniformly in [−1, 1].
- Time stepping: semi-implicit Euler with a fixed step of 1 ms; each input sample is held for 20 steps
  (one sample = 20 ms).
- The state given to the readout is the length of every spring at the end of each sample.

## Readout

Implemented in `poise/readout.py`. Ridge regression (least squares with a small penalty on the size of
the weights) on the features plus a constant:

- each feature is standardised with the mean and standard deviation of the training part;
- penalty `λ = 1e-6 × (number of training samples)`, fixed in advance and not tuned on the test part.

Run length for every task: 200 samples discarded at the start (so the effect of the initial state
fades), then 2000 samples for training and 1000 for testing.

## Tasks and metrics

Implemented in `poise/tasks.py`.

- **Memory capacity.** Input `u(t)` independent and uniform in [−1, 1]. For each delay `k = 1 … 30`
  a separate readout reconstructs `u(t−k)`; its score is the squared correlation between the target
  and the reconstruction on the test part. The memory capacity is the sum over `k`. Higher means the
  state holds more of the recent input.
- **NARMA2.** Input `u(t)` independent and uniform in [0, 0.5]. Target
  `y(t+1) = 0.4·y(t) + 0.4·y(t)·y(t−1) + 0.6·u(t)³ + 0.1`, starting from `y = 0`. The readout at time
  `t` predicts `y(t+1)`. Score: normalised mean squared error (mean squared error divided by the
  variance of the target) on the test part. Lower is better; 1 is what predicting the mean gives.

Seeds: network seed 1; input seeds 2 (memory capacity) and 3 (NARMA2).

## Baseline

The same readout (same standardisation, penalty, split and targets) on the current input alone, without
a body: features `[u(t)]` plus a constant. For independent inputs it cannot recall `u(t−k)`, so its
memory capacity is close to zero (only chance correlation on a finite test part). It is the lower bound
of what the body contributes.

## Checks

- **Trajectory, bit for bit across Linux, macOS and Windows.** The simulation uses only IEEE 754
  operations that are correctly rounded on every platform (elementwise `+ − × ÷` and `sqrt`, one per
  NumPy call), draws random numbers only through `Generator.random`, uses no transcendental functions,
  and adds the forces on each mass in a fixed order without library reductions. A test hashes
  (SHA-256) the lengths of a fixed-seed run and compares with a value stored in the test; CI runs it
  on all three systems.
- **Scores, within a tolerance across systems.** The readout uses linear algebra libraries (BLAS and
  LAPACK) that differ between systems and may round differently. Scores are compared with stored values
  with a relative tolerance of 1e-7. Reason: the features are standardised and the penalty keeps the
  solved system well conditioned, so rounding differences of order 1e-16 cannot grow beyond about
  1e-9; 1e-7 leaves a margin while still catching any real change.
- **Physics.** With no input, a network at rest stays exactly at rest; a network released from a
  displaced position comes to rest because of the damping.

## Results

(Added after the measurements.)
