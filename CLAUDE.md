# Bitwig-Mods

Mods y devices propios para **Bitwig Studio** sobre **Patchbay** (BML), el cargador de mods
de shaboogen-dev: cambia el codigo de Bitwig en memoria al arrancar, sin tocar sus archivos.
Empezado el 2026-11-27. Todo es beta: Patchbay no ha llegado a la 1.0.

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

## Reglas

- **Nunca** entra en Git nada de Bitwig: ni `bitwig.jar`, ni clases descompiladas, ni mapas.
- Patchbay no es de Bitwig GmbH; nada de lo que se publique puede parecer oficial.
