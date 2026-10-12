# Himshikhar NILM ESP32: Edge Energy Meter & Digital Twin

[![ESP32](https://img.shields.io/badge/Hardware-ESP32--WROOM--32-blue.svg)](https://www.espressif.com/)
[![MATLAB/Simulink](https://img.shields.io/badge/Digital%20Twin-MATLAB%2FSimulink%20R2026a-orange.svg)](https://www.mathworks.com/)
[![Firmware](https://img.shields.io/badge/Firmware-C%2B%2B%20Arduino-brightgreen.svg)](firmware/esp32_nilm_meter.ino)
[![Paper PDF](https://img.shields.io/badge/Paper-IEEE%20Transactions%20PDF-red.svg)](docs/Manit_Sharma_IEEE_Transactions_NILM_Paper.pdf)
[![Status](https://img.shields.io/badge/Verification-100%25%20PASS-success.svg)](simulink/verify_nilm_model.m)
[![Author](https://img.shields.io/badge/Author-Manit%20Sharma-purple.svg)](https://github.com/manttii)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0000--1988--6487-green.svg)](https://orcid.org/0009-0000-1988-6487)

A high-accuracy, edge-computed **Non-Intrusive Load Monitoring (NILM)** Energy Meter engineered from discrete analog principles. This repository contains the complete C++ embedded firmware for ESP32, the MATLAB/Simulink digital twin simulation, circuit schematics, and mathematical derivations for AC phase angle resolution, temporal waveform locking, dynamic DC bias tracking, and appliance load disaggregation.

---

## 1. System Overview

Standard commercial smart plugs and power monitors employ dedicated metering ICs (e.g., ADE7758, BL0937, or HLW8012) that abstract away analog signal processing, phase shifts, and waveform dynamics. This project reconstructs energy metering directly from first physical principles:

- **Edge Signal Conditioning:** Interfacing a **ZMPT101B** micro active AC voltage transformer and an **SCT-013** non-invasive split-core current transformer clamp into the ESP32 12-bit SAR ADC.
- **100ms Temporal Waveform Locking:** Real-time discrete integration locked synchronously to integer cycles (5 full cycles of 50 Hz AC).
- **Dynamic DC Midpoint Tracking:** Hardware-adaptive auto-zero calibration and running exponential filtering that eliminates the common **~3.5A phantom current bug** without masking real loads.
- **On-Chip & Simulink NILM Disaggregation:** Heuristic and model-based signature extraction separating purely resistive, inductive motor, and complex reactive loads using active power ($P$), apparent power ($S$), power factor ($PF$), and phase angle ($\theta$).
- **Integrated Telemetry Portal:** Built-in responsive web dashboard (Chart.js), JSON REST API, and SoftAP Wi-Fi provisioning.

![Breadboard Hardware Setup](hardware/breadboard_setup.png)
*Figure 1: Physical hardware setup with ESP32 DevKit, ZMPT101B transformer, and SCT-013 current clamp conditioning circuit.*

---

## 2. Mathematical Foundations & Derivations

### 2.1 The 100ms Temporal Lock Window ($5 \text{ Cycles at } 50\text{Hz}$)

In AC systems, discrete calculation of Root Mean Square (RMS) voltage, current, and active power requires integrating over an exact integer multiple of the fundamental grid period $T$.

For a standard $50\text{ Hz}$ utility grid:
$$T = \frac{1}{f} = \frac{1}{50\text{ Hz}} = 0.020\text{ s} = 20\text{ ms}$$

If an arbitrary sampling window duration $T_w$ is used (e.g., non-synchronized $83\text{ ms}$):
$$\int_{0}^{T_w} \sin^2(\omega t) dt = \frac{T_w}{2} - \frac{\sin(2\omega T_w)}{4\omega}$$

The second term introduces a non-zero, time-varying truncation error (spectral leakage) that artificially fluctuates the computed RMS value from sample to sample.

By locking the firmware sampling window to **exactly $100\text{ ms}$** ($100,000\text{ }\mu\text{s}$):
$$\frac{T_w}{T} = \frac{100\text{ ms}}{20\text{ ms}} = 5.0\text{ integer cycles}$$

Over $N = 5$ full periods, the sinusoidal harmonic integral satisfies:
$$\int_{0}^{5T} \sin(2\omega t) dt \equiv 0 \implies \int_{0}^{5T} \sin^2(\omega t) dt = \frac{5T}{2}$$

This guarantees exact orthogonality, eliminating truncation jitter and enabling deterministic discrete integration.

---

### 2.2 Discrete RMS & Instantaneous Integration

Let $v_{inst}[n]$ and $i_{inst}[n]$ represent instantaneous, DC-subtracted voltage and current samples acquired across $N$ discrete ADC conversions during the 100ms lock:

$$v_{inst}[n] = \text{ADC}_V[n] - V_{\text{offset}}$$
$$i_{inst}[n] = \text{ADC}_I[n] - I_{\text{offset}}$$

The true RMS values are computed using discrete numerical integration:
$$V_{RMS} = \sqrt{\frac{1}{N} \sum_{n=1}^{N} v_{inst}^2[n]} \times \left(\frac{3.3}{4095}\right) \times K_V$$
$$I_{RMS} = \sqrt{\frac{1}{N} \sum_{n=1}^{N} i_{inst}^2[n]} \times \left(\frac{3.3}{4095}\right) \times K_I$$

Where:
- $3.3 / 4095 \approx 0.00080586\text{ V/count}$ converts 12-bit ADC integers into physical pin voltages.
- `VOLTAGE_CAL` and `CURRENT_CAL` are the physical sensor scaling gains (VOLTAGE_CAL, CURRENT_CAL).

---

### 2.3 Mathematical Derivation of Calibration Factors

#### A. Voltage Calibration (`VOLTAGE_CAL` = 883.58)
1. Nominal grid voltage: $V_{\text{RMS}} = 230.0\text{ V}$ (peak value $V_{pk} = 230 \times \sqrt{2} \approx 325.27\text{ V}$).
2. The ZMPT101B active module steps down the $230\text{V}$ AC signal through a micro transformer ($2\text{mA}:2\text{mA}$) and conditions it via an LM358 inverting amplifier.
3. The feedback trimpot is adjusted to yield an AC voltage swing of $0.26028\text{ V RMS}$ ($0.736\text{ V peak-to-peak}$) around the $1.65\text{V}$ midpoint:

   $V_{\text{pin, RMS}} = 0.26028\text{ V}$

4. Setting up the transfer relationship:

   $V_{\text{RMS}} = V_{\text{pin, RMS}} \times K_V \implies 230.0 = 0.26028 \times K_V$

   $K_V = \frac{230.0}{0.26028} = \mathbf{883.58}$

#### B. Current Calibration (`CURRENT_CAL` = 100.0)
1. The SCT-013-000 current transformer features a turns ratio of $N_p : N_s = 1 : 2000$.
2. At rated $100\text{A RMS}$ primary current, the secondary winding produces:

   $I_s = \frac{100\text{A}}{2000} = 50\text{ mA RMS}$

3. The secondary coil drives a burden resistor network calibrated to produce a normalized sensitivity of $1.0\text{ V RMS}$ at $100\text{A RMS}$ line current:

   $\text{Sensitivity} = \frac{100.0\text{ A}}{1.0\text{ V}} = \mathbf{100.0\text{ A/V}}$

   (This corresponds to an effective burden of $R_b = \frac{1.0\text{V}}{0.050\text{A}} = 20.0\,\Omega$, or $33\,\Omega$ with appropriate software scaling).
4. Substituting into the firmware formulation:

   $I_{\text{RMS}} = V_{\text{pin, RMS}} \times K_I \implies K_I = 100.0$

---

### 2.4 Active Power, Apparent Power, Polarity & Phase Angle ($\theta$)

Real active power ($P$) is the discrete time average of the instantaneous voltage-current product:
$$P = \left(\frac{1}{N} \sum_{n=1}^{N} v_{inst}[n] \cdot i_{inst}[n]\right) \times \left(\frac{3.3}{4095}\right)^2 \times K_V \times K_I$$

Apparent power ($S$) represents total volt-amperes:
$$S = V_{RMS} \times I_{RMS}$$

**CT Polarity Auto-Correction:** If the physical split-core clamp is clipped backwards on the wire, $v(t) \cdot i(t)$ produces a negative active power ($P < 0$). The firmware auto-detects this inverted polarity, takes the active power magnitude ($\lvert P \rvert$), and flags `ct_reversed = true` without disrupting power factor calculation or NILM disaggregation:

$$\text{Power Factor } PF = \frac{\lvert P \rvert}{S} \quad (\text{clamped to } [0.0, 1.0] \text{ when } S > 5.0\text{ VA})$$
$$\theta = \arccos(PF) \times \left(\frac{180^\circ}{\pi}\right)$$

---

## 3. The 3.5A Phantom Current Diagnosis & Solution

### 3.1 Root Cause: 43-Count DC Offset Drift
Standard amateur implementations hardcode a fixed midpoint offset:
```cpp
float current_offset = 1760.0; // Hardcoded static bias
```

Under physical bench conditions, resistor tolerances (5% film), USB supply sag ($3.24\text{V}$ instead of $3.30\text{V}$), and ESP32 SAR ADC non-linearities shift the actual physical resting midpoint to **$\approx 1803$ counts**.

$$\Delta \text{ADC} = 1803.0 - 1760.0 = +43.0\text{ counts}$$

When no current flows ($0.0\text{A}$ idle), the firmware integrates this constant 43-count discrepancy:
$$I_{RMS} = 43.0 \times \left(\frac{3.3}{4095}\right) \times 100.0 = 43.0 \times 0.00080586 \times 100.0 \approx \mathbf{3.47\text{ A}}$$

Because $3.47\text{A}$ is significantly higher than the standard $0.8\text{A}$ noise gate, the meter continuously displays **~3.5A phantom current** at idle.

### 3.2 Dual-Layer Mitigation Architecture
This firmware implements an intelligent two-tier auto-tracking engine:

1. **Integer-Cycle Boot Auto-Calibration (200ms Lock):** In `setup()`, the ESP32 samples continuously over an exact **$200,000\text{ }\mu\text{s}$ window** ($10$ full cycles of $50\text{ Hz}$ AC) under zero-load conditions. Because $\int_0^{10T} \sin(\omega t + \phi) dt \equiv 0$, any AC mains signal integrates to exactly zero with $0.000$ counts harmonic leakage, locking true DC bias:

   $I_{\text{offset}} = \frac{1}{M} \sum_{k=1}^{M} \text{ADC}_I[k] \approx 1803.2\text{ counts}$

2. **Dynamic Integer-Cycle Tracking (EMA):** Because the $100\text{ ms}$ temporal lock window spans exactly $5$ complete AC cycles, the fundamental sinusoidal current averages to zero ($\int_0^{5T} i(t) dt = 0$). Any non-zero mean over the window represents physical DC bias, updated recursively:

   $\bar{I}\_{\text{window}} = \frac{1}{N} \sum\_{n=1}^{N} \text{ADC}\_I[n]$

   $I_{\text{offset}}[k] = 0.95 \cdot I_{\text{offset}}[k-1] + 0.05 \cdot \bar{I}_{\text{window}}$

3. **Double-Precision Accumulation & Adaptive Noise Gate:** 64-bit IEEE `double` precision is used during summation to prevent integer truncation bias on small sub-count signals. Residual thermal jitter ($\le 2\text{ counts} \approx 0.16\text{A}$) is eliminated via a low-profile noise gate:

   $\text{If } I_{RMS} < 0.25\text{ A} \implies I_{RMS} = 0.00\text{ A}$

**Result:** Idle current drops cleanly to **$0.00\text{ A}$**, while real loads above $0.3\text{A}$ are captured with high linear fidelity.

---

## 4. Appliance Signatures & NILM Disaggregation

Non-Intrusive Load Monitoring (NILM) determines individual appliance activation without distributed per-plug submeters. Appliances exhibit distinct electrical vectors in the $(P, Q, PF, \theta)$ feature space:

| Appliance | Rated Power ($P$) | Character | Power Factor ($PF$) | Phase Lag ($\theta$) | Rated $I_{RMS}$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Appliance 1: Water Heater** | $1000\text{ W}$ | Pure Resistive ($R$) | **$1.00$** | **$0.0^\circ$** | $4.35\text{ A}$ |
| **Appliance 2: Refrigerator Motor** | $350\text{ W}$ | Inductive Motor ($R-L$) | **$0.72\text{ lag}$** | **$43.9^\circ$** | $2.11\text{ A}$ |
| **Appliance 3: Microwave Oven** | $800\text{ W}$ | Complex Reactive ($R-L$) | **$0.88\text{ lag}$** | **$28.4^\circ$** | $3.95\text{ A}$ |

### Simulink Digital Twin Verification Benchmarks
The MATLAB/Simulink digital twin (`NILM_Himshikhar_Portal.slx`) simulates the grid, appliances, sensor transfer functions, 12-bit ADC quantization, and the discrete firmware subsystem:

```text
======================================================================
  HIMSHIKHAR 2026 ENERGY PORTAL - NILM SIMULATION VERIFICATION
======================================================================
  [PASS] 1. Idle / Standby (No Load)    => V: 230.0V | I: 0.00A | P:     0W | PF: 1.00
  [PASS] 2. Appliance 1: 1000W Heater   => V: 230.0V | I: 4.35A | P:  1001W | PF: 1.00
  [PASS] 3. Appliance 2: Fridge Motor   => V: 230.0V | I: 2.11A | P:   349W | PF: 0.72
  [PASS] 4. Appliance 3: Microwave      => V: 230.0V | I: 3.95A | P:   801W | PF: 0.88
  [PASS] 5. Combined: Heater + Motor    => V: 230.0V | I: 6.04A | P:  1348W | PF: 0.97
  [PASS] 6. Combined: All Appliances    => V: 230.0V | I: 9.92A | P:  2148W | PF: 0.94
======================================================================
  >>> 100% OF ALL NILM APPLIANCE LOAD SIGNATURES VERIFIED! <<<
======================================================================
```

---

## 5. Repository Structure

```
Himshikhar-NILM-ESP32/
├── docs/
│   ├── NILM_ACADEMIC_RESEARCH_PAPER.md    # Full academic research paper (SIRED-2026 benchmark & ESP32 edge adaptation)
│   └── TIER_2_ENGINEERING_WHITEPAPER.md   # Publication-ready engineering whitepaper
├── firmware/
│   └── esp32_nilm_meter.ino               # Production ESP32 C++ firmware
├── hardware/
│   ├── breadboard_setup.png               # Physical prototype photograph
│   └── pinout_and_schematic.md            # Complete BOM, circuit theory & pinout
├── simulink/
│   ├── build_nilm_simulator.m             # Programmatic Simulink model builder
│   ├── NILM_Himshikhar_Portal.slx         # Simulink digital twin model
│   ├── open_nilm_project.m                # Interactive project launcher
│   └── verify_nilm_model.m                # Automated 6-state test verification harness
└── README.md                              # Technical documentation & derivations
```

---

## 6. Quickstart Guide

### 6.1 Hardware Wiring
Refer to [hardware/pinout_and_schematic.md](hardware/pinout_and_schematic.md) for full circuit diagrams.
- Connect ZMPT101B `OUT` $\to$ **GPIO 34**.
- Connect SCT-013 biased audio jack $\to$ **GPIO 35**.
- Power ESP32 via Micro-USB/Type-C.

### 6.2 Flashing the Firmware
1. Open [firmware/esp32_nilm_meter.ino](firmware/esp32_nilm_meter.ino) in Arduino IDE or PlatformIO.
2. Select Board: **ESP32 Dev Module**.
3. Flash the firmware (`Upload`).
4. On first boot, connect your phone or laptop to the Wi-Fi AP: **`Himshikhar_Config`**.
5. Navigate to `http://192.168.4.1`, select your home Wi-Fi SSID, enter the password, and click **Save & Connect**.
6. The ESP32 will reboot, connect to your router, and serve live telemetry at its assigned local IP address!

### 6.3 Running the Simulink Digital Twin
1. Open MATLAB R2026a (or compatible version).
2. Set your working directory to the `simulink/` folder.
3. Run the interactive verification test harness:
   ```matlab
   verify_nilm_model
   ```
4. To open the interactive model:
   ```matlab
   open_nilm_project
   ```

---

## 7. Author & Academic Context

- **Author:** Manit Sharma ([@manttii](https://github.com/manttii))
- **ORCID:** [0009-0000-1988-6487](https://orcid.org/0009-0000-1988-6487)
- **Program:** B.Tech Electronics & Communication Engineering (ECE), 3rd Semester
- **Institution:** Graphic Era Deemed to be University, Dehradun, India
- **Academic Research Paper:** Formatted in IEEE Transactions layout, available in Markdown at [docs/NILM_ACADEMIC_RESEARCH_PAPER.md](docs/NILM_ACADEMIC_RESEARCH_PAPER.md) and as a compiled publication-ready PDF at [docs/Manit_Sharma_IEEE_Transactions_NILM_Paper.pdf](docs/Manit_Sharma_IEEE_Transactions_NILM_Paper.pdf).
- **Tier 2 Engineering Whitepaper:** Available in [docs/TIER_2_ENGINEERING_WHITEPAPER.md](docs/TIER_2_ENGINEERING_WHITEPAPER.md).
