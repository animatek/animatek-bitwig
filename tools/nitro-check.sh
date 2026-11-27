#!/bin/sh
# Analisis semantico de Bitwig 6.1.7 sobre fuentes .nitro, sin abrir Bitwig.
# El probe del blueprint solo esta montado para Windows, pero los nombres ofuscados del
# bitwig.jar de Linux 6.1.7 son los mismos: el frontend windows-6.1.7 funciona aqui.
#   tools/nitro-check.sh devices-src/atek303/atek303.nitro
set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
B="$HOME/Bitwig-Studio-6.1.7/opt/bitwig-studio"
PROBE="$HERE/build/nitro-probe"
if [ ! -f "$PROBE/NitroSemanticProbe.class" ]; then
  mkdir -p "$PROBE"
  "$HERE/tools/javac25" -cp "$B/bin/bitwig.jar:$B/bin/libs.jar" -d "$PROBE" \
    "$HERE/terceros/bitwig-devices-blueprint/tools/host_compiler/NitroSemanticProbe.java"
fi
"$B/lib/jre/bin/java" -DinstallationRoot="$B" -Dnitro.frontend=windows-6.1.7 \
  -cp "$PROBE:$B/bin/bitwig.jar:$B/bin/libs.jar" NitroSemanticProbe "$@" 2>&1 | grep -v "nitro warning"
