#!/usr/bin/env python3
"""Compile atek303.nitro with Bitwig's own compiler and write ATEK303.bwdevice.

Uses the tools of polarity's bitwig-devices-blueprint (set up as in Bitwig-Mods/CLAUDE.md).
    python build.py            # build and copy into Bitwig-Mods/build/devices (the Patchbay test folder)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BLUEPRINT = REPO / "terceros/bitwig-devices-blueprint"
sys.path[:0] = [str(BLUEPRINT), str(BLUEPRINT / "scripts"), str(HERE)]

import compiler_profiles  # noqa: E402
import project_contracts  # noqa: E402
from devices.common.document_graph import run  # noqa: E402
from document import document  # noqa: E402

INPUTS = BLUEPRINT / "local/host-tools/linux-x86_64-bitwig-6.1.7/compiler-inputs.json"
TEST_FOLDER = REPO / "build/devices"


def main() -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--no-install", action="store_true", help="do not copy into the Patchbay test folder")
    cli.add_argument("--lab", action="store_true",
                     help="build 'ATEK Panel Lab': same engine, a panel showing every widget style side by side")
    args = cli.parse_args()
    project = project_contracts.load(HERE / "bitwig-project.json")
    inputs, profile = compiler_profiles.validate_inputs(INPUTS)
    compiler_profiles.require_target(profile, project["target"])
    codec, _ = compiler_profiles.document_parser(inputs, profile)
    output = (HERE / project["output"]["path"]).resolve()
    if args.lab:
        import uuid
        project["name"] = "ATEK Panel Lab"
        project["identity"]["uuid"] = str(uuid.uuid5(uuid.UUID(project["identity"]["uuid"]), "panel-lab"))
        output = output.with_name("ATEK Panel Lab.bwdevice")
    output.parent.mkdir(parents=True, exist_ok=True)

    nitro, = project["sources"]["nitro"]
    with TemporaryDirectory(prefix="atek303-", dir=output.parent) as temporary:
        staging = Path(temporary)
        compiled = staging / "atek303.nitrobin"
        compiler_profiles.compile_source(HERE / nitro, compiled, INPUTS)
        source = staging / "device.json"
        source.write_text(json.dumps(document(project, compiled.read_bytes(), lab=args.lab), ensure_ascii=False), encoding="utf-8")
        candidate = staging / output.name
        run([str(codec), "from-json", str(source), str(candidate)])
        run([str(codec), "roundtrip", str(candidate)])
        candidate.replace(output)

    print(f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output}")
    if not args.no_install:
        TEST_FOLDER.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output, TEST_FOLDER / output.name)
        print(f"Installed in {TEST_FOLDER}; restart Bitwig from Patchbay to load it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
