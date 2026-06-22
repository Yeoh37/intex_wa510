"""Binary sensors for the Intex WA510 integration."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_MANUFACTURER,
    DEVICE_MODEL,
    DEVICE_NAME,
    DEVICE_SW_VERSION,
    DOMAIN,
)
from .coordinator import IntexWA510Coordinator


@dataclass(frozen=True)
class BinarySensorDef:
    """Describe a WA510 binary sensor entity."""

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
    BinarySensorDef("refreshing", "refreshing", "pool_refreshing", "mdi:sync"),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up WA510 binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IntexWA510BinarySensor(coordinator, entry, desc) for desc in BINARY_SENSORS],
        True,
    )


class IntexWA510BinarySensor(CoordinatorEntity, BinarySensorEntity):
    """WA510 binary sensor entity."""

    def __init__(
        self,
        coordinator: IntexWA510Coordinator,
        entry: ConfigEntry,
        desc: BinarySensorDef,
    ) -> None:
        """Initialize the binary sensor entity."""
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
    def is_on(self) -> bool | None:
        """Return whether the binary sensor is currently on."""
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

        if self.desc.key == "refreshing":
            return bool(self.coordinator.data.get("refreshing"))

        return None
