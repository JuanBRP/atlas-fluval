"""Resume-schedule button: power on + Pro mode in one connection."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FluvalConfigEntry
from .const import CMD_MODE, CMD_POWER_ON
from .entity import FluvalEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: FluvalConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([FluvalResumeButton(entry.runtime_data, "resume_schedule")])


class FluvalResumeButton(FluvalEntity, ButtonEntity):
    @property
    def available(self) -> bool:
        # Pressable even when the last poll failed — that's exactly the
        # after-an-outage case this button exists for.
        return True

    async def async_press(self) -> None:
        await self.coordinator.async_command([CMD_POWER_ON, CMD_MODE["pro"]])
