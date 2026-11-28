# Prior work on legged robots: bodies as computation, soft feet, local feedback

Date: 2026-11-27. Issue: #20. Written with an AI assistant.
Each statement carries the level at which it was checked: *(full text)* means the paper itself was
read; *(abstract)* means only the abstract or publisher page; *(bibliography only)* means only the
title, authors and DOI were checked (with Crossref); *(search snippet)* means only a search-engine
summary or an unreachable author copy; *(secondary)* means another paper's description of it.
Statements marked *(inference)* are our reading for poise, not findings of the cited papers.
Literature was searched up to November 2026. IEEE Xplore and several author repositories could not be
reached, so some key papers were checked only through abstracts or reviews (see "Not checked").

## Summary

Prior work answers the three questions unevenly.

1. **Body as computation on legged hardware is thin.** Physical reservoir computing means using a
   physical system's own dynamics as the "reservoir" and training only a linear map (the *readout*)
   from its measured states to an output. Morphological computation is the broader idea that the
   body's shape and material take over part of the control. Only one legged robot was found that
   closed a gait loop through a soft body with a trained linear readout on hardware (the quadruped
   "Kitty", 2013), and it could be checked only through a 2026 review. The one hardware study that
   tested whether a compliant quadruped's body *computes* (HyQ, 2021) concluded that the benefit of
   compliance could **not** be attributed to the body's intrinsic computation *(abstract)*.
2. **Soft, sensorised feet work on hardware, but as sensors with conventional models.** Barometers
   (air-pressure sensors) cast in rubber have measured force, centre of pressure, edges and slip on
   real legs and quadrupeds. The readouts were calibration polynomials, classifiers or a recurrent
   neural network, never a test of the foot as a reservoir.
3. **Decentralised control through local load feedback is shown on small hardware robots.**
   Per-leg oscillators driven only by each foot's load sensor produced coordinated gaits and gait
   transitions on 1.6–2.4 kg robots. The bodies were compliant, but no study removed the compliance
   to measure what it contributed.

No paper found compares a soft legged body or a soft foot against a *delay line* (a readout on a
window of past sensor values) or against an input-only readout. That is the comparison that decided
poise's own mass–spring results.

## Main works at a glance

"HW" = hardware. "Not verified" means the field could not be checked at the stated level.

