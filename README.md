<p align="center">
  <img src="https://raw.githubusercontent.com/Yeoh37/intex_wa510/main/logo.png" alt="Intex WA510 Water Analyzer" width="220">
</p>

# Intex WA510 Water Analyzer

Home Assistant custom integration for the **Intex WA510 / AGP SMART SENSOR T3U** via Tuya Cloud.

---

## Features

### Water monitoring

- pH
- ORP
- Water temperature
- Free chlorine
- Corrected free chlorine
- Battery level
- Error code monitoring

### Controls

- Force measurement refresh
- pH setpoint control
- ORP setpoint control

### Maintenance tracking

- Last cleaning date
- Days since cleaning
- Cleaning reminder
- Configurable cleaning interval
- Cleaning completed button

### Calibration tracking

- Last pH calibration date
- Last ORP calibration date
- Days since pH / ORP calibration
- Calibration reminders
- Configurable calibration intervals
- Calibration completed buttons

### Diagnostics

- Last real measurement timestamp
- Maintenance status
- Sensor indicators
- Calibration status

---

## Installation via HACS

1. Open HACS
2. Add this repository as a custom repository
3. Category: **Integration**
4. Install the integration
5. Restart Home Assistant
6. Add the integration from **Settings → Devices & Services**

Repository:

```text
https://github.com/Yeoh37/intex_wa510
```

---

## Configuration

You need Tuya IoT Platform credentials:

- Access ID / Client ID
- Access Secret / Client Secret
- Device ID

The WA510 device must already be linked to your Tuya / Intex account.

For Europe, the default endpoint is:

```text
https://openapi.tuyaeu.com
```

---

## Supported device

### Intex WA510

Also sold as:

- AGP SMART SENSOR T3U

---

## Entities

### Main sensors

- pH
- ORP
- Water temperature
- Free chlorine
- Corrected free chlorine
- Battery level

### Binary sensors

- Maintenance required
- Cleaning required
- pH calibration required
- ORP calibration required
- Low battery

### Number entities

- pH setpoint
- ORP setpoint
- Cleaning interval
- pH calibration interval
- ORP calibration interval

### Buttons

- Refresh measurement
- Cleaning completed
- pH calibration completed
- ORP calibration completed

### Diagnostic entities

- Last real measurement timestamp
- Error code
- Maintenance status
- pH indicator
- ORP indicator
- Chlorine indicator
- Calibration status

---

## Important notes

The calibration command buttons exposed by Tuya are experimental.

Do not launch a calibration unless you are actually performing the official calibration procedure described in the Intex documentation.

This project is experimental and is not affiliated with Intex, AGP, Tuya, or Home Assistant.

---

## Changelog

### v0.6.0

Clean public release:
- clean GitHub / HACS package structure
- manifest version set to 0.6.0
- README image uses GitHub raw URL for HACS
- logo.png and icon.png included at repository root and in the integration folder
- maintenance and calibration entities kept from v0.5.x
- duplicated unavailable setpoint / threshold sensors removed
- Tuya `off` indicator values translated to clearer statuses
