"""The ATEK303 device document: an event instrument with a Note FX chain before the engine
and an FX chain after it (note in -> Note FX -> Nitro -> FX -> stereo out).

Built from typed structures with the helpers of polarity's bitwig-devices-blueprint. The shape of
the format (proxy order, note port wiring, NoteEvent port record, nested chain slots, panel item
classes) follows what Bitwig writes, as observed in working 6.1.7 devices; nothing is copied
from another device.

The panel follows the layout idea of Bitwig's Polymer: framed sections side by side (oscillator
and sub, filter, envelope and glide) and an output column with the two chains and the levels.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v

# The Polymer look, picked from the Panel Lab (2026-11-27):
POPUP_HEADER = 1          # popup 1: the name in colour with a small arrow, no box ("Union v")
POPUP_STEPPER = 6         # popup 6: "< LP 4 >", as Polymer's filter type
KNOB_MAIN, KNOB_SMALL = 2, 1   # knob 2: light body (main knobs); knob 1 for the small ones
FIELD_TEXT = 1            # field 1: bare coloured text ("0.00 st")
BUTTONS_UNDERLINE = 6     # buttons 6: underlined choice ("0 -1 -2")
TOGGLE_TEXT = 2           # tog 2: text only


# ---------------------------------------------------------------------------------------------
# Parameters, in the order of atek303.nitro's inputs (after note_in).
#   kind "dec": decimal 0-1 knob (audio-rate input); "idx": choice (i32 value input);
#   "bool": on/off (bool value input).
# Preset identifiers of the first eight stay as they were, so saved projects keep their values.
# ---------------------------------------------------------------------------------------------
PARAMETERS = [
    # kind, title, preset id, nitro port, default, tooltip, (min, max) for decimals
    ("dec", "Semi", "SEMI", "semi", 0.0, "Coarse pitch, semitones", -24.0, 24.0),
    ("dec", "Cutoff", "CUTOFF", "cutoff", 0.35, "Filter cutoff, 314-2394 Hz"),
    ("dec", "Resonance", "RESONANCE", "resonance", 0.5, "Filter resonance (linear, as the VR4 pot)"),
    ("dec", "Env", "ENV_MOD", "env_mod", 0.5, "Filter envelope depth (log taper, as the 303 pot)"),
    ("dec", "Decay", "DECAY", "decay", 0.4,
     "Filter envelope decay, 200 ms - 2.5 s as the circuit (accents force the minimum)"),
    ("dec", "Accent", "ACCENT", "accent", 0.5,
     "Accent depth; notes with velocity 100+ are accented, and consecutive accents build up"),
    ("idx", "Wave", "WAVE", "wave_type", [
        "Saw|The 303 ramp: capacitor core with a rounded reset",
        "Square|The 303 comparator square, with its droop; Shape sets the width",
        "Triangle|Skewable triangle; Shape moves the peak"],
     "Saw: the 303 ramp. Square: the circuit's comparator. Triangle: new"),
    ("dec", "Out", "VOLUME", "volume", 0.5, "Output level"),
    ("dec", "Phase", "PHASE", "phase_knob", 0.0, "Start phase of the VCO on each new note, with Retrig on"),
    ("bool", "Retrig", "RETRIG", "retrig", False,
     "On: every new note restarts the VCO at Phase. Off: free-running, as the hardware"),
    ("dec", "Sub", "SUB_LEVEL", "sub_level", 0.0, "Sub-oscillator level"),
    ("idx", "Sub Octave", "SUB_OCTAVE", "sub_octave", ["-1", "-2"], "Sub-oscillator octave"),
    ("idx", "Sub Shape", "SUB_SHAPE", "sub_shape", ["Sine", "Square"], "Sub-oscillator waveform"),
    ("dec", "Slide", "SLIDE", "slide_knob", 0.4, "Slide time, 40-300 ms (overlapping notes slide)"),
    ("dec", "Vel", "VELOCITY", "vel_amount", 0.0, "How much note velocity sets the level"),
    ("dec", "Pan", "PAN", "pan", 0.5, "Pan"),
    ("dec", "Shape", "SHAPE", "shape_knob", 0.44, "Pulse width of the square (the circuit sits at 44 %), skew of the triangle"),
    ("dec", "Sync", "SYNC", "sync_knob", 0.0, "Hard sync: the wave runs up to 36 semitones above the VCO"),
    ("dec", "Fold", "FOLD", "fold_knob", 0.0, "Wavefolder"),
    ("dec", "Fine", "FINE", "fine", 0.0, "Fine pitch, cents", -100.0, 100.0),
    ("dec", "Key", "KEYTRACK", "keytrack", 0.0, "Filter keyboard tracking: how much the notes move the cutoff"),
    ("dec", "Noise", "NOISE", "noise_level", 0.0, "White noise into the filter, with the oscillator"),
    ("bool", "Filter", "FILTER_ON", "filter_on", True, "Filter on; off bypasses it (the oscillator goes straight through)"),
    ("idx", "Ratio", "RATIO", "ratio", ["1:4", "1:2", "1:1", "2:1", "4:1"],
     "Oscillator ratio: two octaves down to two up", 2),
]


def owned(*objects):
    return [{"Object": item} for item in objects]


def settings(connections=()):
    desktop = obj(17, "desktop_settings", {
        "x#17": v("Int16", 0), "y#18": v("Int16", 0),
        "color#19": v("Color", [0.5, 0.5, 0.5, 1.0]),
    })
    return v("Object", obj(236, "component_settings", {
        "desktop_settings#612": v("Object", desktop),
        "inport_connections#614": v("ObjectList", list(connections)),
        "is_polyphonic#615": v("Bool", False),
    }))


def proxy(*, output=False, note=False):
    caption = " Note out" if note else " Audio in (PARENT)" if output else " Audio out (PARENT)"
    port_fields = {
        "name#498": v("String", ""), "description#4741": v("String", ""),
        "decorated_name#499": v("String", caption), "is_inport#500": v("Bool", output),
        "is_optional#1384": v("Bool", False), "exclude_from_graph#7174": v("Bool", False),
    }
    if note:
        port_fields["oversampling#13326"] = v("Byte", 0)
        port = obj(61, "note_port", port_fields)
    else:
        port_fields.update({"channel_count#372": v("Byte", 3), "oversampling#13324": v("Int32", 0)})
        port = obj(242, "audio_port", port_fields)
    return obj(50 if output else 154, "proxy_out_port_component" if output else "proxy_in_port_component", {
        "settings#6194": settings(), "port#301": v("Object", port),
    })


# ---- parameter atoms ------------------------------------------------------------------------

def common_atom_fields(name, ident):
    return {
        "settings#6194": settings(), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "name#374": v("String", name),
        "short_name#821": v("String", name), "preset_identifier#701": v("String", ident),
        "modulations_to_ignore#3826": v("String", ""),
    }


def decimal_atom(name, ident, default, minimum=0.0, maximum=1.0):
    value_type = obj(123, "decimal_value_type", {
        "min#292": v("Double", minimum), "max#293": v("Double", maximum),
        "default_value#891": v("Double", default), "domain#294": v("Byte", 0),
        "engine_domain#295": v("Byte", 0), "value_origin#3014": v("Byte", 0),
        "pixel_step_size#1988": v("Double", -1.0), "unit#296": v("Byte", 0),
        "#297": v("Byte", 2), "parameter_smoothing#4433": v("Bool", True),
        "allow_automation_curves#4434": v("Bool", True),
    })
    return obj(289, "decimal_value_atom", {
        **common_atom_fields(name, ident),
        "value_type#702": v("Object", value_type), "value#712": v("Double", default),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
    })


def indexed_atom(name, ident, items, default_index=0):
    entries = [obj(258, "indexed_value_item", {
        "id#650": v("Byte", index), "name#651": v("String", label.split("|")[0]), "icon#9823": v("String", ""),
        "description#9824": v("String", label.partition("|")[2]), "deprecated#10795": v("Bool", False),
    }) for index, label in enumerate(items)]
    value_type = obj(155, "indexed_value_type", {
        "items#393": v("ObjectList", owned(*entries)), "default_value#6958": v("Byte", default_index),
        "is_periodic#16667": v("Bool", False),
    })
    fields = common_atom_fields(name, ident)
    fields["should_inherit_name#10561"] = v("Bool", False)
    fields = {k: fields[k] for k in ("settings#6194", "channel_count#607", "oversampling#608",
                                     "preset_identifier#701", "name#374", "short_name#821",
                                     "should_inherit_name#10561", "modulations_to_ignore#3826")}
    return obj(180, "indexed_value_atom", {
        **fields, "value_type#702": v("Object", value_type),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
        "value#457": v("Byte", default_index),
    })


def boolean_atom(name, ident, default):
    value_type = obj(198, "boolean_value_type", {
        "icon_name#4755": v("String", ""), "default_value#6957": v("Bool", default),
    })
    fields = common_atom_fields(name, ident)
    fields["should_inherit_name#10561"] = v("Bool", False)
    fields = {k: fields[k] for k in ("settings#6194", "channel_count#607", "oversampling#608",
                                     "preset_identifier#701", "name#374", "short_name#821",
                                     "should_inherit_name#10561", "modulations_to_ignore#3826")}
    return obj(87, "boolean_value_atom", {
        **fields, "value_type#702": v("Object", value_type),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
        "value#210": v("Bool", default),
    })


def make_atom(spec):
    kind, name, ident, _port, default, _tip = spec[:6]
    if kind == "idx":
        return indexed_atom(name, ident, default, spec[6] if len(spec) > 6 else 0)
    if kind == "bool":
        return boolean_atom(name, ident, default)
    return decimal_atom(name, ident, default, *spec[6:8])


# ---- Nitro port descriptors -----------------------------------------------------------------

def nitro_port(name, index, channels, *, output, kind=1):
    return obj(2428, "nitro_port_info", {
        "name#8557": v("String", name), "desc#8558": v("String", ""),
        "channel_count#8559": v("Byte", channels), "index#8560": v("Byte", index),
        "kind#8561": v("Byte", kind), "is_input#8562": v("Bool", not output),
        "is_double_precision#10071": v("Bool", False), "is_compressed_mask#8563": v("Int32", 16777215),
        "is_compressable#8564": v("Bool", False), "event_size#8565": v("Byte", 0),
        "event_type#8566": v("String", ""),
    })


def note_event_port(name, index):
    """A NoteEvent input: kind 2, one channel, 44-byte events."""
    port = nitro_port(name, index, 1, output=False, kind=2)
    port["fields"]["event_size#8565"] = v("Byte", 44)
    port["fields"]["event_type#8566"] = v("String", "NoteEvent")
    return port


# ---- nested device chains -------------------------------------------------------------------

def chain_slot(name, ident, tooltip, connections, *, notes):
    """A nested device chain, as Bitwig's own devices have: notes for Note FX, audio for FX."""
    return obj(587, "nested_device_chain_slot", {
        "settings#6194": settings(connections),
        "preset_identifier#836": v("String", ident), "name#835": v("String", name),
        "tooltip_text#2315": v("String", tooltip), "chain_color#10863": v("Byte", 0),
        "subtrack_sends_count#1374": v("Byte", 0), "sends_access_mode#12052": v("Byte", 0),
        "suggest_audio_input_devices#2435": v("Bool", not notes),
        "suggest_audio_output_devices#5769": v("Bool", not notes),
        "must_have_device_chain#2270": v("Bool", True),
        "suggest_note_input_devices#2434": v("Bool", notes),
        "suggest_note_output_devices#5768": v("Bool", notes),
        "show_mixer_as_subtrack#1373": v("Bool", False), "#2076": v("Bool", False),
        "has_volume_and_pan#2079": v("Bool", False), "#2077": v("Bool", False),
        "has_solo#2220": v("Bool", False), "has_note_led#9926": v("Bool", False),
        "handle_pdc_separately#13583": v("Bool", False),
        "should_devices_in_slot_determine_device_type#5361": v("Bool", False),
    })


