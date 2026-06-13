<p align="center">
  <img src="https://raw.githubusercontent.com/Yeoh37/intex_wa510/main/logo.png" width="220">
</p>

# Intex WA510 Water Analyzer

Home Assistant custom integration for the **Intex WA510 / AGP SMART SENSOR T3U** via Tuya Cloud.

---

## Features

### Water Monitoring
- pH sensor
- ORP sensor
- Water temperature
- Free chlorine
- Corrected free chlorine
- Battery level
- Error code monitoring

### Controls
- Force measurement refresh
- ORP setpoint control
- pH setpoint control

### Maintenance Tracking
- Last cleaning date
- Days since cleaning
- Cleaning reminder
- Configurable cleaning interval

### Calibration Tracking
- Last pH calibration date
- Last ORP calibration date
- Days since calibration
- Calibration reminders
- Configurable calibration intervals

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

```
https://github.com/Yeoh37/intex_wa510
```

---

## Configuration

You will need:

### Tuya IoT Platform

- Access ID
- Access Secret
- Device ID

The device must already be linked to your Tuya account.

---

## Supported Device

### Intex WA510

Also sold as:

- AGP SMART SENSOR T3U

---

## Entities

### Sensors

- pH
- ORP
- Water temperature
- Free chlorine
- Corrected free chlorine
- Battery level
- Last measurement timestamp

### Binary Sensors

- Calibration required
- Cleaning required
- Maintenance required
- Low battery

### Numbers

- pH setpoint
- ORP setpoint
- Cleaning interval
- Calibration interval

### Buttons

- Refresh measurement
- Cleaning completed
- pH calibration completed
- ORP calibration completed

---

## Notes

The calibration command buttons exposed by Tuya are experimental.

Do not launch a calibration unless you are actually performing the official calibration procedure described in the Intex documentation.

---

## Version

### v0.5.2

- Fixed HACS logo display
- Improved configuration structure
- Improved calibration tracking
- Improved maintenance tracking
- Cleaner diagnostics section
- Translation improvements
