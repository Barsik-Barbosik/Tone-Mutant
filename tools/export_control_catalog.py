"""Export existing descriptors without importing Qt or opening MIDI devices."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from constants import constants
from models.tone import Tone
from ui.i18n import tr, parameter_help, module_help


def describe(parameter):
    return {key: getattr(parameter, key) for key in
            ("id", "name", "description", "choices")} | {
                "type": parameter.type.name,
                "display_name_es": tr(parameter.name),
                "description_es": parameter_help(parameter),
                "parameter_number": getattr(parameter, "param_number", None),
                "block": getattr(parameter, "block0", None),
            }


def export():
    tone = Tone()
    data = {
        "source": "https://github.com/Barsik-Barbosik/Tone-Mutant",
        "upstream_commit": "98d03ecc38c61059d3cf345c62a8f8abb1ed989c",
        "model": tone.synthesizer_model,
        "hardware_validation": "CT-X800 read-only captures are in captures/. Writes, audible effects and full ranges remain unverified; descriptors are not a capability guarantee.",
        "main_parameters": [describe(parameter) for parameter in tone.main_parameter_list],
        "advanced_parameters": [describe(parameter) for parameter in tone.advanced_parameter_list],
        "dsp_modules": [{"id": module.id, "name": module.name,
                         "display_name_es": tr(module.name), "description_es": module_help(module),
                         "description": module.description,
                         "parameters": [describe(parameter) for parameter in module.dsp_parameter_list],
                         "bypass": describe(module.bypass)} for module in constants.ALL_DSP_MODULES],
        "ctx700_800_tones": [{"id": tone.id, "name": tone.name}
                             for tone in constants.ALL_INSTRUMENTS_700_800],
    }
    target = Path(__file__).resolve().parents[1] / "docs" / "control-catalog.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target)


if __name__ == "__main__":
    export()
