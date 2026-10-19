"""Data coordinator for one Fluval light."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL
from .device import FluvalError, FluvalPlantDevice

_LOGGER = logging.getLogger(__name__)


class FluvalCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls rarely; refreshes immediately after every command."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, device: FluvalPlantDevice) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{device.address}",
            update_interval=UPDATE_INTERVAL,
        )
        self.device = device

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.device.async_status()
        except FluvalError as err:
            raise UpdateFailed(str(err)) from err

    async def async_command(self, payloads: list[bytes]) -> None:
        try:
            status = await self.device.async_send(payloads)
        except FluvalError as err:
            raise HomeAssistantError(str(err)) from err
        self.async_set_updated_data(status)
