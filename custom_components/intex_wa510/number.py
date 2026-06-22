"""Number entities for the Intex WA510 integration."""

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
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
class NumberDef:
    """Describe a WA510 number entity."""

    key: str
    translation_key: str
    suggested_object_id: str
    unit: str | None
    icon: str
    native_min_value: float
    native_max_value: float
    native_step: float
    action_type: str
    method_name: str | None = None
    storage_key: str | None = None
    entity_category: EntityCategory | None = EntityCategory.CONFIG


NUMBERS = [
    NumberDef(
        "ph_set",
        "ph_set",
        "pool_ph_target",
        None,
        "mdi:target",
        7.2,
        7.8,
        0.1,
        "tuya",
        "set_ph_target",
    ),
    NumberDef(
        "orp_set",
        "orp_set",
        "pool_orp_target",
        "mV",
        "mdi:target",
        650,
        750,
        10,
        "tuya",
        "set_orp_target",
    ),
    NumberDef(
        "cleaning_days",
        "cleaning_days",
        "pool_cleaning_threshold_days",
        "j",
        "mdi:spray-bottle",
        1,
        365,
        1,
        "storage",
        storage_key="cleaning_days",
    ),
    NumberDef(
        "ph_calibration_days",
        "ph_calibration_days",
        "pool_ph_calibration_threshold_days",
        "j",
        "mdi:flask",
        1,
        365,
        1,
        "storage",
        storage_key="ph_calibration_days",
    ),
    NumberDef(
        "orp_calibration_days",
        "orp_calibration_days",
        "pool_orp_calibration_threshold_days",
        "j",
        "mdi:flask",
        1,
        365,
        1,
        "storage",
        storage_key="orp_calibration_days",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up WA510 number entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IntexWA510Number(coordinator, entry, desc) for desc in NUMBERS], True
    )


class IntexWA510Number(CoordinatorEntity, NumberEntity):
    """WA510 number entity."""

    def __init__(
        self, coordinator: IntexWA510Coordinator, entry: ConfigEntry, desc: NumberDef
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.desc = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}_number"
        self._attr_translation_key = desc.translation_key
        self._attr_has_entity_name = True
        self._attr_suggested_object_id = desc.suggested_object_id
        self._attr_native_unit_of_measurement = desc.unit
        self._attr_icon = desc.icon
        self._attr_native_min_value = desc.native_min_value
        self._attr_native_max_value = desc.native_max_value
        self._attr_native_step = desc.native_step
        self._attr_mode = NumberMode.BOX
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

    async def async_set_native_value(self, value: float) -> None:
        """Set the native value on the device or in local storage."""
        if self.desc.action_type == "storage":
            await self.coordinator.async_set_maintenance_threshold(
                self.desc.storage_key, value
            )
            return

        method = getattr(self.coordinator.client, self.desc.method_name)
        await method(value)
        await self.coordinator.async_request_refresh()
