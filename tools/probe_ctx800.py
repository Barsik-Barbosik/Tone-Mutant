"""Capture a bounded set of read requests. This tool never sends parameter writes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from constants import constants
from models.tone import Tone


def pair(value):
    if not 0 <= value <= 16383:
        raise ValueError("Expected a 14-bit nonnegative value")
    return [value & 127, value >> 7]


def request_packet(parameter, block=0, length=1):
    if not 1 <= length <= 24:
        raise ValueError("Read length must be 1-24")
    return [0xF0, 0x44, 0x19, 0x01, 0x7F, 0, 3, 3, 0, 0,
            0, 0, 0, 0, 0, 0] + pair(block) + pair(parameter) + [0, 0] + pair(length - 1) + [0xF7]


def parse_reply(message):
    if (len(message) < 26 or message[:4] != [0xF0, 0x44, 0x19, 0x01]
            or message[4:6] != [0x7F, 1] or message[-1] != 0xF7
            or any(not 0 <= byte < 128 for byte in message[1:-1])):
        return None
    return {"category": message[6], "memory": message[7],
            "parameter_set": message[8] + 128 * message[9],
            "block": message[16] + 128 * message[17],
            "parameter": message[18] + 128 * message[19],
            "index": message[20] + 128 * message[21],
            "length_field": message[22] + 128 * message[23],
            "data": message[24:-1]}


def plan():
    tone = Tone()
    reads = [("Tone name", 0, 0, 16)]
    reads += [(p.name, p.param_number, p.block0, 1)
              for p in tone.main_parameter_list + tone.advanced_parameter_list]
    # Line Select appears in the official CT-X800 parameter table, but not the UI.
    if not any(parameter == 44 and block == 0 for _, parameter, block, _ in reads):
        reads += [("Line Select", 44, 0, 1)]
    for block in range(4):
        reads += [("DSP {} module".format(block + 1), 85, block, 1),
                  ("DSP {} bypass".format(block + 1), 86, block, 1),
                  ("DSP {} data".format(block + 1), 87, block, 14)]
    return reads


def survey_plan():
    """Only the finite address list already used by the upstream TON reader; block 0."""
    return [("Tone parameter {}".format(parameter), parameter, 0,
             16 if parameter in (0, 84) else 14 if parameter == 87 else 1)
            for parameter in list(range(123)) + [200, 201, 202]]


def probe(output, timeout=0.5, survey=False):
    import rtmidi
    midi_in, midi_out = rtmidi.MidiIn(), rtmidi.MidiOut()
    report = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "read-only IPR; category=3 memory=3 parameter_set=0",
              "plan": "upstream TON reader addresses, block 0" if survey else "interface parameters",
              "inputs": midi_in.get_ports(), "outputs": midi_out.get_ports(),
              "requests": [], "received": []}
    try:
        inputs = [(i, name) for i, name in enumerate(report["inputs"]) if "CASIO USB-MIDI" in name.upper()]
        outputs = [(i, name) for i, name in enumerate(report["outputs"]) if "CASIO USB-MIDI" in name.upper()]
        if len(inputs) != 1 or len(outputs) != 1:
            raise RuntimeError("Expected exactly one CASIO USB-MIDI input and output")
        midi_in.open_port(inputs[0][0])
        midi_in.ignore_types(sysex=False, timing=True, active_sense=True)
        midi_out.open_port(outputs[0][0])
        report["selected_input"], report["selected_output"] = inputs[0][1], outputs[0][1]
        consecutive_timeouts = 0
        for name, parameter, block, length in survey_plan() if survey else plan():
            packet = request_packet(parameter, block, length)
            entry = {"name": name, "parameter": parameter, "block": block,
                     "request_hex": bytes(packet).hex(" ").upper(), "reply": None}
            report["requests"].append(entry)
            midi_out.send_message(packet)
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                event = midi_in.get_message()
                if event is None:
                    time.sleep(0.005)
                    continue
                message, delta = event
                reply = parse_reply(message)
                report["received"].append({"hex": bytes(message).hex(" ").upper(), "reply": reply})
                if reply and (reply["category"], reply["memory"], reply["parameter_set"],
                              reply["block"], reply["parameter"], reply["index"]) == (3, 3, 0, block, parameter, 0):
                    entry["reply"] = reply
                    break
            consecutive_timeouts = 0 if entry["reply"] else consecutive_timeouts + 1
            print("{}: {}".format(name, entry["reply"]["data"] if entry["reply"] else "no reply"), flush=True)
            if consecutive_timeouts >= 3:
                report["stopped_reason"] = "Three consecutive unanswered requests"
                break
            time.sleep(0.05)
    finally:
        midi_in.close_port()
        midi_out.close_port()
        midi_in.delete()
        midi_out.delete()
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Capture: {}".format(output), flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="captures/ctx800-readonly.json")
    parser.add_argument("--timeout", type=float, default=0.5)
    parser.add_argument("--survey", action="store_true", help="Query the 126 addresses in the upstream TON reader, block 0 only")
    args = parser.parse_args()
    if not 0.1 <= args.timeout <= 3:
        parser.error("Timeout must be between 0.1 and 3 seconds")
    probe(args.output, args.timeout, args.survey)
