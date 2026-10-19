"""Minimal CBOR (RFC 8949) decoder — just enough for Fluval status frames."""

from __future__ import annotations

import struct
from typing import Any


class Incomplete(Exception):
    """Raised when the buffer ends before the item does (frame still arriving)."""


def _take(buf: bytes, pos: int, n: int) -> bytes:
    if pos + n > len(buf):
        raise Incomplete
    return buf[pos : pos + n]


def _arg(buf: bytes, pos: int, ai: int) -> tuple[int, int]:
    if ai < 24:
        return ai, pos
    sizes = {24: 1, 25: 2, 26: 4, 27: 8}
    if ai not in sizes:
        raise ValueError(f"unsupported CBOR additional info {ai}")
    n = sizes[ai]
    return int.from_bytes(_take(buf, pos, n), "big"), pos + n


def decode(buf: bytes, pos: int = 0) -> tuple[Any, int]:
    """Decode one item at pos; return (value, next_pos)."""
    head = _take(buf, pos, 1)[0]
    pos += 1
    major, ai = head >> 5, head & 0x1F

    if major == 7:
        if ai == 20:
            return False, pos
        if ai == 21:
            return True, pos
        if ai in (22, 23):
            return None, pos
        if ai == 25:
            return struct.unpack(">e", _take(buf, pos, 2))[0], pos + 2
        if ai == 26:
            return struct.unpack(">f", _take(buf, pos, 4))[0], pos + 4
        if ai == 27:
            return struct.unpack(">d", _take(buf, pos, 8))[0], pos + 8
        if ai < 24:
            return ai, pos
        if ai == 24:
            return _take(buf, pos, 1)[0], pos + 1
        raise ValueError(f"unsupported CBOR simple value {ai}")

    val, pos = _arg(buf, pos, ai)
    if major == 0:
        return val, pos
    if major == 1:
        return -1 - val, pos
    if major == 2:
        return bytes(_take(buf, pos, val)), pos + val
    if major == 3:
        return _take(buf, pos, val).decode("utf-8", "replace"), pos + val
    if major == 4:
        items = []
        for _ in range(val):
            item, pos = decode(buf, pos)
            items.append(item)
        return items, pos
    if major == 5:
        out: dict[Any, Any] = {}
        for _ in range(val):
            key, pos = decode(buf, pos)
            value, pos = decode(buf, pos)
            out[key] = value
        return out, pos
    # major 6: tag — skip the tag number, return the tagged item.
    return decode(buf, pos)


def parse_status(frame: bytes) -> dict[Any, Any]:
    """Parse a D2-headed status frame into a dict. Raises Incomplete if truncated."""
    if not frame or frame[0] != 0xD2:
        raise ValueError("not a status frame")
    value, _ = decode(frame, 1)
    if not isinstance(value, dict):
        raise ValueError("status payload is not a map")
    return value
