from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEVICE_NAME,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    DEVICE_SW_VERSION,
)


@dataclass(frozen=True)
class BinarySensorDef:
    key: str
    translation_key: str
    suggested_object_id: str
    icon: str


BINARY_SENSORS = [
    BinarySensorDef(
        "maintenance_required",
        "maintenance_required",
        "pool_maintenance_required",
        "mdi:check-circle-outline",
    ),
    BinarySensorDef(
        "cleaning_required",
        "cleaning_required",
        "pool_cleaning_required",
        "mdi:spray-bottle",
    ),
    BinarySensorDef(
        "ph_calibration_required",
        "ph_calibration_required",
        "pool_ph_calibration_required",
        "mdi:flask",
    ),
    BinarySensorDef(
        "orp_calibration_required",
        "orp_calibration_required",
        "pool_orp_calibration_required",
        "mdi:flask",
    ),
    BinarySensorDef(
        "battery_low", "battery_low", "pool_battery_low", "mdi:battery-alert"
    ),
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IntexWA510BinarySensor(coordinator, entry, desc) for desc in BINARY_SENSORS],
        True,
    )


class IntexWA510BinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, entry, desc: BinarySensorDef):
        super().__init__(coordinator)
        self.desc = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        self._attr_translation_key = desc.translation_key
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
            return value not in ("none", "normal", "off")

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

        return None
