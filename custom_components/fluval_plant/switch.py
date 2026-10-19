"""Power switch."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FluvalConfigEntry
from .const import CMD_POWER_OFF, CMD_POWER_ON
from .entity import FluvalEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: FluvalConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([FluvalPowerSwitch(entry.runtime_data, "power")])


class FluvalPowerSwitch(FluvalEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        return (self.coordinator.data or {}).get("power")

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_command([CMD_POWER_ON])

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_command([CMD_POWER_OFF])
