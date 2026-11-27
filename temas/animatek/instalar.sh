#!/bin/sh
# Genera el tema y lo copia a components/animatek de la Patchbay activa del launcher.
set -e
AQUI=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DATA="${XDG_DATA_HOME:-$HOME/.local/share}/PatchbayLauncher"
VER=$(cat "$DATA/current.txt")
DEST="$DATA/installs/BML-$VER-linux/components/animatek"
python3 -I "$AQUI/generar.py"
mkdir -p "$DEST/resources"
cp "$AQUI/mod.json" "$DEST/"
cp "$AQUI/resources/animatek.bte" "$DEST/resources/"
echo "Instalado en $DEST"
