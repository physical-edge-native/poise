# A soft foot for erg, read as a physical reservoir

Date: 2026-11-27. Issue: #21. Decided by the maintainer on 2026-11-27, who chose the option marked "chosen" at
each decision below (the one the assistant had proposed); this record was written with an AI assistant.
Literature cited here as "to check" has not been read in full text yet; it is covered by the research issue
#20, and this record is updated with its findings.

## Question

Can a soft part attached to erg's four-legged robot (Issue and frame records in erg) be read by a linear
readout on the leg's own microcontroller, so that the body's physical response supplies information the leg
controller would otherwise have to compute or could not sense? And separately: does the soft part help
mechanically (impact absorption, stability) even without a readout?

This connects poise to the Physical-Edge Native Architecture's direction for robots: part of the computation
for the policy is done by the body and by a group of cheap microcontrollers, without a GPU and without
cameras.

## Constraints (from the maintainer, 2026-11-27)

- December 2026 to February 2027: research and design only; **no parts are bought**.
- The attachment can be added to erg later; **erg's robot is not changed from poise**. Anything that needs a
  change to erg is written as a draft proposal to pena-meta.
- Cheap to build; no cameras.

## What erg provides today (erg main, 6035d85)

- 12 joints (Feetech STS3215 serial servos reporting position, speed, load), one ESP32-class
  microcontroller (XIAO ESP32S3) and one IMU per leg, no body computer, 50 Hz control.
- Thigh and shank 90 mm each, PLA frame; the foot is a 12 mm sphere with an Omron SS-5GLD microswitch
  inside it as the contact sensor.
- Per-leg policies run as Dyne's `mlp-actor` (small ReLU networks, bit-exact between Python and the
  microcontroller); legs exchange 13 values per step with neighbours.

## Decision 1: where the soft part goes

| Option | What | For | Against |
|---|---|---|---|
| **A. Soft foot (chosen)** | Replace the 12 mm sphere with a soft foot (cast silicone, or printed TPU) with sensors inside | Smallest change to erg (one end part per leg); the foot is where impacts and contact happen, so its deformation carries what the controller needs (contact timing, load, slip, ground type); the microswitch's on/off signal is the weakest sensor erg has | Small volume for sensors; wear |
| B. Soft lower shank | A compliant segment (TPU beam or silicone) between knee and foot, with strain or IMU sensing | Larger deformation and slower dynamics, closer to the soft-arm work (more memory); series elasticity absorbs impact | Changes the leg's kinematics and the policy's model; bigger change to erg |
| C. Soft link between torso and legs or a soft spine | Compliant mounts or a spine, as in the spine-driven quadruped (Zhao et al. 2013) | The case with the clearest prior hardware result | Redesigns erg's torso; not "added later" |

**Decided: A**, then B as a later step if A shows a readable signal. Reason: A is the only option that
can be swapped in without changing erg's frame or its trained model's kinematics much, and it upgrades the
weakest sensor (a binary switch).

## Decision 2: how the soft part is sensed (cheap, no camera)

| Option | Sensor | Approx. cost per foot | Notes |
|---|---|---|---|
| **2a. Barometric pressure sensors cast in silicone (chosen)** | 1–4 MEMS barometers (e.g. BMP280 / BMP390 class) embedded in the silicone; digital (I2C/SPI), no ADC needed | a few hundred yen each (to check) | A known way to make cheap tactile sensors (to check: the "TakkTile" line of work); gives pressure, i.e. contact force and its distribution, at hundreds of Hz |
| 2b. Accelerometer in the foot | a small IMU or accelerometer in the foot | about ¥1,000 | Reads impacts and vibration directly; the foot's ringing after touch-down is the reservoir's response |
| 2c. Resistive sensors | conductive rubber cord, Velostat, flex sensors | from ¥100 (DIY) to ¥1,500 each | Cheap but drift and vary between pieces (cost estimate, 2026-11-27) |
| 2d. Piezo film | piezoelectric film or disc | a few hundred yen | Fast, reads changes only; needs an analogue front end |

**Decided: 2a with one 2b**: barometers for slow load and its distribution, one accelerometer for fast
impacts. Both are digital, so no extra ADC is needed on the XIAO ESP32S3. The servos' load readings and the
leg IMU that erg already has are used as additional features at no extra cost.

## Decision 3: what the readout produces

The readout is linear (ridge regression), trained offline, as everywhere in poise. Candidate targets, all
measurable in simulation and later on the bench without cameras:

1. **Contact state and contact time** (replace the microswitch): target from the simulator's contact force.
2. **Normal load on the foot** (continuous): target from the simulator.
3. **Slip** (tangential motion of the foot while loaded).
4. **Ground type** (hard, soft, rough) from the touch-down transient.
5. **A feature vector for the leg controller**: the readout's output is fed as extra inputs to erg's per-leg
   policy (closed loop through the policy, not directly to the servos).

**Decided:** start with **1–2** (they have clear ground truth and a direct use in erg), then 4. Item 5 is
the PENA-relevant end goal and needs erg's training pipeline, so it becomes a proposal to pena-meta once 1–2
work in simulation.

## Decision 4: where the readout runs

| Option | For | Against |
|---|---|---|
| **4a. As a Dyne component on the leg's microcontroller (chosen, later)** | Same toolchain as erg's policy (`.dynm` model file, `mlp-actor`, bit-exact between Python and the microcontroller); a linear readout is a one-layer network | Makes poise depend on Dyne (a pinned commit; currently poise has no Dyne dependency, decided 2026-11-25) |
| 4b. Plain C or MicroPython in erg's firmware | No new dependency for poise | A second way of running models on erg; no bit-exact check |

**Decided: 4a**, but only after the simulation shows a useful readout; the dependency is added in its
own issue with a pinned commit, following the cross-repository rules. The readout's output then travels to
the leg's policy inside the microcontroller, not over the network.

## Decision 5: how it is studied in December–February (no parts)

1. Pin MuJoCo (#15) and model a soft foot (flexcomp, 2D or 3D) on a single leg on a test stand in MuJoCo,
   using erg's leg dimensions (copied values with the erg commit they come from; poise does not import erg's
   code). Sensors are modelled as pressures and accelerations read from the soft body.
2. Drive the leg with recorded or scripted foot trajectories (touch-downs on different grounds, pushes).
3. Measure the readout's targets (Decision 3) against the baselines below.
4. Only then a whole-robot model, which needs erg's model file: proposed to pena-meta, because it creates a
   dependency of poise on erg (a pinned commit, a new row in `contracts.md`).

## Measures: what "better" would mean

Every comparison uses the same robot, the same sensors where possible, the same training budget, and is
written down before measuring. Two kinds of benefit are kept apart:

**Mechanical benefit (the soft part without a readout)** — rigid sphere foot vs soft foot, same controller:

- peak acceleration of the leg IMU and of the torso at touch-down;
- peak servo load and its rate of change at touch-down (stress on the servos);
- body attitude: standard deviation of roll and pitch while walking; falls per minute;
- recovery after a push: time until roll and pitch return within a band; largest push survived;
- speed tracking error at commanded speeds (erg's existing measure).

**Computational benefit (the readout)** — the same soft foot, read in different ways:

- contact detection: delay from the true touch-down to detection, false detections per minute;
- load estimate: normalised error of the foot's normal force;
- slip and ground type: detection rate and false alarms;
- when fed to the policy: the walking measures above with and without the readout's output.

**Baselines for the computational benefit** (lesson of #12: a weak baseline makes the body look good):

1. erg's microswitch alone;
2. the same raw sensor signals with a delay line (a window of past samples) and the same linear readout;
3. the same, with polynomial features;
4. a rigid foot with the same sensors (where they can be mounted).

The soft foot's computational benefit is only claimed where it beats 2 and 3, not just 1. No claim of
superiority over other approaches; measured differences, including no benefit, are the result.

**Cost and computation** — parts per foot; readout parameters and microcontroller time per step; extra bytes
per message if the output is shared with neighbours.

## Changes that need erg or pena-meta

- erg: a foot part that accepts the soft foot, sensor wiring along the shank, firmware reading the sensors →
  draft proposal to pena-meta (and then erg issues), not changes made from poise.
- poise depending on Dyne (Decision 4a) and on erg's model (Decision 5, step 4) → new pinned commits in
  `contracts.md`, proposed to pena-meta.
- poise's scope record and CLAUDE.md were updated in #21: hardware design is in scope (no purchases until the
  end of February 2027), and a dependency on Dyne may be added later in its own issue.

Drafts of the pena-meta proposals are handed to the maintainer, who decides when to file them.

## Open points for the research (#20)

- Which of these have been shown on hardware with legged robots, and with which baselines (#20).
- Whether barometer-in-silicone feet have been used on small legged robots, and their durability.
- Typical touch-down transient times relative to erg's 20 ms control period (the readout may need a faster
  sampling rate than the policy).