# ---- panel ----------------------------------------------------------------------------------

def label(text, x, y, w, h=3, color=6):
    return obj(1683, "label_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "text#6219": v("String", text), "color#6520": v("Int16", color),
        "horizontal_alignment#6400": v("Byte", 1), "vertical_alignment#6401": v("Byte", 1),
        "is_visible#6309": v("Bool", True),
    })


def knob(binding, title, tooltip, x, y, *, size=2, color=6):
    # size 1: small, untitled (10 x 9, with a label above); 2: titled, 19 x 15; 3: big, 21 x 22.
    w, h = {1: (10, 9), 2: (19, 15), 3: (21, 22)}[size]
    if size == 1:
        title = ""
    return obj(1687, "knob_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tooltip),
        "data_model#6220": binding, "title#6241": v("String", title),
        "knob_size#6223": v("Byte", size), "show_value_popup#10569": v("Bool", True),
        "attribute_id#11012": v("Int16", 712),
        "knob_style#7055": v("Byte", KNOB_SMALL if size == 1 else KNOB_MAIN),
        "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", color),
    })


def popup(binding, tooltip, x, y, w, h=5, color=6, style=0, label_style=0):
    return obj(1714, "popup_chooser_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tooltip), "data_model#6220": binding,
        "attribute_id#11012": v("Int16", 457), "label_style#6262": v("Byte", label_style),
        "style#6266": v("Byte", style), "color#7528": v("Int16", color), "help_id#10543": v("String", ""),
    })


