#!/usr/bin/env python3
"""Genera resources/animatek.bte, el tema de Animatek para Framework: Themes de Patchbay.

La paleta sale de la web (tema de WordPress) y de los paneles de los modulos de VCV
(UZZ-VCV-RACK): pizarras #33384A / #0D0F13, textos #9AA2B5 / #D0D6E0, azul #2C7FFF,
ambar #FD9A00, verde #24B979 y rojo #FF3B3B. Para retocar: cambiar aqui y volver a
ejecutar `./instalar.sh`, que lo genera y lo copia a la Patchbay activa.
"""
from pathlib import Path

# --- Paleta -----------------------------------------------------------------
# Pizarras, de la mas honda a la mas clara (Grey 0..6 de Bitwig). G6 es el panel de VCV.
G0, G1, G2, G3, G4, G5, G6 = "#0D0F13", "#14161C", "#1A1D25", "#1F232C", "#262B36", "#2E3340", "#33384A"
G7, G8 = "#3D4357", "#4A5168"          # pizarras claras: separadores, scroll, campos
NEGRO = "#000000"

TXT = "#E2E8F0"        # texto principal (web, modo oscuro)
TXT_2 = "#D0D6E0"      # texto de VCV
TXT_3 = "#9AA2B5"      # secundario (etiquetas de VCV)
TXT_4 = "#8A95A8"
TXT_5 = "#5A6375"      # sutil

AZUL = "#2C7FFF"       # marca
AZUL_H = "#1C63D9"     # hover de la web
AZUL_C = "#5C9DFF"     # azul claro para lineas sobre fondo oscuro
AMBAR = "#FD9A00"
AMBAR_C = "#FFB84D"
VERDE = "#24B979"
ROJO = "#FF3B3B"
ROJO_S = "#E5484D"     # rojo algo mas suave para avisos
AMARILLO = "#FFC93C"
MORADO = "#8B6CFF"
TURQUESA = "#22B8CF"
CIAN = "#22D3EE"       # pantalla del transporte (Accent hitech)
MENTA = "#2BB5A0"
LIMA = "#9BC53D"
ROSA = "#E36BA8"


def a(color: str, alpha: str) -> str:
    """Color con alfa en hex (dos cifras), como lo escribe Bitwig Theme Editor."""
    return color[:7] + alpha


