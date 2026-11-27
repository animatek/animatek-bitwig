# Animatek for Bitwig

Themes, devices and mods for [Bitwig Studio](https://www.bitwig.com) by [Animatek](https://animatek.net), made for [Patchbay](https://github.com/shaboogen-dev/Patchbay), the mod loader, and installable with [Patchbay Launcher](https://github.com/arius77R/patchbay-launcher).

> Unofficial. Not made by or affiliated with Bitwig GmbH, the authors of Patchbay or Patchbay Launcher. Bitwig and Bitwig Studio are trademarks of Bitwig GmbH.

## Themes

| Theme | What it looks like |
|---|---|
| [`animatek`](themes/animatek) | Slate greys, Animatek blue `#2C7FFF` as the accent, amber `#FD9A00` for modulation and automation, cyan `#22D3EE` on the transport display. The palette of animatek.net and of the Animatek VCV Rack modules. |

Themes need Patchbay's **Framework: Themes**. Tested on Bitwig Studio 6.1.7 (Linux).

### Install with Patchbay Launcher

In **Sources**, add this repository (`animatek/animatek-bitwig`) as a **Themes** source with the folder `themes`. The themes then appear under **Themes**: install one, choose **Use this theme** with Patchbay closed and start Bitwig from Patchbay.

### Install by hand

Copy the theme's folder (for example `themes/animatek`) into the `components/` folder of your Patchbay install, select it under **Framework: Themes** in Patchbay and start Bitwig from Patchbay.

## Devices

`devices/` will hold `.bwdevice`, `.bwmodulator` and `.bwmodule` presets. Nothing yet.

## Mods

`mods/` will hold Patchbay mods. Nothing yet.

## For contributors

Each theme's `.bte` is generated: edit its `generar.py` and run `./instalar.sh`, which writes the `.bte` and copies the theme into the active Patchbay of Patchbay Launcher. Nothing from Bitwig (its jar, decompiled code or Patchbay's maps) goes into this repository.

## License

[MIT](LICENSE)