def number_field(binding, tooltip, x, y, w, h=4, color=6, style=None):
    # Only the fields whose types are clear; Bitwig fills in the rest, as for older documents.
    return obj(1713, "number_field_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tooltip), "data_model#6220": binding,
        "attribute_id#11012": v("Int16", 712),
        "show_value_bar#6581": v("Bool", False), "color#7526": v("Int16", color),
        **({"style#6540": v("Byte", style)} if style is not None else {}),
    })


def icon_file(name):
    """Bitwig names its icons by path under resources/icons WITH the extension (its own code uses
    "device/keytrack.svg"); without ".svg" the icon is silently not drawn."""
    return name if name.endswith(".svg") else name + ".svg"


def image(filename, x, y, w, h, color=None):
    """One of Bitwig's own icons, by name (resources/icons), tinted with a palette colour.

    The colour is the same kind of attribute as a knob's pie_color (Bitwig's default is 6)."""
    fields = {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "filename#6258": v("String", icon_file(filename)),
    }
    if color is not None:
        fields["color#6521"] = v("Int16", color)
    return obj(1719, "image_panel_item", fields)


def mapping_source(binding, x, y, w, h):
    """The modulation arrow: drag it onto any parameter in Bitwig to modulate it."""
    return obj(1717, "mapping_source_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "data_model#6220": binding,
    })


