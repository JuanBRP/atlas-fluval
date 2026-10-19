# Fluval Plant 4.0 for Home Assistant (ATLAS)

Local Bluetooth control of Fluval Plant 4.0 aquarium lights straight from the
Home Assistant host's own Bluetooth radio — no ESP32, no cloud, no phone app.

Per light: **Power** switch, **Mode** select (Manual / Auto / Pro) and a
**Resume schedule** button (power on + Pro mode in one go — the after-a-power-cut fix).

Connect-on-demand: Home Assistant connects only to send a command or for a
status check every 15 minutes, so the FluvalConnect app still works in between.

Protocol credit: reverse-engineered by
[cryystyy/fluval-plant-pro-4-homeassistant](https://github.com/cryystyy/fluval-plant-pro-4-homeassistant)
(MIT). Not affiliated with Rolf C. Hagen / Fluval.
