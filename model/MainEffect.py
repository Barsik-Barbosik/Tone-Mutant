from enums.enums import ParameterType
from model.DspParameter import DspParameter


class MainEffect:

    @staticmethod
    def get_main_effects_tuple() -> tuple:
        return main_effects_tuple


main_effects_tuple: tuple = (
    DspParameter(100, "Atk. time", "Atk. time - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(101, "Rel. time", "Rel. time - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Cutoff F", "Cutoff F - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Resonance", "Resonance - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Vibrato", "Vibrato - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Oct. shift", "Oct. shift - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Volume", "Volume - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Velocity sensitivity", "Velocity sensitivity - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Rev. send", "Rev. send - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Cho. send", "Cho. send - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Dly. send", "Dly. send - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Pitch band", "Pitch band - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Modulation", "Modulation - description.", ParameterType.KNOB, [0, 127], 0),
    DspParameter(102, "Sustain pedal", "Sustain pedal - description.", ParameterType.COMBO, ["OFF", "ON"], 0))