def modulation_atom(name, ident, connections):
    """A modulation source fed by the Nitro core, as Polymer's envelopes are.

    No display_settings: Bitwig stores it per display (a map keyed by display name), and writing
    it as a plain object makes the device fail to load and Bitwig crash (2026-11-27)."""
    return obj(766, "modulation_source_atom", {
        "settings#6194": settings(connections), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "name#374": v("String", name),
        "preset_identifier#701": v("String", ident),
    })


def drawing_item(binding, x, y, w, h):
    return obj(5517, "", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", ""), "help_id#10543": v("String", ""),
        "help_location#10546": v("Byte", 0), "data_model#6220": binding,
    })


def button_group(binding, tooltip, x, y, w, h=4, style=BUTTONS_UNDERLINE):
    return obj(1712, "button_group_chooser_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tooltip), "help_id#10543": v("String", ""),
        "help_location#10546": v("Byte", 0), "data_model#6220": binding,
        "attribute_id#11012": v("Int16", 457), "is_horizontal#6255": v("Bool", True),
        "break_count#6256": v("Byte", 0), "label_style#6257": v("Byte", 0),
        "button_style#7548": v("Byte", style), "color#10143": v("Int16", 0),
    })


def toggle(binding, title, tooltip, x, y, w, h=5):
    return obj(1702, "toggle_button_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "data_model#6220": binding, "attribute_id#11012": v("Int16", 255),
        "title#6241": v("String", title), "tooltip_text#6867": v("String", tooltip),
        "icon_name#6239": v("String", ""), "style#6240": v("Byte", TOGGLE_TEXT),
        "label_style#6267": v("Byte", 0), "invert_value#6552": v("Bool", False),
        "is_selected#6719": v("Bool", False), "color#7527": v("Int16", 999),
        "font#7530": v("Byte", 0),
    })


