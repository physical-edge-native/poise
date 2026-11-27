# How finely deformation must be sensed to see the mass-spring signals

Date: 2026-11-27. Issue: #35. Written by an AI assistant during a scheduled night run. This is a research
note. It measures physical quantities of the simulations only. **No task score was computed**, and nothing
here changes the measurements in `docs/design/`.

## Question

poise is to design soft parts for erg whose deformation is read out on microcontrollers
(pena-meta `decisions/2026-11-27-robot-repository-roles.md`). In the simulations, the readout sees spring
lengths exactly. A real sensor sees them with limited resolution. How small are the signals in the
simulated bodies, and what resolution would a sensor need just to resolve them?

This sets only a lower bound on the needed resolution. A real soft foot will deform by different amounts.
Sensor noise, drift and the analog front end are not modelled. Whether the readout still works with
coarse features is a separate question, and answering it needs task scores chosen before measuring.

## Method

Both networks (seed 1: the first network, and the network with the settings of Hauser et al. 2011 from
PR #29, commit `b96788e`) were driven by the task inputs at the scale used in the tasks (memory capacity:
uniform in [−1, 1], seed 2; NARMA2: uniform in [0, 0.5], seed 3). After the 200 discarded samples, the
**strain** of each spring was computed: (length − rest length) / rest length. Per spring, two quantities
were taken:

- its standard deviation, which is the size of the signal a readout can use;
- its range (maximum − minimum).

Quantising a signal with an ideal converter of step q adds noise with standard deviation q/√12. The
signal-to-quantisation-noise ratio (SNR) is the strain's standard deviation divided by that noise, in
decibels. Two full scales are considered:

- **own range**: each spring's converter spans exactly that spring's range. This is the best case, and it
  needs per-sensor gain and offset tuned to the motion;
- **common ±10 % strain**: every converter spans −10 % to +10 % strain. This is a plausible fixed design
  for a sensor that must not saturate. The largest strain range seen was 20 %, under the memory-capacity
  input in the Hauser-style network.

## Results

Strain standard deviation per spring (median over springs): first network 1.1e-3 (memory capacity) and
9.2e-4 (NARMA2); Hauser-style network 2.0e-3 and 1.3e-3. So a typical spring's length fluctuates by
about 0.1–0.2 %.

SNR in dB. "Median" is over springs; "worst" is the least-moving spring.

| Network | Input | Bits | Own range, median | Common ±10 %, median | Common ±10 %, worst |
|---|---|---|---|---|---|
| first | memory capacity | 8 | 43.8 | 14.1 | 0.7 |
| first | memory capacity | 12 | 67.9 | 38.2 | 24.8 |
| first | memory capacity | 16 | 92.0 | 62.2 | 48.9 |
| first | NARMA2 | 8 | 45.9 | 12.3 | −8.2 |
| first | NARMA2 | 12 | 70.0 | 36.3 | 15.9 |
| first | NARMA2 | 16 | 94.1 | 60.4 | 40.0 |
| Hauser settings | memory capacity | 8 | 45.2 | 18.9 | 1.6 |
| Hauser settings | memory capacity | 12 | 69.3 | 43.0 | 25.7 |
| Hauser settings | memory capacity | 16 | 93.4 | 67.1 | 49.8 |
| Hauser settings | NARMA2 | 8 | 44.6 | 15.5 | −7.6 |
| Hauser settings | NARMA2 | 12 | 68.7 | 39.6 | 16.5 |
| Hauser settings | NARMA2 | 16 | 92.7 | 63.7 | 40.6 |

Each extra bit adds 6 dB. With 10 bits every spring is above 0 dB in every case. With 8 bits and the common
full scale, six springs fall below 0 dB under the NARMA2 input in each network: their signal is smaller than
one step of the converter.

For the first network, the table leaves out three springs, explained below.

## Findings

1. **The signals are small: about 0.1 % strain.** Seen through a fixed full scale of ±10 % strain, a 12-bit
   converter (common on microcontrollers) gives a median SNR of 36–43 dB, and 16–26 dB for the least-moving
   springs. An 8-bit converter leaves some springs below one step. If a sensor can be ranged to each
   part's own motion, 8 bits already give about 44 dB.
2. **Most of the range is used by rare large deformations.** A typical spring's range is about 6 times its
   standard deviation, and the largest ranges are tens of times larger (#32 found single springs
   compressed by 3–11 %). A fixed full scale that avoids saturation therefore spends most of its steps on
   events that rarely happen.
3. **Three of the first network's 87 features never change.** The first network fixes the four masses with
   the smallest x (`docs/design/2026-11-26-mass-spring-tasks.md`), and three of its springs join two of
   these fixed masses. Their lengths are constant. The readout keeps them without scaling (`poise/readout.py`),
   so they do no harm, but the body has **84 useful features, not 87**. The delayed-input baseline D87 was
   sized to "the number of body features (87 springs)" (`docs/design/2026-11-27-delayed-input-baseline.md`),
   so it has three more useful features than the body. This is small next to the measured differences
   (memory capacity 5.74 against 30.00), but the records should say so. The network with the Hauser settings
   has no such springs: its two fixed masses (leftmost and rightmost) are not joined.
4. For a soft foot, these numbers suggest that a deformation sensor and converter should resolve about
   1e-4 strain (0.01 %) over a range of a few percent, about 9–10 bits of useful dynamic range above the
   noise, if a real foot deforms as little as these networks do. It is not known yet whether it does.

## Suggestions (not decisions)

- Record finding 3 in the mass-spring design records (an erratum line next to "87 springs"). One option is to
  leave springs between two fixed masses out of the network, but that would change the first network and its
  stored results, so it would need its own issue.
- A later measurement could add quantisation (and noise) to the features at a few bit depths fixed in advance,
  and report the task scores for each. This would show how much sensing resolution the readout actually needs.

## Script

```python
import numpy as np
from poise import massspring as m, tasks

for name, net in [("first", m.make_network(1)), ("hauser", m.make_hauser_network(1))]:
    for task, (lo, hi, seed) in {"MC": (-1, 1, 2), "NARMA2": (0, .5, 3)}.items():
        L = m.simulate(net, tasks.uniform_inputs(seed, lo, hi))[tasks.WASHOUT:]
        rel = (L - net.rest_length) / net.rest_length
        sd, span = rel.std(axis=0), rel.max(axis=0) - rel.min(axis=0)
        moving = span > 0  # three springs of the first network join two fixed masses
        for bits in (8, 10, 12, 16):
            own = 20 * np.log10(sd[moving] / (span[moving] / 2**bits / np.sqrt(12)))
            common = 20 * np.log10(sd[moving] / (0.2 / 2**bits / np.sqrt(12)))
            print(name, task, bits, np.median(own), np.median(common), common.min())
```
