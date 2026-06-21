from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEVICE_NAME, DEVICE_MANUFACTURER, DEVICE_MODEL, DEVICE_SW_VERSION


@dataclass(frozen=True)
class BinarySensorDef:
    key: str
    name: str
    suggested_object_id: str
    icon: str


BINARY_SENSORS = [
    BinarySensorDef("maintenance_required", "Maintenance requise", "piscine_maintenance_requise", "mdi:check-circle-outline"),
    BinarySensorDef("cleaning_required", "Entretien - Nettoyage requis", "piscine_nettoyage_wa510_requis", "mdi:spray-bottle"),
    BinarySensorDef("ph_calibration_required", "Calibration - pH requise", "piscine_calibration_ph_requise", "mdi:flask"),
    BinarySensorDef("orp_calibration_required", "Calibration - ORP requise", "piscine_calibration_orp_requise", "mdi:flask"),
    BinarySensorDef("battery_low", "Batterie faible", "piscine_batterie_faible", "mdi:battery-alert"),
    BinarySensorDef("refreshing", "Actualisation en cours", "piscine_actualisation_en_cours", "mdi:sync"),
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IntexWA510BinarySensor(coordinator, entry, desc) for desc in BINARY_SENSORS], True)


class IntexWA510BinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, desc: BinarySensorDef):
        super().__init__(coordinator)
        self.desc = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        self._attr_name = desc.name
        self._attr_has_entity_name = True
        self._attr_suggested_object_id = desc.suggested_object_id
        self._attr_icon = desc.icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_id"])},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "sw_version": DEVICE_SW_VERSION,
        }

    @property
    def is_on(self):
        if not self.coordinator.data:
            return None

        if self.desc.key == "maintenance_required":
            value = self.coordinator.data.get("maintenance_indicator")
            if value is None:
                return None
            return value not in ("Aucune", "Normal", "off")

        if self.desc.key == "cleaning_required":
            days = self.coordinator.data.get("days_since_cleaning")
            threshold = self.coordinator.data.get("cleaning_days") or 30
            return days is None or days >= threshold

        if self.desc.key == "ph_calibration_required":
            days = self.coordinator.data.get("days_since_ph_calibration")
            threshold = self.coordinator.data.get("ph_calibration_days") or 120
            return days is None or days >= threshold

        if self.desc.key == "orp_calibration_required":
            days = self.coordinator.data.get("days_since_orp_calibration")
            threshold = self.coordinator.data.get("orp_calibration_days") or 120
            return days is None or days >= threshold

        if self.desc.key == "battery_low":
            battery = self.coordinator.data.get("battery")
            if battery is None:
                return None
            return battery < 20

        if self.desc.key == "refreshing":
            return bool(self.coordinator.data.get("refreshing"))

        return None