def chain_display(binding, x, y, w, h):
    return obj(1704, "component_display_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "data_model#6220": binding,
    })


def section(items, x, y, w, h):
    """A framed section, as Bitwig nests them: child positions are relative to the frame."""
    return obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, w, h)),
        "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 1), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6),
        "brightness#6245": v("Byte", SECTION_BRIGHTNESS),
    })


PANEL_WIDTH, PANEL_HEIGHT = 204, 53
# Frame brightness: 3 came out black; 0 should be the device background (#1B1F2A) or close to it.
SECTION_BRIGHTNESS = 0
# Bitwig's panel palette, as seen on screen (2 yellow, 4 blue, 5 purple, 1 orange): a rainbow,
# so 0 should be red, 3 green and 6 grey. Polymer colours: amber oscillator, green-teal filter,
# blue envelope, red output.
OSC_COLOR, FILTER_COLOR, ENV_COLOR, OUT_COLOR = 1, 3, 4, 0


def main_panel(ref_of, note_fx_ref, fx_ref, drawing_ref, mod_ref=None):
    """The panel, from layout.json (edited with tools/panel_editor.py)."""
    layout = json.loads((Path(__file__).parent / "layout.json").read_text(encoding="utf-8"))
    specs = {spec[2]: spec for spec in PARAMETERS}
    chains = {"NOTE_FX": note_fx_ref, "FX": fx_ref}

    def build(it):
        kind, x, y = it["type"], it["x"], it["y"]
        w, h = it.get("w"), it.get("h")
        spec = specs.get(it.get("param"))
        binding = ref_of.get(it.get("param"))
        tooltip = spec[5] if spec else ""
        color = it.get("color", 6)
        if kind == "knob":
            return knob(binding, it.get("title", spec[1]), tooltip, x, y, size=it.get("size", 2), color=color)
        if kind == "label":
            return label(it["text"], x, y, w, h or 3, color=color)
        if kind == "popup":
            return popup(binding, tooltip, x, y, w, h or 5, color=color, style=it.get("style", POPUP_HEADER))
        if kind == "field":
            return number_field(binding, tooltip, x, y, w, h or 4, color=color, style=it.get("style", FIELD_TEXT))
        if kind == "buttons":
            return button_group(binding, tooltip, x, y, w, h or 4, style=it.get("style", BUTTONS_UNDERLINE))
        if kind == "toggle":
            t = toggle(binding, it.get("title", spec[1]), tooltip, x, y, w, h or 5)
            t["fields"]["style#6240"] = v("Byte", it.get("style", TOGGLE_TEXT))
            if it.get("icon"):
                t["fields"]["icon_name#6239"] = v("String", icon_file(it["icon"]))
            return t
        if kind == "chain":
            return chain_display(chains[it["chain"]], x, y, w, h)
        if kind == "drawing":
            return drawing_item(drawing_ref, x, y, w, h)
        if kind == "icon":
            return image(it["icon"], x, y, w or 3, h or 3, it.get("color"))
        if kind == "modsource":
            return mapping_source(mod_ref, x, y, w or 4, h or 3)
        raise ValueError(f"layout.json: unknown item type {kind!r}")

    sections = [section([build(it) for it in sec["items"]], sec["x"], sec["y"], sec["w"], sec["h"])
                for sec in layout["sections"]]
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"),
        "items#6221": v("ObjectList", owned(*sections)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6),
        "brightness#6245": v("Byte", 1),
    })
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", layout["panel"]["width"]), "height#6233": v("Byte", layout["panel"]["height"]),
        "expressions#6277": v("ObjectList", []),
    })


# Value ranges of Bitwig 6.1.7's panel enums (from its own definitions; an index past the end is
# "Unknown enum value" and the device does not load). Order inside each enum is what the Lab shows.
POPUP_STYLES = 9          # BUTTON, DISPLAY, FLAT, PLAIN, STEPPER, UNDERLINE, VALUE_FIELD(_HOVER/_IN_DISPLAY)
BUTTON_STYLES = 7         # BUTTON, CHECKBOX, BORDERLESS_BUTTON/_HOVER, UNDERLINE, DISPLAY_BUTTON, INSIDE_DISPLAY
KNOB_STYLES = 4           # NORMAL, DARKEST, LIGHTER, LIGHTEST
NUMBER_FIELD_STYLES = 3   # NORMAL, WHITE, IN_DISPLAY


