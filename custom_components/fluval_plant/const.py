"""Constants for the Fluval Plant 4.0 integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "fluval_plant"

# Vendor serial-over-BLE service (see upstream docs/PROTOCOL.md).
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

NAME_PREFIXES = ("Plant4.0_", "PlantPro_")

# Frames: one header byte followed by a CBOR map.
CMD_POWER_ON = bytes([0xD1, 0xA1, 0x02, 0xF5])
CMD_POWER_OFF = bytes([0xD1, 0xA1, 0x02, 0xF4])
CMD_MODE = {
    "manual": bytes([0xD1, 0xA1, 0x01, 0x00]),
    "auto": bytes([0xD1, 0xA1, 0x01, 0x01]),
    "pro": bytes([0xD1, 0xA1, 0x01, 0x02]),
}
CMD_STATUS = bytes([0xD0, 0xFF])

STATUS_HEADER = 0xD2
KEY_MODE = 1
KEY_POWER = 2
MODE_BY_VALUE = {0: "manual", 1: "auto", 2: "pro"}
MODES = ["manual", "auto", "pro"]

# Each poll briefly holds the light's single BLE slot, so keep it sparse.
UPDATE_INTERVAL = timedelta(minutes=15)
CONNECT_SETTLE_S = 1.0
INTER_WRITE_S = 0.3
STATUS_TIMEOUT_S = 8.0
