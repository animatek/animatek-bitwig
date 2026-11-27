"""The ATEK303 device document: an event instrument (note in -> Nitro -> stereo out).

Built from typed structures with the helpers of polarity's bitwig-devices-blueprint. The shape of
an event instrument (proxy order, note port wiring, NoteEvent port record) follows the format as
observed in a working 6.1.7 instrument; nothing is copied from another device.
"""
from __future__ import annotations

import hashlib

from devices.common.document_graph import iter_owned_objects
from devices.common.panel_helpers import connection, grid_layout, obj, value as v

PANEL_WIDTH, PANEL_HEIGHT = 76, 53


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


def decimal_parameter(name, ident, *, minimum, maximum, default):
    value_type = obj(123, "decimal_value_type", {
        "min#292": v("Double", minimum), "max#293": v("Double", maximum),
        "default_value#891": v("Double", default), "domain#294": v("Byte", 0),
        "engine_domain#295": v("Byte", 0), "value_origin#3014": v("Byte", 0),
        "pixel_step_size#1988": v("Double", -1.0), "unit#296": v("Byte", 0),
        "#297": v("Byte", 2), "parameter_smoothing#4433": v("Bool", True),
        "allow_automation_curves#4434": v("Bool", True),
    })
    return obj(289, "decimal_value_atom", {
        "settings#6194": settings(), "channel_count#607": v("Byte", 0),
        "oversampling#608": v("Byte", 0), "name#374": v("String", name),
        "short_name#821": v("String", name), "preset_identifier#701": v("String", ident),
        "modulations_to_ignore#3826": v("String", ""),
        "value_type#702": v("Object", value_type), "value#712": v("Double", default),
        "allow_automation#7489": v("Bool", True), "allow_modulation#7490": v("Bool", True),
    })


def nitro_port(name, index, channels, *, output):
    return obj(2428, "nitro_port_info", {
        "name#8557": v("String", name), "desc#8558": v("String", ""),
        "channel_count#8559": v("Byte", channels), "index#8560": v("Byte", index),
        "kind#8561": v("Byte", 1), "is_input#8562": v("Bool", not output),
        "is_double_precision#10071": v("Bool", False), "is_compressed_mask#8563": v("Int32", 16777215),
        "is_compressable#8564": v("Bool", False), "event_size#8565": v("Byte", 0),
        "event_type#8566": v("String", ""),
    })


def note_event_port(name, index):
    """A NoteEvent input: kind 2, one channel, 44-byte events."""
    port = nitro_port(name, index, 1, output=False)
    port["fields"]["kind#8561"] = v("Byte", 2)
    port["fields"]["event_size#8565"] = v("Byte", 44)
    port["fields"]["event_type#8566"] = v("String", "NoteEvent")
    return port


# (name, preset id, nitro port, default, tooltip) in the order of atek303.nitro's inputs.
PARAMETERS = [
    ("Tuning", "TUNING", "tuning", 0.5, "Master tuning, 400-480 Hz for A4"),
    ("Cutoff", "CUTOFF", "cutoff", 0.35, "Filter cutoff, 314-2394 Hz"),
    ("Resonance", "RESONANCE", "resonance", 0.5, "Filter resonance (linear, as the VR4 pot)"),
    ("Env Mod", "ENV_MOD", "env_mod", 0.5, "Filter envelope depth (log taper, as the 303 pot)"),
    ("Decay", "DECAY", "decay", 0.4, "Filter envelope decay, 200 ms - 2.5 s as the circuit (accents force the minimum)"),
    ("Accent", "ACCENT", "accent", 0.5, "Accent depth; notes with velocity 100+ are accented, and consecutive accents build up"),
    ("Waveform", "WAVEFORM", "waveform", 0.0, "Saw (0) to square (1), blended"),
    ("Volume", "VOLUME", "volume", 0.5, "Output level"),
]

KNOB_W, KNOB_H = 18, 22


def knob(binding, title, tooltip, x, y):
    return obj(1687, "knob_panel_item", {
        "layout_settings#6226": v("Object", grid_layout(x, y, KNOB_W, KNOB_H)),
        "is_visible#6309": v("Bool", True), "is_enabled#6310": v("Bool", True),
        "tooltip_text#6867": v("String", tooltip),
        "data_model#6220": binding, "title#6241": v("String", title),
        "knob_size#6223": v("Byte", 3), "show_value_popup#10569": v("Bool", True),
        "attribute_id#11012": v("Int16", 712), "knob_style#7055": v("Byte", 3),
        "label_color#7056": v("Int16", 6), "pie_color#7057": v("Byte", 6),
    })


def main_panel(bindings):
    items = []
    for index, (binding, (title, _ident, _port, _default, tooltip)) in enumerate(zip(bindings, PARAMETERS)):
        column, row = index % 4, index // 4
        items.append(knob(binding, title, tooltip, 2 + column * KNOB_W, 4 + row * (KNOB_H + 2)))
    grid = obj(1681, "grid_panel_item", {
        "layout_settings#6226": v("NullObject"), "items#6221": v("ObjectList", owned(*items)),
        "border_style#6228": v("Byte", 0), "title#6242": v("String", ""),
        "show_title#6243": v("Bool", False), "title_color#6522": v("Byte", 6),
        "brightness#6245": v("Byte", 0),
    })
    return obj(1680, "panel", {
        "name#6211": v("String", "Main"), "root_item#6212": v("Object", grid),
        "width#6232": v("Int16", PANEL_WIDTH), "height#6233": v("Byte", PANEL_HEIGHT),
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


def document(project, binary):
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
    params = [decimal_parameter(name, ident, minimum=0.0, maximum=1.0, default=default)
              for name, ident, _port, default, _tip in PARAMETERS]
    dsp = obj(1721, "nitro_atom", {
        "settings#6194": settings([wire(note_proxy), *(wire(p) for p in params)]),
        "channel_count#607": v("Byte", 0), "oversampling#608": v("Byte", 0),
        "fft_order#6567": v("Byte", 0),
        # Descriptors follow the port order in atek303.nitro.
        "nitro_inputs#15756": v("ObjectList", owned(
            note_event_port("note_in", 0),
            *(nitro_port(port, index, 1, output=False)
              for index, (_n, _i, port, _d, _t) in enumerate(PARAMETERS, 1)),
        )),
        "nitro_outputs#15757": v("ObjectList", owned(nitro_port("out", 0, 2, output=True))),
        "code_storage#10421": v("ByteArray", [0, *binary]),
        "is_code_storage_binary_ast#14616": v("Bool", True),
        "use_code_path#11360": v("Bool", False), "code_path#11357": v("String", ""),
    })
    output_proxy = proxy(output=True)
    output_proxy["fields"]["settings#6194"] = settings([wire(dsp, 0)])
    panel = main_panel([ref(p) for p in params])
    identity = project["identity"]
    tags = project["presentation"]["tags"]
    body = obj(151, "device_contents", {
        "proxy_in_ports#177": v("ObjectList", owned(audio_proxy, note_proxy)),
        "child_components#173": v("ObjectList", owned(audio_source, *params, dsp)),
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
