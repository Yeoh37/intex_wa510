# Intex WA510 Water Analyzer

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue.svg)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Version](https://img.shields.io/badge/version-v0.6.2-green.svg)](https://github.com/Yeoh37/intex_wa510)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Home Assistant custom integration for the **Intex WA510 / AGP SMART SENSOR T3U** pool water analyzer using the **Tuya Cloud API**.

---

## Features

- 🌡 Water temperature
- 🧪 pH monitoring
- ⚡ ORP (Redox) monitoring
- 💧 Free chlorine monitoring
- 📊 Corrected free chlorine calculation
- 🔋 Battery level
- 🔔 Maintenance reminders
- 🔄 Manual measurement refresh button
- 📱 Home Assistant Companion compatible
- 🏊 Dedicated pool dashboard compatible

---

## Prerequisites

Before installing the integration:

1. Pair the analyzer with **Tuya Smart** or **Smart Life**
2. Verify that measurements are visible in the mobile application
3. Create a Tuya IoT Cloud project
4. Link your application account to the cloud project

---

## Installation with HACS

### Add Custom Repository

Repository URL:

```text
https://github.com/Yeoh37/intex_wa510
```

Category:

```text
Integration
```

### Install

1. HACS → Integrations
2. Custom repositories
3. Add repository
4. Install Intex WA510 Water Analyzer
5. Restart Home Assistant
6. Add Integration

---

## Tuya Cloud Configuration

Create a project:

https://iot.tuya.com

You will need:

- Access ID
- Access Secret
- Device ID

---

## Finding Your Device ID

### Method 1 – Tuya IoT Platform

- Open Cloud → Devices
- Select your WA510
- Copy Device ID

### Method 2 – Tuya Smart App

- Device details
- Device information
- Virtual ID

---

## Entities Created

### Sensors

- Water Temperature
- pH
- ORP
- Free Chlorine
- Corrected Free Chlorine
- Battery
- Maintenance Status

### Binary Sensors

- Maintenance Required
- Calibration Required
- Low Battery

### Buttons

- Refresh Measurement

---

## Typical Values

### pH

| Value | Status |
|---------|---------|
| 7.0 - 7.4 | Ideal |
| 7.4 - 7.6 | Good |
| > 7.8 | Too High |
| < 6.8 | Too Low |

### Free Chlorine

| Value | Status |
|---------|---------|
| 1 - 3 ppm | Ideal |
| < 1 ppm | Insufficient |
| > 5 ppm | Excessive |

### ORP

| Value | Status |
|---------|---------|
| 650 - 750 mV | Ideal |
| < 600 mV | Weak disinfection |
| > 800 mV | Strong oxidation |

---

# Support the Project ☕

This integration is developed and maintained during my free time.

If it helps you manage your pool, saves you time, or simply makes your Home Assistant setup better, consider supporting the project.

Your support helps me:

- Fix bugs faster
- Maintain compatibility with future Home Assistant releases
- Add new features
- Purchase hardware for testing
- Keep the integration free and open-source

## Buy Me a Coffee

👉 https://buymeacoffee.com/yeoh37

Any support is greatly appreciated ❤️

---

## Reporting Issues

Please include:

- Home Assistant version
- Integration version
- Error logs
- Screenshots when possible

GitHub Issues:

https://github.com/Yeoh37/intex_wa510/issues

---

## Roadmap

- Improved diagnostics
- Enhanced chlorine calculations
- Dashboard examples
- HACS default repository submission
- Additional pool chemistry indicators

---

## Disclaimer

This project is an independent community-developed integration.

It is not affiliated with:

- Intex
- AGP
- Tuya
- Smart Life
- Home Assistant
- Nabu Casa

This software is provided **"AS IS"**, without warranty of any kind.

The author shall not be held responsible for:

- Incorrect measurements
- Water chemistry interpretation errors
- Pool treatment decisions
- Chemical dosage calculations
- Equipment damage
- Property damage
- Data loss
- Service interruptions
- Direct or indirect damages resulting from the use of this integration

Users remain solely responsible for verifying water quality and maintaining their pool according to manufacturer recommendations.

This integration is intended as an informational tool only and must not replace proper water testing procedures.

**Use at your own risk.**

---

## Author

**Yeoh37**

GitHub:
https://github.com/Yeoh37/intex_wa510

Support:
https://buymeacoffee.com/yeoh37
