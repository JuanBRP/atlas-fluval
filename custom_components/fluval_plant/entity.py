"""Shared entity base."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import FluvalCoordinator


class FluvalEntity(CoordinatorEntity[FluvalCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: FluvalCoordinator, key: str) -> None:
        super().__init__(coordinator)
        address = coordinator.device.address
        self._attr_unique_id = f"{address}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            connections={(CONNECTION_BLUETOOTH, address)},
            name=coordinator.device.name,
            manufacturer="Fluval",
            model="Plant 4.0",
        )
