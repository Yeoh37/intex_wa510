"""Button entities for the Intex WA510 integration."""

from dataclasses import dataclass
import logging

from homeassistant.components.button import ButtonEntity
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

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ButtonDef:
    """Describe a WA510 button entity."""

    key: str
    translation_key: str
    suggested_object_id: str
    icon: str
    action_type: str
    method_name: str | None = None
    maintenance_key: str | None = None
    entity_category: EntityCategory | None = None


BUTTONS = [
    ButtonDef(
        "refresh_measurement",
        "refresh_measurement",
        "pool_refresh_measurement",
        "mdi:refresh",
        "refresh",
    ),
    ButtonDef(
        "cleaning_done",
        "cleaning_done",
        "pool_cleaning_done",
        "mdi:spray-bottle",
        "maintenance",
        maintenance_key="last_cleaning",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonDef(
        "ph_calibration_done",
        "ph_calibration_done",
        "pool_ph_calibration_done",
        "mdi:flask-check",
        "maintenance",
        maintenance_key="last_ph_calibration",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonDef(
        "orp_calibration_done",
        "orp_calibration_done",
        "pool_orp_calibration_done",
        "mdi:flask-check-outline",
        "maintenance",
        maintenance_key="last_orp_calibration",
        entity_category=EntityCategory.CONFIG,
    ),
    ButtonDef(
        "ph_cal_start",
        "ph_cal_start",
        "pool_start_ph_calibration",
        "mdi:flask-outline",
        "tuya",
        "start_ph_calibration",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonDef(
        "ph_cal_4",
        "ph_cal_4",
        "pool_confirm_ph_4",
        "mdi:numeric-4-circle-outline",
        "tuya",
        "validate_ph_4_calibration",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonDef(
        "ph_cal_9",
        "ph_cal_9",
        "pool_confirm_ph_9",
        "mdi:numeric-9-circle-outline",
        "tuya",
        "validate_ph_9_calibration",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonDef(
        "orp_cal_start",
        "orp_cal_start",
        "pool_start_orp_calibration",
        "mdi:lightning-bolt-outline",
        "tuya",
        "start_orp_calibration",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ButtonDef(
        "orp_cal_256",
        "orp_cal_256",
        "pool_confirm_orp_256",
        "mdi:lightning-bolt-circle",
        "tuya",
        "validate_orp_256_calibration",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up WA510 buttons from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [IntexWA510Button(coordinator, entry, desc) for desc in BUTTONS], True
    )


class IntexWA510Button(CoordinatorEntity, ButtonEntity):
    """WA510 button entity."""

    def __init__(
        self, coordinator: IntexWA510Coordinator, entry: ConfigEntry, desc: ButtonDef
    ) -> None:
        """Initialize the button entity."""
        super().__init__(coordinator)
        self.desc = desc
        self._attr_unique_id = f"{entry.entry_id}_{desc.key}"
        self._attr_translation_key = desc.translation_key
        self._attr_has_entity_name = True
        self._attr_suggested_object_id = desc.suggested_object_id
        self._attr_icon = desc.icon
        self._attr_entity_category = desc.entity_category
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data["device_id"])},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "sw_version": DEVICE_SW_VERSION,
        }

    async def async_press(self) -> None:
        """Handle button press actions."""
        _LOGGER.info("WA510 BUTTON PRESSED: %s", self.desc.key)

        try:
            if self.desc.action_type == "maintenance":
                await self.coordinator.async_mark_maintenance_done(
                    self.desc.maintenance_key
                )
                return

            if self.desc.action_type == "refresh":
                await self.coordinator.async_refresh_measurement_and_update()
                return

            method = getattr(self.coordinator.client, self.desc.method_name)
            result = await method()
            _LOGGER.info("WA510 BUTTON RESULT: %s / result=%s", self.desc.key, result)
            await self.coordinator.async_request_refresh()

        except Exception:
            _LOGGER.exception("WA510 BUTTON ERROR: %s", self.desc.key)
