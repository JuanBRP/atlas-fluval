"""Mode select (Manual / Auto / Pro)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FluvalConfigEntry
from .const import CMD_MODE, MODES
from .entity import FluvalEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: FluvalConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([FluvalModeSelect(entry.runtime_data, "mode")])


class FluvalModeSelect(FluvalEntity, SelectEntity):
    _attr_options = MODES

    @property
    def current_option(self) -> str | None:
        return (self.coordinator.data or {}).get("mode")

    @property
    def extra_state_attributes(self) -> dict | None:
        data = self.coordinator.data or {}
        return {
            "channels_r_b_cw_ww_a": data.get("channels"),
            "pro_schedule": data.get("pro_schedule"),
        }

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_command([CMD_MODE[option]])
