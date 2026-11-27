# A second network with the settings of Hauser et al. (2011)

Date: 2026-11-27. Issue: #14. Decided by the maintainer on 2026-11-26 (build one network with that paper's
settings, measure it once with the same tasks and baselines). The details below were chosen by an AI
assistant during a scheduled night run, which also wrote this record. The setup was written and committed
**before** any task score of this network was computed; the results are added at the end.

## Why

The first network (`2026-11-26-mass-spring-tasks.md`) differs from the network of H. Hauser et al.,
"Towards a theoretical foundation for morphological computation with compliant bodies", *Biological
Cybernetics* 105:355–370 (2011), DOI 10.1007/s00422-012-0471-0, in how the springs are joined, how many
masses are fixed, and the ranges of the coefficients (table in `docs/research/2026-11-26-prior-work.md`).
On NARMA2 the first network did worse than a short window of past inputs
(`2026-11-27-delayed-input-baseline.md`). A second network built from that paper's settings shows how much
of this comes from the network itself rather than from the tasks and the measurement, which stay the same.

The network is taken from the paper, not chosen by its scores. Only one network is built (seed 1, as for
the first network), so this is not an optimisation of the body.

## Setup

Implemented as a second constructor, `make_hauser_network(seed)` in `poise/massspring.py`. It returns the
same kind of network as `make_network` and is simulated by the same `simulate`.

| Item | This network (from the paper) | First network (unchanged) |
|---|---|---|
| Masses | 30, 1 kg, uniform at random in the unit square | same |
| Springs | Delaunay triangulation of the masses | each mass to its 5 nearest |
| Fixed masses | 2: the one with the smallest x and the one with the largest x | 4 with the smallest x |
| `k1`, `d1` | log-uniform in [1, 100] | uniform, [1, 100] and [1, 10] |
| `k3`, `d3` | uniform in [100, 200] | uniform, [1, 200] and [1, 10] |
| Input masses | 20 % of the free masses (6 of 28), horizontal force, weight uniform in [−1, 1] | 20 % (5 of 26) |
| Integration | semi-implicit Euler, 1 ms, 20 steps per sample | same |
| State for the readout | length of every spring | same |

Choices that the paper does not settle, or that were not checked in it:

- **Where the masses are placed.** The size of the area in the paper was not checked; the unit square is
  kept so that only the listed items differ from the first network. A different area would change the
  rest lengths and the angles at which forces act, so this is a real difference if the paper used another
  size. *(Not checked against the paper.)*
- **Input weights.** Kept as in the first network (uniform in [−1, 1]); the paper's values were not checked.
- **Integration.** The paper uses 4th-order Runge–Kutta. Semi-implicit Euler is kept so that the
  integrator does not differ from the first network; with a 1 ms step and these coefficients the fastest
  mode moves by a small fraction of a period per step. The difference to the paper is stated, not removed.
- **Selection.** The paper picks the best of 400 random networks. This is not reproduced: selecting by
  score would optimise the body, which poise does not do.
- **Input signal.** The paper drives with a product of sines. poise's tasks and inputs are kept, because
  the aim is to compare networks under the same tasks.

### Delaunay triangulation without a new dependency

The triangulation is computed in poise, without SciPy. Random positions from `Generator.random` are exact
multiples of 2⁻⁵³, so they are scaled to Python integers and the geometric tests (orientation and
"inside the circle through three points") are computed **exactly** in integer arithmetic. Every triple of
masses that is not on one line and has no other mass strictly inside its circumscribed circle is a
triangle; the springs are the sides of these triangles. With 30 masses this checks 4060 triples and takes
well under a second. Exact arithmetic makes the result the same on every platform and free of rounding
mistakes; for points in general position it is the Delaunay triangulation (four masses on one circle have
probability zero and are detected by a test: the number of triangles must equal 2n − 2 − h, where h is
the number of masses on the convex hull).

### Log-uniform coefficients without a platform maths library

A log-uniform draw in [1, 100] is `10^(2r)` with `r` uniform in [0, 1). The exponential from the C library
(or NumPy) is not correctly rounded and may differ in the last bit between Linux, macOS and Windows, which
would break the bit-exact check of the trajectory. The power is therefore computed with elementwise
`+ − × ÷` only, in a fixed order: `x = 2r·ln 10`, then `exp(x) = (exp(x/16))^16`, with `exp(x/16)` from a
fixed number of terms of its Taylor series (Horner's rule) and four squarings. The result agrees with
`numpy.exp` to about 1e-14 relative (checked by a test), which is irrelevant for a random draw, and it is
the same bit for bit on every platform.

## Measurements

Exactly the tasks, inputs, seeds, split, readout and scores of `2026-11-26-mass-spring-tasks.md`: memory
capacity over delays 1–30 and NARMA2. They are reported next to the first network, the input-only
baseline and the delayed-input baselines already measured (D87, D-val, P3). The delayed-input baselines do
not depend on the body and are not measured again; D87 keeps its window of 87 inputs, so it no longer has
exactly as many features as the body (the new network has fewer springs; the count is reported).

Information processing capacity (#13) is measured for the first network in a separate pull request that
is not merged yet; for this network it is left to a follow-up once that code is on main.

## What is expected before measuring

- Fewer springs than the first network (a triangulation of 30 points has 87 − h edges, h ≥ 3 being the
  number of hull points), so slightly fewer features.
- Stronger damping (`d1` up to 100, `d3` 100–200) makes the trace of past inputs fade faster: memory
  capacity is expected to be **lower** than the first network's 5.74.
- Much stronger cubic springs and dampers may give more nonlinearity; whether that helps NARMA2 is open.
  Either outcome, including a worse result than the first network, is the result.

## Checks

- Network parameters and a 200-sample trajectory are hashed (SHA-256) and compared with stored values on
  Linux, macOS and Windows (bit for bit, same reasons as for the first network).
- Scores are compared with stored values with a relative tolerance of 1e-7 (same reason as before: the
  readout uses BLAS and LAPACK).
- The triangulation: number of triangles 2n − 2 − h, number of springs 3n − 3 − h, no two springs cross.
- Physics: at rest without input it stays exactly at rest; released from a displaced position it comes to
  rest; no floppy modes.
- The first network's hashes and scores do not change.

## Results

To be added after measuring.
