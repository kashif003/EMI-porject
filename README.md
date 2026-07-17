# EMI Project — IMU + BLE RSSI Indoor Localization with a Particle Filter

A university project (Embedded Intelligence course, OTH Amberg-Weiden) that performs **indoor localization** by fusing **IMU sensor data** (accelerometer, gyroscope, magnetometer from an Arduino Nano 33 BLE Sense) with **BLE RSSI-based distance estimation**, feeding both into a custom **particle filter** to track a person's position and heading as they walk through a mapped indoor space.

**Authors:** Nitesh Ramesh Morem, Kashif Riyaz (MAI, OTH Amberg-Weiden)

## What it does

1. **Data collection** (`logger.py`) — connects to an Arduino Nano 33 BLE Sense over Bluetooth Low Energy using `bleak`, streaming live accelerometer/gyroscope/magnetometer readings (via the BMI270/BMM150 IMU) plus RSSI readings from nearby BLE beacons, and logs everything to CSV.
2. **Sensor fusion / heading estimation** (`sensorprocessing.ipynb`, and reproduced in `main.ipynb`):
   - Computes a magnetometer-based compass heading (`arctan2` on the horizontal magnetic field).
   - Adds tilt compensation using accelerometer-derived pitch/roll.
   - Computes a gyroscope-integrated heading (yaw) from angular velocity.
   - Combines both with a **complementary filter** (98% gyro / 2% magnetometer) to get a heading that resists gyro drift while staying responsive to fast turns.
3. **RSSI → distance conversion** (`rssi_model.ipynb`):
   - Calibrates a **log-distance path-loss model** from RSSI readings at a known reference distance.
   - Converts live RSSI values from two BLE beacons into estimated distances, and cross-checks the distance trends against known heading-change events for sanity-checking.
4. **Step detection** — a custom hybrid peak-detection function (`hybrid_step_detection`) finds footstep events in the accelerometer magnitude signal (threshold + minimum time interval + prominence), used to advance the particle filter by a fixed step length per detected step.
5. **Particle filter localization** (in `main.ipynb`):
   - `Particle` — represents one position/heading hypothesis, with a `move()` step that advances it using the estimated step length + heading (with noise), rejecting moves that land outside the mapped walkable area (checked via a polygon mask built with OpenCV).
   - `ParticleFilter` — manages the full particle population: initializes particles around a known start point, moves them all on each detected step, reweights them based on how well their implied distances-to-beacons match the RSSI-derived distances, resamples based on weight, and estimates final position as the (weighted) average of surviving particles.
   - Visualized live with **Pygame**, rendering the estimated path against the map.
6. **Ablation comparisons** — the project explicitly compares three configurations to show what each signal source contributes:
   - With map constraints + RSSI (best — converges closely to ground truth)
   - With map, without RSSI
   - Without any map constraint
   - (Recorded as `.mp4` demo videos — see below)

## Repository structure

```
EMI-porject/
├── README.md / ReadMe.txt          # Project docs (submission notes: team, file listing)
├── logger.py                        # BLE data logger (connects to Arduino Nano 33 BLE Sense, records IMU + RSSI to CSV)
├── main.ipynb                       # Main notebook: heading fusion, step detection, particle filter, Pygame visualization
├── sensorprocessing.ipynb           # Magnetometer/gyro/complementary-filter heading derivation (standalone deep-dive)
├── rssi_model.ipynb                 # RSSI → distance path-loss model calibration and validation
├── imu.csv                          # Raw logged IMU data
├── imu_updated.csv                  # IMU data with derived heading columns (from main.ipynb)
├── rssi.csv                         # Raw logged RSSI data
├── WITH_MAP+RSSI.mp4                # Demo: particle filter with map constraints + RSSI
├── WITHOUT_RSSI.mp4                 # Demo: particle filter with map, without RSSI
└── WITHOUT_MAP_CONSTRAINTS.mp4       # Demo: particle filter without any map boundary constraint
```

## Requirements

- Python packages (used across the notebooks and `logger.py`):
  - `pandas`, `numpy`, `matplotlib`, `scipy` (peak detection via `find_peaks`)
  - `opencv-python` (`cv2`) — for building the map polygon mask
  - `pygame` — for the live particle filter visualization
  - `bleak` — for BLE communication with the Arduino in `logger.py`
- Hardware (only needed to *record new data*, not to reprocess the included CSVs): an Arduino Nano 33 BLE Sense running firmware that streams IMU + RSSI data over a custom BLE characteristic.

## Getting started

1. **Install dependencies**
   ```bash
   pip install pandas matplotlib scipy pygame numpy opencv-python bleak
   ```
2. **(Optional) Record new data** — flash the Arduino with compatible firmware, update the target device name and BLE UUIDs in `logger.py`, then run:
   ```bash
   python logger.py
   ```
3. **Reprocess/explore the included data** — open `main.ipynb` (uses the provided `imu.csv` and `rssi.csv`), or dig into `sensorprocessing.ipynb` and `rssi_model.ipynb` for the heading-fusion and RSSI-calibration derivations respectively.
4. **Watch the demo videos** (`.mp4` files) to see the particle filter converge under the three tested configurations.

## Suggested new repo names

The current name (`EMI-porject`) has a typo and is generic — "EMI" mainly signals the course name, not what the project actually does. Some more descriptive alternatives:

- `imu-rssi-indoor-localization`
- `ble-particle-filter-localization`
- `indoor-positioning-imu-fusion`
- `step-heading-particle-filter`
- `imu-ble-indoor-tracker`

Any of these would make the repo self-explanatory from the name alone (and fix the "porject" typo along the way).
