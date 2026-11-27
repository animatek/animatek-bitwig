# Bitwig-Mods

Mods y devices propios para **Bitwig Studio** sobre **Patchbay** (BML), el cargador de mods
de shaboogen-dev: cambia el codigo de Bitwig en memoria al arrancar, sin tocar sus archivos.
Empezado el 2026-11-27. Todo es beta: Patchbay no ha llegado a la 1.0.

**Repo publico: `animatek/animatek-bitwig`** (MIT), para que Patchbay Launcher lo lea como
fuente sin login: los temas con la carpeta `themes`, los devices con `devices`. Todo lo que
se publica va en ingles (README, nombres de carpeta); este CLAUDE.md sigue en español.

## Changelog compartido

Al terminar algo relevante: `cambios apuntar "Bitwig-Mods" "<que cambio, verificacion, commit>" -a <agente>`.
Nunca editar `/mnt/SPEED/CODE/CHANGELOG.md` a mano.

## Version de Bitwig: la 6.1.7, no la tuya de diario

Patchbay solo trae mapas para 6.0, 6.0.11, 6.1-6.1.4 y **6.1.7**. La de diario de Javier es la
**6.1.10** y no la reconoce (el sha256 de su `bitwig.jar` no esta en `maps/*/builds.json`).
Por eso hay una 6.1.7 aparte, sacada del .deb de bitwig.com sin instalar nada en el sistema:

- `~/Bitwig-Studio-6.1.7/opt/bitwig-studio/bitwig-studio` — la que usa Patchbay.
- `~/.config/bml/bml.properties` — `bitwig.executable` apunta ahi. El launcher tambien saca
  de ahi su Java (el de Bitwig).
- Con mods solo se arranca **desde Patchbay**. Arrancado normal, Bitwig va sin mods.
- Cuando Patchbay publique mapas para 6.1.10, se cambia la ruta y se puede borrar la 6.1.7.

## Carpetas

| Carpeta | Que es | En Git |
| --- | --- | --- |
| `apps/` | `Patchbay-Launcher/` (0.9.7) y `BML-<ver>-linux/` (Patchbay a pelo). Bajados de sus releases. | no |
| `terceros/` | Clones de referencia: `Patchbay` (loader, modkit, guia en `docs/sdk/`), `Mods`, `patchbay-launcher`, `polarity/bitwig-mods` y `polarity/bitwig-devices`. | no |
| `mods/` | Nuestros mods (cuando los haya). | si |
| `themes/animatek/` | Tema **Animatek** (paleta de la web y de VCV). Se retoca en `generar.py` y `./instalar.sh` lo genera y lo copia a `components/animatek` de la Patchbay activa; luego reiniciar Bitwig desde Patchbay. | si |
| `devices/` | Nuestros `.bwdevice` / `.bwmodulator` / `.bwmodule`. | si |

## Arrancar

Desde el menú de aplicaciones: **Patchbay Launcher** (Multimedia), con `~/.local/share/applications/patchbay-launcher.desktop`.
Si `apps/` cambia de sitio, hay que actualizar esa entrada.

```bash
/mnt/SPEED/CODE/Bitwig-Mods/apps/Patchbay-Launcher/patchbay-launcher   # el launcher (log en ~/.local/share/PatchbayLauncher/logs)
sh /mnt/SPEED/CODE/Bitwig-Mods/apps/BML-0.36.0-dev.17-linux/bml-ui.sh   # Patchbay sin launcher
```

## Escribir mods

Guia: `terceros/Patchbay/docs/sdk/README.md`. Para compilar, las herramientas esperan un
workspace con `BML/`, `Mods/`, `bitwig/jars/<ver>/` y `maps/<build>/` (el zip
`BML-<ver>-workspace-maps.zip` de la release). Necesita JDK 25 con `--release 21` y Python 3.
Para que el launcher encuentre un mod publicado: `<mod-id>-<ver>.zip` en la release,
`<mod-id>/mod.json` en el repo y nombre con categoria (`terceros/patchbay-launcher/docs/PUBLISHING.md`).

## Devices nativos (Nitro)

Se hacen con el blueprint de polarity (`terceros/bitwig-devices-blueprint`): Nitro para el DSP,
SkSL para el panel y el compilador del propio `bitwig.jar` de la 6.1.7. Montado y probado el
2026-11-27 con su ejemplo (Blueprint Gain: preflight PASS y Bitwig lo registra).

- Herramientas: Python 3.12 en `.venv` del blueprint (con `uv`), Rust en `~/.cargo` (rustup, sin
  tocar el PATH: anteponer `$HOME/.cargo/bin`) y `tools/javac25` como `--javac`.
- `build-local-host-tools.py` lo bloqueo una vez el clasificador de Claude Code; Javier autorizo
  lanzarlo.
- Lo construido para probar va a `build/devices/` (fuera de Git), que es la carpeta registrada en
  Patchbay: `~/.config/bml/mods/custom-device-registrar/config.json`. Bitwig se reinicia desde
  Patchbay para que lo vea.
- Primer objetivo: ATEK303 como instrumento nativo. La secuencia vive en el clip: velocidad >= 100
  es accent y notas solapadas son slide (asi lo decide Open303, `rosic_Open303.cpp:193-195`).

## Reglas

- **Nunca** entra en Git nada de Bitwig: ni `bitwig.jar`, ni clases descompiladas, ni mapas.
- Patchbay no es de Bitwig GmbH; nada de lo que se publique puede parecer oficial.
