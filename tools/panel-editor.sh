#!/bin/sh
# Abre el editor de paneles (http://127.0.0.1:4310) para un device; por defecto ATEK303.
#   tools/panel-editor.sh [devices-src/<device>]
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec "$HERE/terceros/bitwig-devices-blueprint/.venv/bin/python" "$HERE/tools/panel_editor.py" "$@"
