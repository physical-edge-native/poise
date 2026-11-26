# Prior work on soft and compliant bodies as reservoirs

Date: 2026-11-26. Issue: #11. Written with an AI assistant. The main papers below were read in full
text; bibliographic details (volume, pages, DOI) were checked with Crossref. Statements marked
*(not checked)* come only from abstracts or secondary sources. Statements marked *(our reading)* are
inferences for poise, not findings of the papers.

## Where poise's network comes from

H. Hauser, A. J. Ijspeert, R. M. Füchslin, R. Pfeifer, W. Maass, "Towards a theoretical foundation
for morphological computation with compliant bodies", *Biological Cybernetics* 105(5–6), 355–370
(2011), DOI [10.1007/s00422-012-0471-0](https://doi.org/10.1007/s00422-012-0471-0). (The DOI says
2012 because the paper appeared online in January 2012.)

The paper argues, from Boyd and Chua's result on fading-memory operators and Volterra series, that a
sufficiently diverse compliant body with a linear readout can emulate complex nonlinear filters
(Sect. 2). Its setup, compared with poise (paper: Sect. 4, pp. 363–367):

| Item | Hauser et al. 2011 | poise (`docs/design/2026-11-26-mass-spring-tasks.md`) |
|---|---|---|
| Masses | 30 | 30 |
| Springs | 78, Delaunay triangulation (no crossings) | 87, each mass joined to its 5 nearest (may cross) |
| Spring and damper law | `k1·x + k3·x³`, `d1·v + d3·v³` | same form |
| Fixed masses | 2 (leftmost and rightmost) | 4 (smallest x) |
| Input masses | 20 % per input, horizontal force | 5 masses (about 17 %), horizontal force |
| Input weights | uniform in [−1, 1] | uniform in [−1, 1] |
| `k1`, `d1` | log-uniform in [1, 100] | `k1` uniform in [1, 100], `d1` uniform in [1, 10] |
| `k3`, `d3` | uniform in [100, 200] | `k3` uniform in [1, 200], `d3` uniform in [1, 10] |
| Integration | 4th-order Runge–Kutta, 1 ms | semi-implicit Euler, 1 ms |
| Input signal | product of three sines (deterministic) | random values held for 20 steps |
| Readout | spring lengths, pseudo-inverse | spring lengths, ridge regression |
| Network | best of 400 random networks | one network (seed 1), not selected |
| Baseline without body | linear regression on the current input and a constant | same |

poise's damping and cubic coefficients are much smaller than the paper's. *(Our reading:)* this may
make poise's network behave more linearly, which would fit its large memory capacity and small gain
on NARMA2.