| Work | Robot / soft part | HW or simulation (what exactly on HW) | Sensors | Readout output | Baselines | Checked at |
|---|---|---|---|---|---|---|
| Zhao et al., IROS 2013, DOI 10.1109/IROS.2013.6696539 | Quadruped "Kitty", spine of soft silicone blocks | HW: trot, bound, turn by switching readout weights | Force sensors in spine (32 FSR400 per a snippet, not verified) | 4 motor commands, loop closed through the body | Not verified | Bibliography + secondary (2026 review) |
| Caluwaerts et al., Artif. Life 19(1):35–66, 2013, DOI 10.1162/ARTL_a_00080 | Tensegrity (not legged) | Simulation | Not verified | Periodic gait signals, linear feedback | Not verified | Abstract |
| Caluwaerts et al., J. R. Soc. Interface 11, 2014, DOI 10.1098/rsif.2014.0520 | Six-bar tensegrity "ReCTeR" | HW prototype used to validate the simulator; readout gait on HW not verified | Not verified | Not verified | Not verified | Bibliography + search snippet |
| Degrave et al., IROS 2015, pp. 4486–4491 | Oncilla quadruped, compliant pantograph legs | Oncilla named; HW vs simulation split not verified | 8 rotary encoders | Trot motor signals | Linear feedback (failed) vs nonlinear memory-less feedback (stable trot) | Abstract |
| Urbain et al., Front. Neurorobot. 11:16, 2017, DOI 10.3389/fnbot.2017.00016 | 2-D mass–spring–damper networks, 3–26 nodes | Simulation only | Node accelerations, 3-step buffer | Next-step actuation, closed loop | Open-loop controller only | Full text |
| Vandesompele et al., arXiv 2004.04560 | Simulated Tigrillo quadruped + software spiking reservoir | Simulation only | 4 passive-joint angles | 4 motor signals | None for the body alone | Full text (skimmed) |
| Urbain et al., Auton. Robots 45:421–434, 2021, DOI 10.1007/s10514-021-09974-9 | HyQ hydraulic quadruped, controller-set compliance | Simulation and HyQ experiments | Ground reaction forces | Joint positions and velocities (end-to-end network) | Compliance levels | Abstract |
| Terajima et al., arXiv 2507.21496 (Chaos 35(8):083111) | Six-bar tensegrity (not legged) | Simulation only (MuJoCo) | 24 tendon lengths and velocities | 2 motor signals, closed loop | None (no input-only, delay, ESN) | Full text (skimmed) |
| Tomioka et al., arXiv 2503.05601 | 2-D mass–spring–damper bodies, body co-optimised | Simulation only | Spring lengths | Classification, NARMA-type, locomotion | Body shapes, linear vs MLP brain | Full text (skimmed) |
| Yamaguchi et al., arXiv 2608.05684 | Amoeba-inspired 4-legged walker | HW, on-board microcontroller | 3-axis accelerometer + 8 foot pressure sensors | Flat vs rough ground | Accelerometer only vs all sensors | Full text (skimmed) |
| Ruppert & Badri-Spröwitz, FootTile, arXiv 2005.09025 | Polyurethane dome with air bubble over a barometer | HW: leg sliding on a rail, force plate reference | MPL115A2 barometer, 330 Hz | Force (3rd-order polynomial), centre of pressure | Force plate, pressure plate | Full text |
| Tyler et al., arXiv 2304.09370 | Cassie-scale foot, barometer pads | HW on a test machine (pressing, not walking) | 8 BMP390, accelerometer, acoustic, capacitive | 10-class terrain | Several classifiers | Full text |
| Van Hauwermeiren et al., RA-L 9(7):6368–6375, 2024, DOI 10.1109/LRA.2024.3405378 | Barometer array in rubber sphere | HW on Unitree Go1 | Barometers | No contact / flat / edge, edge orientation | Go1's stock foot force sensor | Bibliography + search snippet |
| Liu et al., SlipSense, arXiv 2606.24350 | Two-hardness silicone foot, 45 mm, 65 g | HW on Unitree Go1 (trotting) | 8 MEMS pressure sensors + IMU, 1 kHz | 3-axis force (LSTM), slip | Foot-velocity kinematic slip detector | Full text |
| Wu et al., DogLegs, arXiv 2503.04580 | Rigid leg, IMU near foot | HW on Unitree Go2 | Leg IMU (ICM-20602), 200 Hz | Contact (likelihood-ratio test) | Go2 foot-force threshold | Full text |
| Owaki et al., J. R. Soc. Interface 10:20120669, 2013, DOI 10.1098/rsif.2012.0669 | 1.6 kg quadruped, spring backbone | HW | Foot load per leg | Per-leg oscillator phase | None centralised | Full text |
| Owaki & Ishiguro, Sci. Rep. 7:277, 2017, DOI 10.1038/s41598-017-00348-9 | 2.0 kg quadruped Oscillex 3 | HW on treadmill: walk, trot, gallop | FSR400 foot load | Per-leg oscillator phase | None centralised | Full text |
| Owaki et al., Front. Neurorobot. 11:29, 2017, DOI 10.3389/fnbot.2017.00029 | 2.4 kg hexapod, leg springs | HW on treadmill | 3-axis foot force sensors | Per-leg oscillator phase | Own-leg load only vs with neighbours' load | Full text |
| Spröwitz et al., Oncilla, Front. Robot. AI 5:67, 2018, DOI 10.3389/frobt.2018.00067 | 5.1 kg quadruped, spring-loaded legs | HW, open-loop gaits | Force sensors fitted, not used | None (open loop) | None | Full text |
| Sartoretti et al., arXiv 1901.08537 | Hexapod | HW, per-leg policies learned online | Not extracted | Per-leg actions | Centralised learner | Full text |

