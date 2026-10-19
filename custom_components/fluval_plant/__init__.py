"""Fluval Plant 4.0 — local Bluetooth control from Home Assistant."""

from __future__ import annotations

import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import FluvalCoordinator
from .device import FluvalPlantDevice

PLATFORMS = [Platform.SWITCH, Platform.SELECT, Platform.BUTTON]

type FluvalConfigEntry = ConfigEntry[FluvalCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: FluvalConfigEntry) -> bool:
    lock = hass.data.setdefault(DOMAIN, {}).setdefault("radio_lock", asyncio.Lock())
    device = FluvalPlantDevice(hass, entry.data[CONF_ADDRESS], entry.title, lock)
    coordinator = FluvalCoordinator(hass, entry, device)
    # Don't block startup on a light that's out of range or powered off;
    # entities start unavailable and recover on the next poll or command.
    await coordinator.async_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FluvalConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
