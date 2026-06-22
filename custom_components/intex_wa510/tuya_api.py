"""Tuya Cloud API client used by the Intex WA510 integration."""

import hashlib
import hmac
import json
import time
from typing import Any

import aiohttp


class TuyaApiError(Exception):
    """Tuya API error."""


class TuyaCloudClient:
    """Small Tuya Cloud API client for Intex WA510 / AGP SMART SENSOR T3U."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        endpoint: str,
        access_id: str,
        access_secret: str,
        device_id: str,
    ) -> None:
        """Initialize the client with Tuya endpoint and credentials."""
        self.session = session
        self.endpoint = endpoint.rstrip("/")
        self.access_id = access_id
        self.access_secret = access_secret
        self.device_id = device_id
        self._token: str | None = None
        self._token_expire_at = 0.0

    def _sign(
        self, method: str, path: str, body: str = "", token: str = ""
    ) -> tuple[str, str]:
        timestamp = str(int(time.time() * 1000))
        content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
        string_to_sign = f"{method}\n{content_hash}\n\n{path}"
        sign_str = f"{self.access_id}{token}{timestamp}{string_to_sign}"
        signature = (
            hmac.new(
                self.access_secret.encode("utf-8"),
                sign_str.encode("utf-8"),
                hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        return timestamp, signature

    async def _request(
        self,
        method: str,
        path: str,
        token: str = "",
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body_str = ""
        if body is not None:
            body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False)

        timestamp, signature = self._sign(method, path, body=body_str, token=token)
        headers = {
            "client_id": self.access_id,
            "sign": signature,
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
            "Content-Type": "application/json",
        }

        if token:
            headers["access_token"] = token

        async with self.session.request(
            method,
            self.endpoint + path,
            headers=headers,
            data=body_str if body is not None else None,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            data = await resp.json(content_type=None)

        if not data.get("success", False):
            raise TuyaApiError(f"Tuya API error: {data}")

        return data

    async def get_token(self) -> str:
        """Get a valid Tuya access token, refreshing it when needed."""
        if self._token and time.time() < self._token_expire_at - 60:
            return self._token

        data = await self._request("GET", "/v1.0/token?grant_type=1")
        result = data["result"]
        self._token = result["access_token"]
        self._token_expire_at = time.time() + int(result.get("expire_time", 7200))
        return self._token

    async def get_properties(self) -> dict[str, Any]:
        """Fetch all device shadow properties."""
        token = await self.get_token()
        path = f"/v2.0/cloud/thing/{self.device_id}/shadow/properties"
        data = await self._request("GET", path, token=token)
        props = data.get("result", {}).get("properties", [])
        return {p["code"]: p.get("value") for p in props}

    async def send_properties(self, properties: dict[str, Any]) -> dict[str, Any]:
        """Send one or more property updates to the device."""
        token = await self.get_token()
        path = f"/v2.0/cloud/thing/{self.device_id}/shadow/properties/issue"
        body = {"properties": properties}
        return await self._request("POST", path, token=token, body=body)

    async def refresh_measurement(self) -> dict[str, Any]:
        """Trigger a manual measurement refresh on the device."""
        return await self.send_properties({"refresh_switch": True})

    async def set_ph_target(self, value: float) -> dict[str, Any]:
        """Set pH target in centi-pH units expected by the device."""
        return await self.send_properties({"ph_set": round(value * 100)})

    async def set_orp_target(self, value: int) -> dict[str, Any]:
        """Set ORP target in millivolts."""
        return await self.send_properties({"orp_set": int(value)})

    async def start_ph_calibration(self) -> dict[str, Any]:
        """Start pH calibration workflow."""
        return await self.send_properties({"ph_caliberate": 0})

    async def validate_ph_4_calibration(self) -> dict[str, Any]:
        """Confirm pH 4.00 calibration step."""
        return await self.send_properties({"ph_caliberate": 1})

    async def validate_ph_9_calibration(self) -> dict[str, Any]:
        """Confirm pH 9.00 calibration step."""
        return await self.send_properties({"ph_caliberate": 129})

    async def start_orp_calibration(self) -> dict[str, Any]:
        """Start ORP calibration workflow."""
        return await self.send_properties({"orp_caliberate": 0})

    async def validate_orp_256_calibration(self) -> dict[str, Any]:
        """Confirm ORP 256 mV calibration step."""
        return await self.send_properties({"orp_caliberate": 1})