The follow-up, H. Hauser et al., "The role of feedback in morphological computation with compliant
bodies", *Biological Cybernetics* 106(10), 595–613 (2012), DOI
[10.1007/s00422-012-0516-4](https://doi.org/10.1007/s00422-012-0516-4), shows that tasks beyond fading
memory, such as generating limit cycles, need feedback from the readout to the body, and that feedback
is sufficient (abstract, p. 595). Only the readout weights are trained; input and feedback weights are
random and fixed; training uses teacher forcing (Sect. 5.3). poise's current scope (open-loop readout)
lies inside the limit this paper draws.

## Soft bodies

- K. Nakajima et al., "A soft body as a reservoir: case studies in a dynamic model of
  octopus-inspired soft robotic arm", *Frontiers in Computational Neuroscience* 7:91 (2013), DOI
  [10.3389/fncom.2013.00091](https://doi.org/10.3389/fncom.2013.00091): a simulated arm of 20 segments;
  the lengths of 80 longitudinal springs are the state; 4th-order Runge–Kutta with a 0.01 step; the
  baseline is a linear regression on the current input; closed-loop limit cycles are embedded.
- K. Nakajima, T. Li, H. Hauser, R. Pfeifer, "Exploiting short-term memory in soft body dynamics as a
  computational resource", *J. R. Soc. Interface* 11(100):20140437 (2014), DOI
  [10.1098/rsif.2014.0437](https://doi.org/10.1098/rsif.2014.0437) (read in the arXiv version
  1406.4929): a physical silicone arm in water; timer, closed-loop square wave, short-term memory and
  parity tasks. It compares with logistic regression on the current input and with echo state
  networks (software reservoirs) of 10 nodes, the size of the sensor set. The best network did better
  on short-term memory (capacity 4.59 ± 0.58 against 2.50 ± 0.08 for the arm) and equally on parity.
- K. Nakajima, H. Hauser, T. Li, R. Pfeifer, "Information processing via physical soft body",
  *Scientific Reports* 5:10487 (2015), DOI [10.1038/srep10487](https://doi.org/10.1038/srep10487):
  10 bend sensors in a silicone arm; input is a product of sines with amplitude 0.2; NARMA2, 5, 10, 15
  and 20. Its baseline uses the current input and a constant only. Its error is normalised by the sum
  of squared targets, not by their variance. It also compares with leaky echo state networks of 10
  nodes on the same data; the best of them did better than the arm on all tasks. No memory capacity
  task, no closed loop in this paper.
- Other bodies: tensegrity structures (Caluwaerts et al., *Artificial Life* 19(1):35–66, 2013, DOI
  10.1162/ARTL_a_00080; *J. R. Soc. Interface* 11(98):20140520, 2014, DOI 10.1098/rsif.2014.0520),
  a quadruped's silicone spine (Zhao et al., IROS 2013, DOI 10.1109/IROS.2013.6696539), a pneumatic
  arm (Eder, Hisch, Hauser, *Advanced Robotics* 32(7):375–385, 2018, DOI 10.1080/01691864.2017.1402703),
  origami (Bhovad and Li, *Scientific Reports* 11:13002, 2021, DOI 10.1038/s41598-021-92257-1), and
  mass-spring locomotion (Urbain et al., *Frontiers in Neurorobotics* 11:16, 2017, DOI
  10.3389/fnbot.2017.00016). Contents of Caluwaerts 2013, Zhao 2013 and Eder 2018 *(not checked)*.
- Since about 2018, most new work uses soft bodies for sensing (bending angle, payload) rather than
  closed-loop control; most of it is preprints *(mostly not checked)*.

## Measures

- **Memory capacity**: the sum over delays of the squared correlation between a past input and its
  linear reconstruction. For independent inputs it cannot exceed the number of linearly independent
  state variables *(bound: not checked in a primary source)*.
- **Information processing capacity**: J. Dambre, D. Verstraeten, B. Schrauwen, S. Massar,
  "Information processing capacity of dynamical systems", *Scientific Reports* 2:514 (2012), DOI
  [10.1038/srep00514](https://doi.org/10.1038/srep00514). Capacities for products of Legendre
  polynomials of past inputs (uniform input in [−1, 1]); the total is bounded by the number of
  linearly independent state variables; the first order is memory capacity; higher orders are
  nonlinear capacity. Thresholds against finite-data bias are set per system; the paper uses about
  10⁶ steps.
- **NARMA2**: the "second-order system" `y(t+1) = 0.4 y(t) + 0.4 y(t) y(t−1) + 0.6 u(t)³ + 0.1`
  (A. F. Atiya, A. G. Parlos, *IEEE Trans. Neural Networks* 11(3):697–709, 2000, DOI
  10.1109/72.846741; original text *not checked*) is often called NARMA2, but some papers use the
  N = 2 member of the general NARMA-N family under the same name (arXiv:2405.06561; arXiv:2610.16432).
  Input signals (random uniform in [0, 0.5], uniform in [0, 1], products of sines) and error
  normalisation (variance or sum of squares) also differ. **Published NARMA2 errors cannot be compared
  with poise's numbers**; comparisons are made inside poise, with the same definition for all
  baselines.

## Baselines in the literature

Every soft-body paper read uses a linear regression on the current input (and a constant) as the
"no body" baseline; Nakajima 2014 and 2015 also compare with echo state networks. **No soft-body work
was found that compares with a linear readout on a window of past inputs, or that reports information
processing capacity.** *(Our reading:)* with an input-only baseline, any body with memory wins memory
tasks almost by construction, so poise adds a delayed-input baseline (#12) and measures information
processing capacity (#13).

## Simulators

The papers read used their own simulators (custom mass-spring code; NTRT for tensegrity). For the
soft arm, MuJoCo (from its documentation sources and code, `google-deepmind/mujoco`, commit 1652af95):

- Soft bodies are built with `flex` and `flexcomp`. Version 4.0.0 (2026-11-06) removed the `composite`
  element and the cable plugin; 1D `flexcomp` replaces them. Several 2026 releases changed model
  behaviour (elastic constants, shear), and 4.0.1 (2026-11-11) fixed a sparse factorisation error in
  4.0.0. Flex elasticity needs `integrator="discrete"`.
- MuJoCo is deterministic, but bit-exact results are guaranteed only for the same version and the same
  architecture; x86 and ARM use different vectorised code paths. FMA is disabled by default.
- The Python package `mujoco-core` 4.0.1 has wheels for CPython 3.11–3.15 on Linux (x86-64, aarch64),
  macOS (arm64) and Windows (amd64); none for macOS x86-64.

poise pins MuJoCo and decides how to check reproducibility before the soft arm (#15).

## Not checked

Atiya and Parlos's original text (the input range of the second-order system); the contents of
Caluwaerts 2013, Zhao 2013, Eder 2018 and Müller and Hoffmann 2017 ("What is morphological
computation?", *Artificial Life* 23(1):1–24, DOI 10.1162/ARTL_a_00219); supplementary tables
(e.g. Nakajima 2015, Table S1); most preprints from 2024–2026.
