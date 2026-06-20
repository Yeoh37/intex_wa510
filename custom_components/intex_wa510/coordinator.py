from __future__ import annotations

from datetime import date, datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_DEVICE_ID,
    CONF_ENDPOINT,
    DEFAULT_CLEANING_DAYS,
    DEFAULT_ENDPOINT,
    DEFAULT_ORP_CALIBRATION_DAYS,
    DEFAULT_PH_CALIBRATION_DAYS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .tuya_api import TuyaCloudClient

_LOGGER = logging.getLogger(__name__)


class IntexWA510Coordinator(DataUpdateCoordinator):
    """Fetch Intex WA510 data from Tuya Cloud and store maintenance dates."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.entry = entry
        self.client = TuyaCloudClient(
            async_get_clientsession(hass),
            entry.data.get(CONF_ENDPOINT, DEFAULT_ENDPOINT),
            entry.data[CONF_ACCESS_ID],
            entry.data[CONF_ACCESS_SECRET],
            entry.data[CONF_DEVICE_ID],
        )

        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}")
        self.maintenance_data: dict[str, str | int | None] = {
            "last_cleaning": None,
            "last_ph_calibration": None,
            "last_orp_calibration": None,
            "cleaning_days": DEFAULT_CLEANING_DAYS,
            "ph_calibration_days": DEFAULT_PH_CALIBRATION_DAYS,
            "orp_calibration_days": DEFAULT_ORP_CALIBRATION_DAYS,
            "last_measurement": None,
        }

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def async_load_maintenance_data(self) -> None:
        stored = await self._store.async_load()
        if isinstance(stored, dict):
            self.maintenance_data.update(stored)

    async def _async_update_data(self):
        raw = await self.client.get_properties()

        last_measurement = datetime.now().replace(microsecond=0).isoformat()
        self.maintenance_data["last_measurement"] = last_measurement
        await self._store.async_save(self.maintenance_data)

        _LOGGER.info(
            "WA510 REFRESH=%s | PH=%s | ORP=%s | FC=%s | FC_CORRIGE=%s",
            raw.get("refresh_switch"),
            raw.get("PH_Number"),
            raw.get("ORP_Number"),
            raw.get("fc_number"),
            raw.get("fcwchemical"),
        )

        return {
            "temperature_c": raw.get("water_tempture_c"),
            "temperature_f": raw.get("water_tempture_f"),
            "ph": self._scale(raw.get("PH_Number"), 100),
            "orp": raw.get("ORP_Number"),
            "free_chlorine": self._scale(raw.get("fc_number"), 100),
            "free_chlorine_chemical": self._scale(raw.get("fcwchemical"), 100),
            "battery": raw.get("battery_capacity"),
            "ph_indicator": self._indicator(raw.get("ph_indcator")),
            "orp_indicator": self._indicator(raw.get("orp_indicator")),
            "fc_indicator": self._indicator(raw.get("fc_indicator")),
            "orp_set": raw.get("orp_set"),
            "ph_set": self._scale(raw.get("ph_set"), 100),
            "maintenance_indicator": self._maintenance_indicator(
                raw.get("maintenance_indicator")
            ),
            "error_code": raw.get("error_code"),
            "refresh_switch": raw.get("refresh_switch"),
            "ph_caliberate": raw.get("ph_caliberate"),
            "orp_caliberate": raw.get("orp_caliberate"),
            "report_number": raw.get("report_number"),
            "fc_unit_change_switch": raw.get("fc_unit_change_switch"),
            "fc_sta_flg": raw.get("fc_sta_flg"),
            "last_cleaning": self.maintenance_data.get("last_cleaning"),
            "last_ph_calibration": self.maintenance_data.get("last_ph_calibration"),
            "last_orp_calibration": self.maintenance_data.get("last_orp_calibration"),
            "days_since_cleaning": self.days_since("last_cleaning"),
            "days_since_ph_calibration": self.days_since("last_ph_calibration"),
            "days_since_orp_calibration": self.days_since("last_orp_calibration"),
            "cleaning_days": self.get_int("cleaning_days", DEFAULT_CLEANING_DAYS),
            "ph_calibration_days": self.get_int(
                "ph_calibration_days", DEFAULT_PH_CALIBRATION_DAYS
            ),
            "orp_calibration_days": self.get_int(
                "orp_calibration_days", DEFAULT_ORP_CALIBRATION_DAYS
            ),
            "last_measurement": last_measurement,
            "raw": raw,
        }

    async def async_mark_maintenance_done(self, key: str | None) -> None:
        if key is None:
            return
        self.maintenance_data[key] = date.today().isoformat()
        await self._store.async_save(self.maintenance_data)
        await self.async_request_refresh()

    async def async_set_maintenance_threshold(
        self, key: str | None, value: float
    ) -> None:
        if key is None:
            return
        self.maintenance_data[key] = int(value)
        await self._store.async_save(self.maintenance_data)
        await self.async_request_refresh()

    async def async_refresh_measurement_and_update(self) -> None:
        """Force a WA510 measurement and refresh HA after a short delay."""
        await self.client.refresh_measurement()
        await self.async_request_refresh()

        async def delayed_refresh(now=None):
            await self.async_request_refresh()

        self.hass.loop.call_later(
            20, lambda: self.hass.async_create_task(delayed_refresh())
        )
        self.hass.loop.call_later(
            60, lambda: self.hass.async_create_task(delayed_refresh())
        )

    def days_since(self, key: str) -> int | None:
        value = self.maintenance_data.get(key)
        if not value:
            return None
        try:
            stored_date = datetime.fromisoformat(str(value)).date()
        except ValueError:
            return None
        return (date.today() - stored_date).days

    def get_int(self, key: str, default: int) -> int:
        value = self.maintenance_data.get(key)
        try:
            return int(value)
        except TypeError, ValueError:
            return default

    @staticmethod
    def _scale(value, div):
        if value is None:
            return None
        return round(float(value) / div, 2)

    @staticmethod
    def _indicator(value):
        if value == "off":
            return "normal"
        if value == "green":
            return "ok"
        if value == "red":
            return "anomaly"
        return value

    @staticmethod
    def _maintenance_indicator(value):
        if value == "off":
            return "none"
        if value == "red":
            return "required"
        return value
