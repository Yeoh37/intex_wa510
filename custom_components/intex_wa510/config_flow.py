"""Config flow for the Intex WA510 integration."""

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_DEVICE_ID,
    CONF_ENDPOINT,
    DEFAULT_ENDPOINT,
    DOMAIN,
)


class IntexWA510ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intex WA510."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user step to collect Tuya credentials and device ID."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Intex WA510",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_ACCESS_ID): str,
                vol.Required(CONF_ACCESS_SECRET): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Required(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