ICON_FORMATS = ["device/power_on", "device/power_on.svg", "power_on", "icons/device/power_on.svg"]


def lab_panel(ref_of, mod_ref=None):
    """Panel Lab 2: icon name formats, toggles with icons and the modulation arrow."""
    items = [label("Lab 2: iconos, botones con icono y flecha de modulacion", 2, 0, 120)]
    for i, name in enumerate(ICON_FORMATS):
        x = 2 + i * 50
        items += [label(f"img {i}: {name}", x, 4, 48), image(name, x + 20, 8, 4, 4)]
    for i, name in enumerate(ICON_FORMATS):
        x = 2 + i * 50
        t = toggle(ref_of["FILTER_ON"], "", f"icon {name}", x + 18, 22, 8, 5)
        t["fields"]["icon_name#6239"] = v("String", name)
        items += [label(f"tog {i}", x, 17, 48), t]
    items += [label("flecha", 2, 33, 20), mapping_source(mod_ref, 8, 37, 5, 4),
              label("ratio (popup 7)", 30, 33, 30), popup(ref_of["RATIO"], "", 34, 37, 14, color=1, style=7)]
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6),
        "brightness#6245": v("Byte", 1),
    })
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", 206), "height#6233": v("Byte", 53),
        "expressions#6277": v("ObjectList", []),
    })


def metadata(project, revision):
    identity = project["identity"]
    tags = project["presentation"]["tags"]
    fields = {
        "application_version_name": v("String", project["target"]["bitwigVersion"]),
        "creator": v("String", identity["creator"]), "device_creator": v("String", identity["creator"]),
        "device_category": v("String", identity["category"]),
        "device_description": v("String", project["presentation"]["description"]),
        "device_id": v("String", identity["uuid"]), "device_uuid": v("Uuid", identity["uuid"]),
        "device_name": v("String", project["name"]), "device_type": v("String", "note_to_audio"),
        "has_audio_input": v("Bool", False), "has_audio_output": v("Bool", True),
        "has_note_input": v("Bool", True), "has_note_output": v("Bool", False),
        "preset_name": v("String", project["name"]), "revision_id": v("String", revision),
        "revision_no": v("Int32", 1), "suggest_for_audio_input": v("Bool", False),
        "suggest_for_note_input": v("Bool", True), "tags": v("String", tags),
        "type": v("String", "application/bitwig-device"),
    }
    return {**obj(4, "meta", fields), "wide_names": [False] * len(fields)}


