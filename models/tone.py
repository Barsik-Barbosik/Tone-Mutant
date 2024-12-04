from typing import List

from constants import constants
from constants.enums import ParameterType
from models.dsp_module import DspModule
from models.instrument import Instrument
from models.parameter import MainParameter, AdvancedParameter
from utils.utils import get_all_instruments


class Tone:
    def __init__(self):
        self.name: str = None
        self.synthesizer_model: str = None
        self.parent_tone: Instrument = None

        # Main parameters: parameters, that can be edited using synthesizer "tone edit" menu
        self.main_parameter_list: List[MainParameter] = [
            MainParameter(1, 20, 1, "Attack Time",
                          "Adjusts the time after a key is pressed from when the note starts to sound until it reaches maximum volume. A larger value specifies a slower attack.",
                          ParameterType.SPECIAL_ATK_REL_KNOB, [0, 127]),
            MainParameter(2, 20, 5, "Release Time",
                          "Adjusts how long notes linger after keyboard keys are released. A larger values specifies a longer release.",
                          ParameterType.SPECIAL_ATK_REL_KNOB, [0, 127]),
            MainParameter(3, 14, 0, "Cutoff Frequency",
                          "Adjusts timbre by attenuating the components of a note’s frequency characteristics that are higher than a certain frequency (cutoff frequency). A larger value specifies a brighter, harder sound, while a lower value specifies a mellower, softer sound.",
                          ParameterType.KNOB_X2, [0, 127]),
            MainParameter(4, 15, 0, "Resonance",
                          "Adjusts the gain of harmonic tones in the vicinity of the cutoff frequency specified above. A larger value creates a more unusual sound.",
                          ParameterType.KNOB_X2, [0, 127]),
            MainParameter(5, 59, 0, "Vibrato Type",
                          "Selects the vibrato waveform.",
                          ParameterType.COMBO, ["Sine", "Triangle", "Sawtooth", "Square"]),
            MainParameter(6, 63, 0, "Vibrato Depth",
                          "VSpecifies the depth of vibrato.",
                          ParameterType.KNOB, [0, 127]),
            MainParameter(7, 60, 0, "Vibrato Rate",
                          "Adjusts the speed of vibrato.",
                          ParameterType.KNOB, [0, 127]),
            MainParameter(8, 61, 0, "Vibrato Delay",
                          "Adjusts the time until vibrato starts after a note is sounded.",
                          ParameterType.KNOB, [0, 127]),
            MainParameter(9, 43, 0, "Octave Shift",
                          "Shifts the pitch upwards or downwards in octave steps.",
                          ParameterType.KNOB, [-3, 3]),
            MainParameter(10, 45, 0, "Volume",
                          "Specifies the volume level of a tone. A larger value sets a higher volume level.",
                          ParameterType.KNOB, [0, 127]),
            MainParameter(11, 5, 0, "Velocity Sense",
                          "VSpecifies how much the tone and/or volume should be affected by keyboard touch (pressure). A larger positive value specifies more brightness and greater volume as keyboard touch becomes stronger. A larger negative value specifies more softness and less volume as keyboard touch becomes stronger. A value of 0 specifies no change in accordance with keyboard touch.",
                          ParameterType.KNOB, [-64, 63]),
            MainParameter(12, 57, 0, "Reverb Send",
                          "Specifies how much reverb is applied to a tone.",
                          ParameterType.KNOB, [0, 127]),
            MainParameter(13, 56, 0, "Chorus Send",
                          "Specifies how much chorus is applied to a tone.",
                          ParameterType.KNOB, [0, 127]),
            MainParameter(14, 58, 0, "Delay Send",
                          "Specifies how much delay is applied to a tone.",
                          ParameterType.KNOB, [0, 127])]

        # Advanced parameters: parameters, that cannot be edited using synthesizer "tone edit" menu
        self.upper_volume = AdvancedParameter(200, 200, 0, "UPPER 1 Volume",
                                              "Volume of the note. Only notes played on the keyboard are affected by this (not MIDI IN or rhythms).",
                                              ParameterType.KNOB, [0, 127])

        self.advanced_parameter_list: List[AdvancedParameter] = [
            AdvancedParameter(1, 41, 0, "Sound B for Note-off",
                              "Sound B is triggered when a key is released, producing a sound specifically for the note-off action. This adds detail or effects to the end of a note, such as a fade, click, or other textures.",
                              ParameterType.COMBO, ["Disabled", "Enabled"]),
            AdvancedParameter(2, 42, 0, "Note-off velocity",
                              "This refers to how the speed at which you press and release a key affects the velocity of Sound B.",
                              ParameterType.COMBO, ["Note-off Velocity", "Note-on Velocity", "Minimum of Both", "Unknown"]),
            AdvancedParameter(3, 115, 0, "Sound B for Double-stop",
                              "Sound B is triggered when two notes are played together, simulating the effect of a double-stop, as used in string instruments.",
                              ParameterType.COMBO, ["Disabled", "Enabled"]),
            AdvancedParameter(4, 114, 0, "Monophonic Mode",
                              "In monophonic mode, the synthesizer produces only one note at a time, regardless of how many keys are pressed. If multiple keys are pressed simultaneously or in succession, the most recent key pressed takes priority and becomes the only note that sounds.",
                              ParameterType.COMBO, ["Disabled", "Enabled"]),
            AdvancedParameter(5, 116, 0, "Portamento",
                              "Portamento lets the sound slide smoothly from one note to the next instead of jumping.",
                              ParameterType.COMBO, ["Disabled", "Mode 1", "Mode 2"]),
            AdvancedParameter(6, 107, 0, "Portamento Time",
                              "Portamento time controls how long it takes to slide from one note to another. A shorter time makes the slide quick, while a longer time creates a slow, smooth glide.",
                              ParameterType.KNOB, [0, 127]), ]

        self.dsp_module_1: DspModule = None
        self.dsp_module_2: DspModule = None
        self.dsp_module_3: DspModule = None
        self.dsp_module_4: DspModule = None

    def to_json(self):
        obj = {
            "name": self.name,
            "synthesizer_model": self.synthesizer_model,
            "parent_tone": self.parent_tone,
            "parameters": self.main_parameter_list,
            "dsp_modules": {
                "dsp_1": self.dsp_module_1,
                "dsp_2": self.dsp_module_2,
                "dsp_3": self.dsp_module_3,
                "dsp_4": self.dsp_module_4
            }
        }
        return obj

    @staticmethod
    def get_instrument_by_id(instrument_id: int):
        if instrument_id is None or instrument_id == 0:
            return None

        for instrument in get_all_instruments():
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