TEMA = {
    # Fondos y pizarras
    "Window background": G0,
    "Grey 0": G0, "Grey 1": G1, "Grey 2": G2, "Grey 3": G3,
    "Grey 4": G4, "Grey 5": G5, "Grey 6": G6,
    "Display Background": G0,
    "Display Background (error)": "#3A1C20",
    "Grey Display Background": a(G0, "55"),
    "The Grid (background)": G0,
    "The Grid (stroke)": G2,
    "Dark Panel Sub-frame Fill": G2,
    "Dark Panel Sub-frame Stroke": G4,
    "Panel Stroke (focused)": AZUL,
    "Device Header": G3,
    "Device Header (selected)": G6,
    "List Item Background": G2,
    "Tree Item Background": G2,
    "Tree Separator": "#00000000",
    "List Separator": G5,
    "Light Separator Line": G8,
    "Dark tree separator": G5,
    "Dark tree background (selected)": G6,
    "Dark tree background (standby selected)": G4,
    "Dark tree hover background change": a(TXT, "0A"),
    "Selected Dashboard Tree": G4,
    "Shadow": "#00000055",
    "Dark offset for automation/channel bar": "#00000026",
    "Light offset for automation/channel bar": a(TXT, "1E"),

    # Texto
    "Default text": TXT,
    "Dark Text": TXT_2,
    "Light Text": TXT,
    "Lighter Text": "#F4F4F5",
    "Medium Light Text": TXT,
    "Subtle Dark Text": TXT_3,   # texto de las notificaciones: con TXT_5 no se leia
    "Subtle Light Text": a(TXT, "99"),
    "Subtler Light Text": a(TXT, "66"),
    "Dark tree text": TXT_2,
    "Dark tree text (selected)": "#FFFFFF",
    "Link Text": AZUL_C,
    "Error Text": a(ROJO_S, "E0"),
    "Menu text": TXT,
    "Menu description text": TXT_4,
    "Menu Icon": TXT_3,
    "Menu background": G2,
    "Menu separator": G5,
    "Menu stroke": G0,

    # Acento: azul de marca; el ambar queda para modulacion y lo que "se mueve"
    "Accent (default)": AZUL,
    "Accent (hitech)": CIAN,     # tempo, posicion y tonalidad de la barra de arriba
    "Implicit On (subtle)": AZUL_H,
    "Knob Value Color": AZUL,
    "Led On": AZUL,
    "Led Off": G6,
    "Progress bar": AZUL,
    "Progress background": a(G4, "BB"),
    "Drop Indicator": AZUL_C,
    "White Selection": "#FFFFFF",
    "White Selection (standby)": a(TXT, "66"),
    "Device Locked Overlay": a(AZUL, "40"),
    "Comp fill": a(AZUL, "44"),

    # Botones y campos (pildoras de la web: primario azul)
    "Abstract Button Pressed Background": AZUL_H,
    "Abstract Button Selected Background": G7,
    "Abstract Button Stroke": G1,
    "Abstract Button Unselected Background": G3,
    "Button background": a(G5, "90"),
    "Button in tree background": G4,
    "Button stroke": G0,
    "Pressed button background": a(AZUL, "70"),
    "View button background": "#00000000",
    "Pressed view button background": G4,
    "Inverted Selected Borderless Button background": G7,
    "OK Button background": AZUL,
    "Checkbox background": a(G7, "90"),
    "Field background": G4,
    "Number field bar background": G7,
    "Close button mouse over background": "#0000004A",
    "Close button pressed background": "#00000090",
    "Timeline edit tool chooser background": G4,

    # Iconos de conmutadores
    "Normal Toggle Icon": TXT_3,
    "Mouse Over Toggle Icon": TXT_2,
    "Pressed Toggle Icon": TXT,
    "Active Toggle Icon (Playing)": "#FFFFFF",
    "Normal Inverted Toggle Icon": "#00000044",
    "Mouse Over Inverted Toggle Icon": "#00000088",
    "Pressed Inverted Toggle Icon": NEGRO,
    "Active Inverted Toggle Icon (Playing)": "#FFFFFF",

    # Mandos (como los de VCV: cuerpo pizarra, linea clara)
    "Knob Body Darkest": G2,
    "Knob Body Lighter": "#7E879C",
    "Knob Body Lightest": "#B4BCCB",
    "Knob Emboss Highlight": a(TXT, "1E"),
    "Knob Emboss Shadow": "#00000040",
    "Knob Line": "#F4F4F5",
    "Knob Line Dark": "#0A0A0A",
    "Knob Stroke": G5,
    "Brighter": "#7E879C",

    # Scroll
    "Scrollbar": G8,
    "Scrollbar background": "#00000000",
    "Modern Scrollbar Background (active)": a(G8, "33"),
    "Modern Scrollbar Handle (active)": "#6B7489",
    "Modern Scrollbar Handle (inactive)": a("#6B7489", "88"),
    "Modern Dark Scrollbar Handle (active)": "#000000FF",
    "Modern Dark Scrollbar Handle (inactive)": "#00000088",

    # Tooltips, notificaciones y ventanas emergentes
    "Tooltip Background": G3,
    "Tooltip Stroke": G7,
    "Light Tooltip Background": TXT_2,
    "Notification Background": G3,
    "Notification Normal": AZUL,
    "Notification Error": ROJO_S,
    "Popup Notification Background": "#000000AA",
    "Popup insert": G7,
    "Popup overlay background color": a(G0, "CC"),
    "Hitcount background": a(G7, "66"),
    "Hitcount text color": a(TXT_2, "88"),
    "Warning": AMBAR,

    # Activacion y estados
    "Activation Green": VERDE,
    "Activation Red": ROJO,
    "Activation Yellow": AMBAR,
    "Record button color": ROJO,
    "Monitoring buttons color": AMBAR,
    "User Automation Override Color": VERDE,

    # Medidores
    "Meter Normal": VERDE,
    "Meter Yellow": AMBAR,
    "Meter Red": ROJO_S,
    "Meter Clipping": ROJO,
    "Meter Gain Reduction": AZUL_C,
    "Meter Hitech": AZUL,
    "Meter Hitech Background": a(AZUL, "1E"),
    "Meter Muted": TXT_5,

    # Modulacion: ambar
    "Modulation Mapping Color": AMBAR,
    "Modulation Mapping Color (polyphonic)": AMBAR_C,
    "Modulation Mapping Color (subtractive)": TXT_5,
    "Modulation Mapping Background (monophonic)": a(AMBAR, "44"),
    "Modulation Mapping Background (polyphonic)": a(AMBAR_C, "44"),
    "Mapping": AMBAR,
    "Launcher Mapping Indication": TXT_4,
    "Automation Color": AMBAR_C,

    # Indicadores de mapeo (8 colores distintos)
    "Mapping indication 1": ROJO_S,
    "Mapping indication 2": AMBAR,
    "Mapping indication 3": AMARILLO,
    "Mapping indication 4": LIMA,
    "Mapping indication 5": VERDE,
    "Mapping indication 6": AZUL,
    "Mapping indication 7": MORADO,
    "Mapping indication 8": ROSA,

    # Colores de panel de los devices
    "Panel Blue": AZUL,
    "Panel Green": VERDE,
    "Panel Lime": LIMA,
    "Panel Mint": MENTA,
    "Panel Orange": AMBAR,
    "Panel Purple": MORADO,
    "Panel Red": ROJO_S,
    "Panel Turquoise": TURQUESA,
    "Panel Yellow": AMARILLO,

    # Colores de producto de Bitwig
    "Bitwig 16-Track": AZUL,
    "Bitwig 8-Track": MENTA,
    "Bitwig CI": AMBAR,
    "Bitwig Essentials": AZUL,
    "Bitwig Mint": MENTA,
    "Bitwig Producer": AMARILLO,
    "Bitwig Red": ROJO_S,

    # Tintes de device
    "Device Tint Future": a(AZUL, "40"),
    "Device Tint Military": a(VERDE, "33"),
    "Device Tint Retro": a(AMBAR, "33"),

    # Audio, ondas y marcadores
    "Audio Event Background": G2,
    "Audio Event Boundary": "#00000055",
    "Audio Event Waveform": TXT_2,
    "Display Waveform": TXT,
    "Display Stroke": "#00000030",
    "Display Loop Markers": AZUL,
    "Display Start/End Markers": AMBAR,
    "Analyzed Beat Color": AZUL_C,
    "Beat Marker Color": AZUL_C,
    "Onset Color Max": "#FFE0A3",
    "Onset Color Min": AMBAR_C,
    "Grid Line (Primary)": "#000000FF",
    "Grid Line (Secondary)": "#00000040",

    # Linea de tiempo y selecciones
    "Header Loop Region Background": "#00000022",
    "Loop Region Background": a(TXT, "18"),
    "Header Time Selection Across All Lanes Fill": a(G6, "CC"),
    "Header Time Selection Across All Lanes Stroke": TXT_2,
    "Header Time Selection Cursor Stroke": TXT_2,
    "Header Time Selection Fill": a(G4, "CC"),
    "Header Time Selection Standby Cursor Stroke": TXT_2,
    "Header Time Selection Standby Fill": a(TXT, "06"),
    "Header Time Selection Standby Stroke": TXT_3,
    "Header Time Selection Stroke": TXT,
    "Time Selection Across All Lanes Fill": a(AZUL, "AA"),
    "Time Selection Across All Lanes Stroke": TXT,
    "Time Selection Cursor Stroke": "#FFFFFF",
    "Time Selection Fill": a(AZUL, "55"),
    "Time Selection Inactive Fill": a(TXT, "0A"),
    "Time Selection Inactive Stroke": a(TXT, "1A"),
    "Time Selection Not Selected Fill": "#00000000",
    "Time Selection Not Selected Stroke": "#00000000",
    "Time Selection Standby Cursor Stroke": TXT,
    "Time Selection Standby Fill": a(TXT, "33"),
    "Time Selection Standby Stroke": "#00000000",
    "Time Selection Stroke": TXT,
    "Timeline Cue Marker": G8,
    "Timeline Header Background Pattern": a(TXT, "0A"),
    "Timeline Header Cue Marker": G8,
    "Timeline Header Tooltip Background": a(G4, "CC"),
    "Timeline Header Tooltip Text": TXT_2,
    "Timeline Tooltip Background": a(G7, "CC"),
    "Timeline Tooltip Text": TXT,
}

CABECERA = """\
// Animatek para Bitwig Studio: tema para Framework: Themes de Patchbay.
// Paleta de animatek.net y de los modulos de VCV: pizarras, azul #2C7FFF y ambar #FD9A00.
// Generado por generar.py: no editar a mano.
Gradient: true
"""


def main() -> None:
    aqui = Path(__file__).resolve().parent
    salida = aqui / "resources" / "animatek.bte"
    salida.parent.mkdir(exist_ok=True)
    lineas = [f"{nombre}: {color}" for nombre, color in TEMA.items()]
    salida.write_text(CABECERA + "\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(TEMA)} colores -> {salida}")


if __name__ == "__main__":
    main()