def document(project, binary, *, note_fx_output_port=1, lab=False):
    shader = (Path(__file__).parent / "osc_display.sksl").read_text(encoding="utf-8")
    bindings = []

    def ref(target, *, list_entry=False):
        key = "ObjectRef" if list_entry else "value"
        wrapper = {"ObjectRef": 0} if list_entry else v("ObjectRef", 0)
        bindings.append((wrapper, key, target))
        return wrapper

    def wire(target, port=0):
        entry = connection(port=port)
        entry["Object"]["fields"]["source_component#248"] = ref(target)
        return entry

    # Root proxies first, as Bitwig writes them: audio then note.
    audio_proxy = proxy()
    note_proxy = proxy(note=True)
    audio_source = obj(2000, "audio_source_atom", {
        "settings#6194": settings([wire(audio_proxy)]), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "port_color#10378": v("Int16", 999),
        "name#3639": v("String", "In"), "preset_identifier#3640": v("String", "IN"),
    })
    atoms = [make_atom(spec) for spec in PARAMETERS]
    ref_of = {}

    # Note FX: the incoming notes go through a nested note chain before the engine.
    note_fx = chain_slot("Note FX", "NOTE_FX", "Note effects before ATEK303",
                         [wire(audio_proxy), wire(note_proxy)], notes=True)

    inputs = [note_event_port("note_in", 0)]
    for index, (kind, _name, _ident, port, *_rest) in enumerate(PARAMETERS, 1):
        inputs.append(nitro_port(port, index, 1, output=False, kind=1 if kind == "dec" else 3))
    dsp = obj(1721, "nitro_atom", {
        "settings#6194": settings([wire(note_fx, note_fx_output_port), *(wire(a) for a in atoms)]),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0),
        "nitro_inputs#15756": v("ObjectList", owned(*inputs)),
        "nitro_outputs#15757": v("ObjectList", owned(
            nitro_port("out", 0, 2, output=True), nitro_port("display", 1, 4, output=True),
            nitro_port("mod_out", 2, 1, output=True),
        )),
        "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
    })
    # The envelope + accent modulation source, only when the panel shows its arrow.
    layout = json.loads((Path(__file__).parent / "layout.json").read_text(encoding="utf-8"))
    wants_mod = lab or any(it["type"] == "modsource" for sec in layout["sections"] for it in sec["items"])
    mod = modulation_atom("Env + Accent", "ENV_MOD_OUT", [wire(dsp, 2)]) if wants_mod else None

    # FX: an audio chain after the engine, as in Polymer.
    fx = chain_slot("FX", "FX", "Audio effects after ATEK303", [wire(dsp, 0), wire(note_proxy)], notes=False)

    # The oscillator drawing: an SkSL shader fed by the core's four-lane display output.
    drawing = obj(5512, "", {
        "settings#6194": settings([wire(dsp, 1), *(connection() for _ in range(8))]),
        "channel_count#607": v("Byte", 0), "name#374": v("String", ""),
        "prevent_parent_from_sleeping#11002": v("Bool", False),
        "preset_identifier#701": v("String", "OSC_DRAWING"), "#16316": v("WideString", shader),
    })

    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(fx, 0)])

    for spec, atom in zip(PARAMETERS, atoms):
        ref_of[spec[2]] = ref(atom)
    mod_ref = ref(mod) if mod else None
    panel = lab_panel(ref_of, mod_ref) if lab else main_panel(ref_of, ref(note_fx), ref(fx), ref(drawing), mod_ref)

    identity = project["identity"]
    tags = project["presentation"]["tags"]
    body = obj(151, "device_contents", {
        "proxy_in_ports#177": v("ObjectList", owned(audio_proxy, note_proxy)),
        "child_components#173": v("ObjectList", owned(audio_source, *atoms, note_fx, dsp, drawing, *([mod] if mod else []), fx)),
        "panels#6213": v("ObjectList", owned(panel)),
        "proxy_out_ports#178": v("ObjectList", owned(output_proxy)),
        "device_UUID#385": v("Uuid", identity["uuid"]), "device_name#386": v("String", project["name"]),
        "description#2057": v("String", project["presentation"]["description"]),
        "creator#387": v("String", identity["creator"]), "category#390": v("String", identity["category"]),
        "suggest_for_note_input#4846": v("Bool", True), "suggest_for_audio_input#4847": v("Bool", False),
        "settings#6194": v("NullObject"), "fft_order#6566": v("Byte", 0),
        "analysis_fft_order#11047": v("Byte", 11), "analysis_fft_fall_speed#11110": v("Byte", 1),
        "device_revision#13647": v("Byte", 1), "sleep_level_threshold#1977": v("Double", -96.0),
        "sleep_level_timeout#1978": v("Double", 0.05), "prevent_sleep#14608": v("Bool", False),
        "comment#388": v("String", ""), "keywords#389": v("String", tags),
        "device_type#391": v("Byte", 2), "has_been_modified#392": v("Bool", True),
        "color_tint#13354": v("Color", [0.0, 0.0, 0.0, 0.0]),
    })
    object_ids = {id(item): index for index, item in enumerate(iter_owned_objects(body), 1)}
    for wrapper, key, target in bindings:
        wrapper[key] = object_ids[id(target)]

    revision = hashlib.sha1(f"{identity['uuid']}/{project['version']}".encode("utf-8")).hexdigest()
    return {
        "header": {"format_version": 3, "serialization_format": 2, "document_version": 207,
                   "object_offset": 0, "resources_offset": 0, "flags": 0},
        "metadata": metadata(project, revision), "body": body,
        "meta_nonce": "0" * 32, "body_nonce": "0" * 32,
    }
