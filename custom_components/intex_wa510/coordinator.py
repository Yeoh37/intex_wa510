"""Data coordinator for the Intex WA510 integration."""

import contextlib
from datetime import datetime, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

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
    FAST_REFRESH_INTERVAL,
    FAST_REFRESH_SECONDS,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .tuya_api import TuyaCloudClient

_LOGGER = logging.getLogger(__name__)


class IntexWA510Coordinator(DataUpdateCoordinator):
    """Fetch Intex WA510 data from Tuya Cloud and store maintenance dates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator and persistent maintenance store."""
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
        self.fast_refresh_active = False
        self._fast_refresh_handles = []

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def async_load_maintenance_data(self) -> None:
        """Load persisted maintenance data from storage."""
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
            "refreshing": self.fast_refresh_active,
            "raw": raw,
        }

    async def async_mark_maintenance_done(self, key: str | None) -> None:
        """Mark a maintenance task as completed today."""
        if key is None:
            return
        self.maintenance_data[key] = dt_util.now().date().isoformat()
        await self._store.async_save(self.maintenance_data)
        await self.async_request_refresh()

    async def async_set_maintenance_threshold(
        self, key: str | None, value: float
    ) -> None:
        """Persist a maintenance threshold value and refresh entities."""
        if key is None:
            return
        self.maintenance_data[key] = int(value)
        await self._store.async_save(self.maintenance_data)
        await self.async_request_refresh()

    async def async_refresh_measurement_and_update(self) -> None:
        """Force a WA510 measurement then poll quickly for about 30 seconds."""
        await self.client.refresh_measurement()
        self._start_fast_refresh_mode()
        await self.async_request_refresh()

    def _start_fast_refresh_mode(self) -> None:
        """Start a temporary fast refresh window after a manual measurement request."""
        self._cancel_fast_refresh_handles()
        self.fast_refresh_active = True
        self._notify_fast_refresh_state()

        for delay in range(
            FAST_REFRESH_INTERVAL,
            FAST_REFRESH_SECONDS + 1,
            FAST_REFRESH_INTERVAL,
        ):
            handle = self.hass.loop.call_later(
                delay,
                lambda: self.hass.async_create_task(self._async_fast_refresh_tick()),
            )
            self._fast_refresh_handles.append(handle)

        handle = self.hass.loop.call_later(
            FAST_REFRESH_SECONDS + 1,
            lambda: self.hass.async_create_task(self._async_stop_fast_refresh_mode()),
        )
        self._fast_refresh_handles.append(handle)

    async def _async_fast_refresh_tick(self) -> None:
        """Refresh values during the temporary fast refresh window."""
        if not self.fast_refresh_active:
            return
        try:
            await self.async_request_refresh()
        except Exception:
            _LOGGER.exception("WA510 FAST REFRESH ERROR")

    async def _async_stop_fast_refresh_mode(self) -> None:
        """Stop fast refresh mode and notify Home Assistant."""
        self.fast_refresh_active = False
        self._cancel_fast_refresh_handles()
        self._notify_fast_refresh_state()

    def _cancel_fast_refresh_handles(self) -> None:
        for handle in self._fast_refresh_handles:
            with contextlib.suppress(Exception):
                handle.cancel()
        self._fast_refresh_handles = []

    def _notify_fast_refresh_state(self) -> None:
        """Notify entities when only the fast refresh state changes."""
        if self.data is not None:
            updated = dict(self.data)
            updated["refreshing"] = self.fast_refresh_active
            self.async_set_updated_data(updated)

    def days_since(self, key: str) -> int | None:
        """Return days elapsed since a stored maintenance date."""
        value = self.maintenance_data.get(key)
        if not value:
            return None
        try:
            stored_date = datetime.fromisoformat(str(value)).date()
        except ValueError:
            return None
        return (dt_util.now().date() - stored_date).days

    def get_int(self, key: str, default: int) -> int:
        """Return an integer threshold from storage or a default value."""
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
