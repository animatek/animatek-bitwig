#!/bin/sh
# Genera el tema y lo copia a components/animatek de la Patchbay activa del launcher.
set -e
AQUI=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DATA="${XDG_DATA_HOME:-$HOME/.local/share}/PatchbayLauncher"
VER=$(cat "$DATA/current.txt")
DEST="$DATA/installs/BML-$VER-linux/components/animatek"
python3 -I "$AQUI/generar.py"
# El .bte va en la raiz de la carpeta: el launcher solo ve los temas locales asi.
rm -rf "$DEST"
mkdir -p "$DEST"
cp "$AQUI/mod.json" "$AQUI/animatek.bte" "$DEST/"
echo "Instalado en $DEST"
