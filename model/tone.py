from constants import constants
from constants.enums import ParameterType
from model.dsp_module import DspModule
from model.instrument import Instrument
from model.parameter import MainParameter


class Tone:
    def __init__(self):
        self.name: str = None
        self.base_tone: Instrument = None

        self.main_parameter_list: list[MainParameter] = [
            MainParameter(1, 20, 1, "Attack Time",
                          "Adjusts the time after a key is pressed from when the note starts to sound until it reaches maximum volume. A larger value specifies a slower attack.",
                          ParameterType.KNOB, [0, 1023], 0),
            MainParameter(2, 20, 5, "Release Time",
                          "Adjusts how long notes linger after keyboard keys are released. A larger values specifies a longer release.",
                          ParameterType.KNOB, [0, 1023], 0),
            MainParameter(3, 14, 0, "Cutoff Frequency",
                          "Adjusts timbre by attenuating the components of a note’s frequency characteristics that are higher than a certain frequency (cutoff frequency). A larger value specifies a brighter, harder sound, while a lower value specifies a mellower, softer sound.",
                          ParameterType.KNOB_255, [0, 127], 0),
            MainParameter(4, 15, 0, "Resonance",
                          "Adjusts the gain of harmonic tones in the vicinity of the cutoff frequency specified above. A larger value creates a more unusual sound.",
                          ParameterType.KNOB_255, [0, 127], 0),
            MainParameter(5, 59, 0, "Vibrato Type",
                          "Selects the vibrato waveform.",
                          ParameterType.COMBO, ["Sine", "Triangle", "Sawtooth", "Square"], 0),
            MainParameter(6, 63, 0, "Vibrato Depth",
                          "VSpecifies the depth of vibrato.",
                          ParameterType.KNOB, [0, 127], 0),
            MainParameter(7, 60, 0, "Vibrato Rate",
                          "Adjusts the speed of vibrato.",
                          ParameterType.KNOB, [0, 127], 0),
            MainParameter(8, 61, 0, "Vibrato Delay",
                          "Adjusts the time until vibrato starts after a note is sounded.",
                          ParameterType.KNOB, [0, 127], 0),
            MainParameter(9, 43, 0, "Octave Shift",
                          "Shifts the pitch upwards or downwards in octave steps.",
                          ParameterType.KNOB, [1, 7], 4),
            MainParameter(10, None, 0, "Volume",
                          "Specifies the volume level of a tone. A larger value sets a higher volume level.",
                          ParameterType.KNOB, [0, 127], 0),
            MainParameter(11, None, 0, "Velocity Sense",
                          "VSpecifies how much the tone and/or volume should be affected by keyboard touch (pressure). A larger positive value specifies more brightness and greater volume as keyboard touch becomes stronger. A larger negative value specifies more softness and less volume as keyboard touch becomes stronger. A value of 0 specifies no change in accordance with keyboard touch.",
                          ParameterType.KNOB, [-64, 63], 0),
            MainParameter(12, None, 0, "Reverb Send",
                          "Specifies how much reverb is applied to a tone.",
                          ParameterType.KNOB, [0, 127], 0),
            MainParameter(13, None, 0, "Chorus Send",
                          "Specifies how much chorus is applied to a tone.",
                          ParameterType.KNOB, [0, 127], 0),
            MainParameter(14, None, 0, "Delay Send",
                          "Specifies how much delay is applied to a tone.",
                          ParameterType.KNOB, [0, 127], 0)]

        # Advanced parameters:
        # reverb params, chorus params, delay params, pitch bend wheel, modulation wheel, sustain pedal

        self.dsp_module_1: DspModule = None
        self.dsp_module_2: DspModule = None
        self.dsp_module_3: DspModule = None
        self.dsp_module_4: DspModule = None

    def to_json(self):
        obj = {
            "name": self.name,
            "base_tone": self.base_tone,
            "parameters": self.main_parameter_list,
            "dsp_modules": [
                {"dsp_1": self.dsp_module_1,
                 "dsp_2": self.dsp_module_2,
                 "dsp_3": self.dsp_module_3,
                 "dsp_4": self.dsp_module_4
                 }
            ]}
        return obj

    @staticmethod
    def get_instrument_by_id(instrument_id: int):
        if instrument_id is None or instrument_id == 0:
            return None

        for instrument in constants.ALL_INSTRUMENTS:
            if instrument.id == instrument_id:
                return instrument

        return None

    @staticmethod
    def get_dsp_module_by_id(dsp_module_id: int):
        if dsp_module_id is None or dsp_module_id == 0 or dsp_module_id == 0x7F:
            return None

        for dsp_module in constants.ALL_DSP_MODULES:
            if dsp_module.id == dsp_module_id:
                return dsp_module

        return None