## Bodies as computation

**Kitty (Zhao et al. 2013)** is the only legged hardware example found of a soft body used as a
reservoir with a trained linear readout in closed loop. According to a 2026 review, a linear readout
mapped "the internal force and strain of the flexible spine into four control commands"; it was
trained open-loop with *teacher forcing* (feeding the target instead of the readout's own output),
then the loop was closed, and the robot could trot, bound or turn "simply by switching the readout
weights" *(secondary: Wang et al., Nat. Commun. 17:2455, 2026,
https://www.nature.com/articles/s41467-026-70866-6)*. Sensor count, sampling rate, baselines and
numbers could not be checked.

**Simulation studies** are more detailed but stay in simulation. Urbain et al. (2017) trained a
readout on accelerations of 3–26-node mass–spring–damper networks to reproduce an open-loop gait,
then closed the loop *(full text)*. Their only reference was the open-loop controller; networks with
fewer than 6 nodes gave non-significant results even in open loop *(full text)*. The readout input
was already a buffer of the last three acceleration samples, so the result is "body plus a short
delay line", not the body alone *(inference)*. Terajima et al. (2025) embedded two behaviours in one
ridge-regression readout of a simulated tensegrity in MuJoCo; closed loop was sometimes unstable
*(full text, skimmed)*. Tomioka et al. (2025) co-optimised body and readout by gradient, which is
outside poise's scope (poise does not optimise the body) *(full text, skimmed)*. Ridge regression is
linear least squares with a penalty on weight size.

**Tests of whether the body computes** are few, and point the same way as poise's own results.
Degrave et al. (2015) found on the moderately compliant Oncilla quadruped that linear feedback from
8 joint encoders was **not sufficient** for a stable trot; a memory-less nonlinear feedback was
*(abstract)*. Urbain et al. (2021) varied compliance on HyQ in simulation and experiments and found
"better controllability using less memory and computational resources when increasing compliance.
However, we show empirically that this effect cannot be attributed to the ability of the body to
perform intrinsic computation" *(abstract; method not read)*.

**Terrain sensing with reservoir computing on legged robots** exists, but the reservoir is software.
An *echo state network* (ESN: a fixed random recurrent neural network with a trained linear readout)
running on a microcontroller classified flat vs rough ground on a 4-legged walker: one-step accuracy
54 % from the accelerometer alone, 82 % with all sensors, up to 97 % on average with multi-step
history *(full text, skimmed: arXiv 2608.05684)*. Earlier work used reservoir computing on joint
angles and foot force for terrain *(secondary / abstract only)*. **No soft foot used as a physical
reservoir on a legged robot was found.**

## Soft and sensorised feet

**Barometers in rubber** come from Tenzer, Jentoft and Howe, IEEE Robot. Autom. Mag. 21(3):89–95,
2014, DOI 10.1109/MRA.2014.2310152 *(bibliography only; reported linearity under 1 % and noise under
0.01 N from search snippets)*. A plain overmolded sensor saturates near 5 N *(secondary, via
FootTile)*. Foot-scale loads need a design change:

- **FootTile** puts a 6 mm air bubble in a polyurethane dome. Range 25–35 N, sampled at 330 Hz,
  under 10 EUR and about 0.9 g per sensor. Output is nonlinear in force and was fitted with a
  3rd-order polynomial. On a leg sliding on a rail, mean force error was under 1 N against a force
  plate and centre-of-pressure error under 4 mm. It survived hopping in liquid mud *(full text)*.
- **SlipSense** potted 8 MEMS pressure sensors in Shore 40A silicone under a Shore 30A outer layer,
  with an IMU (inertial measurement unit: accelerometer and gyroscope) in the middle; 65 g against the
  stock 51 g Go1 foot, sampled at 1 kHz, deployed while trotting on Go1. A recurrent network (LSTM)
  over a 50 ms window estimated 3-axis force; the authors argue static models struggle at high force
  because of hysteresis and stress relaxation of the elastomer. Slip detection: 85.9 % accuracy at
  24.1 ± 6.4 mm average displacement, better than a foot-velocity baseline *(full text)*.
- **Van Hauwermeiren et al. (2024)** put a barometer array in a rubber sphere on Go1 and classified
  no contact, flat contact and edges, compared with Go1's stock foot force sensor; withstood repeated
  impacts of at least 40 N *(bibliography only + search snippet)*.
- **Tyler et al. (2023)** pressed a barometer-padded foot into 10 terrains on a test machine (not
  walking). Random forest reached 99.90 %; a support vector machine (SVM) was worst at 59.15 %, which
  the authors attribute to linear one-vs-rest separation. Accelerometer and barometer features
  mattered most. Raw barometer data drifted linearly over time and was detrended *(full text)*.

**Simpler contact sensing** also works. DogLegs detected contact on Go2 from an approximately
3 US dollar IMU near each foot at 200 Hz, with qualitatively fewer false positives than Go2's
foot-force threshold (no rates given) *(full text)*. A one-piece printed capacitive foot
(TPU and conductive PLA) responded with 16.6 ms average delay relative to a commercial sensor
*(abstract: Bao et al., Eng. Res. Express 8:115518, 2026, DOI 10.1088/2631-8695/ae7539)*.

**Larger robots** use expensive force/torque sensors: ANYmal's sensorised feet measured local slope
and contact force (Valsecchi et al., RA-L 5(2):1548–1555, 2020, DOI 10.1109/LRA.2020.2969160)
*(bibliography only + search snippet)*. Small-robot capacitive feet with an SVM reached 82.5 % on
4 terrains *(search snippet)*. Terrain classifiers in general use per-step hand-made features and
nonlinear classifiers; Spot reached about 95 % on hardware with k-nearest neighbours on 0.5 s windows
at 16.7 Hz *(full text: arXiv 2508.16504)*.

**Mechanical effects of soft feet on small robots** were not quantified in reachable sources. A MuJoCo
model of the SoftFoot, validated against bench tests, exists for a humanoid in simulation
*(abstract and introduction: arXiv 2412.03191)*. One 2018 dog-like robot found its silicone feet too
soft to carry the weight *(search snippet)*. Durability is a known weakness: a piezo strain-gauge foot
sensor lasted about 8 min *(secondary, via arXiv 2008.05240)*, and SlipSense cites fragility as a key
bottleneck of added foot sensors *(full text)*.

## Decentralised local feedback

**Load-driven oscillators per leg** ("Tegotae", Owaki, Ishiguro and colleagues) are the clearest
hardware evidence. Each leg has a phase oscillator, `dφ/dt = ω − σ·N·cos φ`, where `N` is that
foot's measured load; there are no connections between oscillators. Legs coordinate through the body:
a leg still carrying load late in stance is delayed until another leg takes the load *(full text)*.

- On a 1.6 kg quadruped with a spring backbone, adding 0.12–0.29 kg to the fore or hind legs changed
  the gait without informing the controller *(full text, 2013)*.
- On the 2.0 kg Oscillex 3 (one DC motor per leg, FSR400 foot sensors, one mbed microcontroller),
  changing only `ω` produced walk, trot and gallop on a treadmill; cost of transport was measured
  *(full text, 2017)*.
- On a 2.4 kg hexapod (2 servos per leg, 2.9 N/mm leg springs, 3-axis foot force sensors), using
  only the leg's own load failed to give insect-like gaits in 7 of 10 trials; adding neighbours' load
  gave 10/10 *(full text, 2017)*.

The load signal was used continuously, not as an on/off threshold *(full text)*. None of these
papers ran a stiff-body control condition *(full text, as far as read)*.

**Compliance without feedback** is a separate result. Oncilla (5.1 kg, spring-loaded legs) ran all
shown gaits open loop: trot at 0.55 m/s average, slopes up to 10° *(full text)*. Cheetah-cub (about
1 kg) self-stabilised under an open-loop controller and passed step-downs of up to 20 % of leg length
with 80–20 % success *(abstract: IJRR 32:932–950, 2013, DOI 10.1177/0278364913489205)*. The Oncilla
paper also states a design trade-off: sensors at the foot give clean contact force but add distal
mass and must survive impacts *(full text)*.

**Learned per-leg policies** are mostly simulation. On hardware, Sartoretti et al. learned per-leg
policies online on a hexapod in about 45 min, where a centralised learner showed no improvement after
more than 3 h *(full text)*. Zhang et al. (ICRA 2024) coupled each oscillator to its own leg's force in
simulation on Mini Cheetah; the policy itself was centralised, hardware was preliminary video only,
and the authors call simulated contact forces "highly inaccurate" *(full text: arXiv 2402.08662)*.

## What has been shown on hardware / What has not been shown

### Shown on hardware

| Claim | Evidence | Checked at |
|---|---|---|
| A soft spine with a linear readout can close a gait loop and switch gaits | Kitty, 2013 | Secondary only |
| Compliance can improve controllability, but not through intrinsic computation | HyQ, 2021 | Abstract |
| Linear feedback from joint encoders is not enough on a compliant quadruped | Oncilla, 2015 | Abstract; HW/simulation split unclear |
| A software ESN on a microcontroller classifies ground type from foot pressure and acceleration | Amoeba-inspired walker, 2026 | Full text (skimmed) |
| Barometer-in-rubber feet measure force (under 1 N error) and centre of pressure | FootTile, leg on rail | Full text |
| Barometer-type feet detect slip and estimate 3-axis force while trotting (with an LSTM, 1 kHz) | SlipSense on Go1 | Full text |
| A barometer sphere foot classifies edges | Go1, 2024 | Search snippet |
| A cheap leg IMU detects contact | DogLegs on Go2 | Full text |
| Local foot-load feedback alone coordinates legs on small quadrupeds | Owaki 2013, 2017 | Full text |
| On a hexapod, neighbours' load is also needed | Owaki 2017 | Full text |
| Leg compliance stabilises open-loop gaits | Oncilla, Cheetah-cub | Full text / abstract |

### Not shown (not found in this search)

"Not found" means not found within this search, not that it does not exist.

- A **soft foot used as a physical reservoir** on a legged robot, in hardware or in simulation.
- Any legged or locomotion body-reservoir study that compares against an **input-only readout, a
  delay line of the same signals, or a matched-size ESN**. All locomotion body-reservoir results
  except Kitty are simulation only.
- A **linear readout on raw sensor time series** for foot terrain classification. The closest
  linear model (SVM, one-vs-rest) was the worst classifier, on a press rig, not walking.
- **Barometer foot vs microswitch**: accuracy or latency of contact detection.
- **Quantitative impact, energy or wear data** for soft pads on small (under 5 kg) quadrupeds, and
  cycle life of a barometer foot during walking.
- The **same decentralised controller on a compliant vs a stiff body**.
- How much information about **other legs' loads** reaches one foot's local sensors through the body.
- Fully per-leg learned policies with only local observations on a **cheap quadruped**, 2024–2026.

## Implications for poise's soft foot (all inference)

poise plans a soft silicone foot for erg, a separate low-cost open-source quadruped (servo-driven
legs, one microcontroller and IMU per leg, 50 Hz control, current foot a rigid sphere with a
microswitch). The foot would hold 1–4 barometers cast in silicone and one accelerometer, read first by
a linear (ridge) readout for contact state, contact timing and foot load, later ground type. It is
studied as a single leg in MuJoCo first. The following are our readings, not findings of the papers.

1. **The delay line is the baseline that matters.** In poise's mass–spring network, memory capacity
   (how many past input steps a linear readout can recover) was 5.74 against 30 for a delay line;
   on NARMA2 (a standard nonlinear benchmark), normalised mean squared error was 0.347 against 0.153
   for a 9-tap delay line and 0.004 for cubic features of a 6-tap window; information processing
   capacity was mostly linear (degree 1: 9.2, degree 2: 2.0, degree 3: about 0; total 11.2 of 87).
   Prior locomotion work never ran this comparison, and Urbain 2017's readout already contained a
   delay buffer. With HyQ 2021 and Degrave 2015 pointing the same way, a small computational
   contribution from the foot is a plausible outcome and would be a valid result.
2. **Mechanical and computational benefits must be measured separately.** Oncilla and Cheetah-cub
   show compliance helping with no computation at all. A rigid foot, a soft foot read by its
   sensors, and the same soft foot read through a delay line separate the two effects.
3. **Load is the most useful first target.** The decentralised-feedback hardware work used a
   continuous load signal; a cheap FSR was enough. A soft foot must beat a plain load or contact
   sensor (the microswitch baseline) to be worth its complexity.
4. **Range and hysteresis shape the sensor design.** A barometer under solid silicone saturates near
   5 N; an air bubble (FootTile) sets range. Elastomer hysteresis and stress relaxation will bias a
   readout of instantaneous pressure, especially when unloading. A readout over a short window of
   past pressures tests whether memory (from the delay line or from the silicone) fixes this.
5. **Drift is expected.** Barometer data drifted on the Cassie foot; temperature sensitivity rises
   when silicone is bonded to the sensor *(search snippet)*. Each swing phase unloads the foot and
   gives a free zero reference.
6. **Sampling faster than control may matter.** The literature sampled at 200 Hz–1 kHz for contact
   and slip. Sampling inside the leg's microcontroller faster than 50 Hz and feeding a short window
   to the readout is the natural experiment.
7. **Ground type is the hardest target for a linear readout.** Published terrain classifiers are
   nonlinear; polynomial features are the fair intermediate baseline.
8. **Foot mass matters at the leg tip.** FootTile-type domes weigh about 1 g; SlipSense weighs 65 g.
9. **Simulation contact is a known weak point.** Contact forces in simulators have been called
   inaccurate (in IsaacGym), and a validated MuJoCo soft-foot model exists only at humanoid scale.
   Single-leg MuJoCo results should state this limit.
10. **One measurable open question:** whether one foot's signals carry information about other legs'
    loads. The hexapod result says such information matters for decentralised control.

## Not checked

- Zhao et al. 2013 (Kitty): full text unreachable; sensor count, rate, baselines and limitations
  unknown. The "32 FSR400" figure is from a search snippet only.
- Degrave et al. 2015: whether the stable trot ran on the physical robot; network details.
- Caluwaerts et al. 2013 and 2014: specific results.
- Urbain et al. 2021 (HyQ): how "intrinsic computation" was tested (paywalled).
- Tenzer et al. 2014: hysteresis, temperature and durability numbers; exact barometer part.
- Chuah & Kim, IEEE Sensors J. 14(5):1693–1703, 2014, DOI 10.1109/JSEN.2014.2299805, and Catalano et
  al., IEEE T-RO 38(1):302–316, 2022, DOI 10.1109/TRO.2021.3088060: probably contain impact and
  durability data; not read.
- Van Hauwermeiren et al. 2024: barometer part, accuracy, sampling rate.
- Walknet (Cruse et al., Neural Networks 11:1435–1447, 1998, DOI 10.1016/S0893-6080(98)00067-7)
  and Tekken (Fukuoka et al., IJRR 22(3–4):187–202, 2003, DOI 10.1177/0278364903022003004):
  bibliography only.
- Iida's "Puppy" robots: not searched.
- Material choices (casting silicones, TPU wear, adhesion, strain relief): no primary sources found;
  manufacturer datasheets not consulted.
