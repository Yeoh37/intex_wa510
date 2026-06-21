<p align="center">
  <img src="https://raw.githubusercontent.com/Yeoh37/intex_wa510/main/logo.png" alt="Intex WA510 Water Analyzer" width="220">
</p>

# Intex WA510 Water Analyzer

Home Assistant custom integration for the **Intex WA510 / AGP SMART SENSOR T3U** via Tuya Cloud.

## v0.6.3

Branding support release:
- added `custom_components/intex_wa510/brand/icon.png`
- added `custom_components/intex_wa510/brand/logo.png`
- kept icon/logo at repository root and integration root
- manifest version set to 0.6.2
- device presentation kept as **Analyseur Piscine**

## Features

- pH / ORP monitoring
- Water temperature
- Free chlorine and corrected free chlorine
- Battery level
- Force measurement refresh
- pH and ORP setpoint control
- Cleaning tracking
- Calibration tracking
- Configurable maintenance thresholds

## Installation via HACS

Repository:

```text
https://github.com/Yeoh37/intex_wa510
```

Add as a custom repository, category **Integration**, then install and restart Home Assistant.

## Important notes

Calibration command buttons are experimental. Do not use them outside a real calibration procedure.

## Changelog

### v0.6.3

Fast refresh release:
- pressing **Actualiser mesure** now starts a temporary fast refresh mode
- values are refreshed every 5 seconds for about 30 seconds
- new binary sensor: **Actualisation en cours**
- normal cloud polling resumes automatically after the fast refresh window

