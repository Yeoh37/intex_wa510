"""Sensor entities for the Intex WA510 integration."""

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
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
class SensorDef:
    """Describe a WA510 sensor entity."""

    key: str
    translation_key: str
    suggested_object_id: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT
    icon: str | None = None
    entity_category: EntityCategory | None = None


SENSORS = [
    SensorDef(
        "temperature_c",
        "temperature_c",
        "pool_water_temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        "mdi:water-thermometer",
    ),
    SensorDef(
        "ph", "ph", "pool_ph", None, None, SensorStateClass.MEASUREMENT, "mdi:ph"
    ),
    SensorDef(
        "orp",
        "orp",
        "pool_orp",
        "mV",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:lightning-bolt",
    ),
    SensorDef(
        "free_chlorine",
        "free_chlorine",
        "pool_free_chlorine",
        "ppm",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:test-tube",
    ),
    SensorDef(
        "free_chlorine_chemical",
        "free_chlorine_chemical",
        "pool_corrected_free_chlorine",
        "ppm",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:test-tube",
    ),
    SensorDef(
        "battery",
        "battery",
        "pool_battery",
        PERCENTAGE,
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        "mdi:battery",
    ),
    SensorDef(
        "ph_indicator",
        "ph_indicator",
        "pool_ph_indicator",
        None,
        None,
        None,
        "mdi:ph",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "orp_indicator",
        "orp_indicator",
        "pool_orp_indicator",
        None,
        None,
        None,
        "mdi:lightning-bolt",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "fc_indicator",
        "fc_indicator",
        "pool_chlorine_indicator",
        None,
        None,
        None,
        "mdi:test-tube",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "maintenance_indicator",
        "maintenance_indicator",
        "pool_maintenance",
        None,
        None,
        None,
        "mdi:wrench-clock",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "error_code",
        "error_code",
        "pool_error_code",
        None,
        None,
        None,
        "mdi:alert-circle-outline",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "ph_caliberate",
        "ph_caliberate",
        "pool_ph_calibration_status",
        None,
        None,
        None,
        "mdi:flask",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "orp_caliberate",
        "orp_caliberate",
        "pool_orp_calibration_status",
        None,
        None,
        None,
        "mdi:flask",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "last_cleaning",
        "last_cleaning",
        "pool_last_cleaning",
        None,
        None,
        None,
        "mdi:spray-bottle",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "last_ph_calibration",
        "last_ph_calibration",
        "pool_last_ph_calibration",
        None,
        None,
        None,
        "mdi:flask",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "last_orp_calibration",
        "last_orp_calibration",
        "pool_last_orp_calibration",
        None,
        None,
        None,
        "mdi:flask",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "days_since_cleaning",
        "days_since_cleaning",
        "pool_days_since_cleaning",
        "j",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:calendar-clock",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "days_since_ph_calibration",
        "days_since_ph_calibration",
        "pool_days_since_ph_calibration",
        "j",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:calendar-clock",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "days_since_orp_calibration",
        "days_since_orp_calibration",
        "pool_days_since_orp_calibration",
        "j",
        None,
        SensorStateClass.MEASUREMENT,
        "mdi:calendar-clock",
        EntityCategory.DIAGNOSTIC,
    ),
    SensorDef(
        "last_measurement",
        "last_measurement",
        "pool_last_measurement",
        None,
        None,
        None,
        "mdi:clock-check-outline",
        EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up WA510 sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IntexWA510Sensor(coordinator, entry, desc) for desc in SENSORS], True
    )


class IntexWA510Sensor(CoordinatorEntity, SensorEntity):
    """WA510 sensor entity."""

    def __init__(
        self, coordinator: IntexWA510Coordinator, entry: ConfigEntry, desc: SensorDef
    ) -> None:
        """Initialize the sensor entity."""
        super().__init__(coordinator)
        self.desc = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        self._attr_translation_key = desc.translation_key
        self._attr_has_entity_name = True
        self._attr_suggested_object_id = desc.suggested_object_id
        self._attr_native_unit_of_measurement = desc.unit
        self._attr_device_class = desc.device_class
        self._attr_state_class = desc.state_class
        self._attr_icon = desc.icon
        self._attr_entity_category = desc.entity_category
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_id"])},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "sw_version": DEVICE_SW_VERSION,
        }

    @property
    def native_value(self):
        """Return the current native value from coordinator data."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.desc.key)
