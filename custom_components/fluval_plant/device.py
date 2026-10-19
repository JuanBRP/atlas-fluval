"""BLE client for one Fluval Plant 4.0 light.

Connect-on-demand: each call connects, does its work, reads status and
disconnects, so the light's single BLE slot is free the rest of the time.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .cbor import Incomplete, parse_status
from .const import (
    CMD_STATUS,
    CONNECT_SETTLE_S,
    INTER_WRITE_S,
    KEY_MODE,
    KEY_POWER,
    MODE_BY_VALUE,
    NOTIFY_UUID,
    STATUS_HEADER,
    STATUS_TIMEOUT_S,
    WRITE_UUID,
)

_LOGGER = logging.getLogger(__name__)


class FluvalError(Exception):
    """Light unreachable or misbehaving."""


class FluvalPlantDevice:
    """One light, addressed by BLE MAC."""

    def __init__(self, hass: HomeAssistant, address: str, name: str, lock: asyncio.Lock) -> None:
        self.hass = hass
        self.address = address
        self.name = name
        # Shared across all lights: one radio, one conversation at a time.
        self._lock = lock

    async def async_status(self) -> dict[str, Any]:
        return await self._session([])

    async def async_send(self, payloads: list[bytes]) -> dict[str, Any]:
        return await self._session(payloads)

    async def _session(self, payloads: list[bytes]) -> dict[str, Any]:
        async with self._lock:
            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, self.address, connectable=True
            )
            if ble_device is None:
                raise FluvalError(f"{self.name} is not in Bluetooth range (or the phone app holds it)")

            try:
                client = await establish_connection(
                    BleakClientWithServiceCache, ble_device, self.name, max_attempts=3
                )
            except Exception as err:  # noqa: BLE001 - surface any connect failure
                raise FluvalError(f"could not connect to {self.name}: {err}") from err

            try:
                write_char = client.services.get_characteristic(WRITE_UUID)
                if write_char is None or client.services.get_characteristic(NOTIFY_UUID) is None:
                    found = [
                        f"{s.uuid}: {[c.uuid for c in s.characteristics]}" for s in client.services
                    ]
                    _LOGGER.error(
                        "%s does not expose the expected FFF0 service; GATT layout: %s",
                        self.name,
                        found,
                    )
                    raise FluvalError("unexpected GATT layout — see log")
                with_response = "write" in write_char.properties

                loop = asyncio.get_running_loop()
                buffer = bytearray()
                waiter: asyncio.Future[dict[Any, Any]] = loop.create_future()

                def _on_notify(_char: BleakGATTCharacteristic, data: bytearray) -> None:
                    nonlocal buffer
                    if data and data[0] == STATUS_HEADER:
                        buffer = bytearray(data)
                    elif buffer:
                        buffer.extend(data)
                    else:
                        return
                    try:
                        status = parse_status(bytes(buffer))
                    except Incomplete:
                        return
                    except ValueError as err:
                        _LOGGER.debug("%s: unparsable frame %s (%s)", self.name, buffer.hex(), err)
                        buffer = bytearray()
                        return
                    buffer = bytearray()
                    if not waiter.done():
                        waiter.set_result(status)

                await client.start_notify(NOTIFY_UUID, _on_notify)
                await asyncio.sleep(CONNECT_SETTLE_S)

                for payload in payloads:
                    await client.write_gatt_char(WRITE_UUID, payload, response=with_response)
                    await asyncio.sleep(INTER_WRITE_S)

                # Status replies to our own commands may land first; we want a fresh dump.
                if waiter.done():
                    waiter = loop.create_future()
                await client.write_gatt_char(WRITE_UUID, CMD_STATUS, response=with_response)
                try:
                    raw = await asyncio.wait_for(waiter, STATUS_TIMEOUT_S)
                except TimeoutError as err:
                    raise FluvalError(f"{self.name} did not report status") from err
            finally:
                try:
                    await client.disconnect()
                except Exception:  # noqa: BLE001
                    _LOGGER.debug("%s: disconnect raised", self.name, exc_info=True)

        return {
            "power": raw.get(KEY_POWER),
            "mode": MODE_BY_VALUE.get(raw.get(KEY_MODE)),
        }
