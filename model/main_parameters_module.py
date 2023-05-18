from typing import List

from enums.enums import ParameterType
from model.dsp_parameter import DspParameter


class MainParametersModule:
    def __init__(self, main_parameter_list: List[DspParameter]):
        self.main_parameter_list = main_parameter_list

    @staticmethod
    def get_all_main_parameters() -> tuple:
        return _main_tone_parameters


_main_tone_parameters: tuple = (
    DspParameter(1, "Attack Time",
                 "Adjusts the time after a key is pressed from when the note starts to sound until it reaches maximum volume. A larger value specifies a slower attack.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(2, "Release Time",
                 "Adjusts how long notes linger after keyboard keys are released. A larger values specifies a longer release.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(3, "Cutoff Frequency",
                 "Adjusts timbre by attenuating the components of a note’s frequency characteristics that are higher than a certain frequency (cutoff frequency). A larger value specifies a brighter, harder sound, while a lower value specifies a mellower, softer sound.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(4, "Resonance",
                 "Adjusts the gain of harmonic tones in the vicinity of the cutoff frequency specified above. A larger value creates a more unusual sound.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(5, "Vibrato Type",
                 "Selects the vibrato waveform.",
                 ParameterType.COMBO, ["Sine", "Triangle", "Sawtooth", "Square"], 0),
    DspParameter(6, "Vibrato Depth",
                 "VSpecifies the depth of vibrato.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(7, "Vibrato Rate",
                 "Adjusts the speed of vibrato.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(8, "Vibrato Delay",
                 "Adjusts the time until vibrato starts after a note is sounded.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(9, "Octave Shift",
                 "Shifts the pitch upwards or downwards in octave steps.",
                 ParameterType.KNOB, [-3, 3], 0),
    DspParameter(10, "Volume",
                 "Specifies the volume level of a tone. A larger value sets a higher volume level.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(11, "Velocity Sense",
                 "VSpecifies how much the tone and/or volume should be affected by keyboard touch (pressure). A larger positive value specifies more brightness and greater volume as keyboard touch becomes stronger. A larger negative value specifies more softness and less volume as keyboard touch becomes stronger. A value of 0 specifies no change in accordance with keyboard touch.",
                 ParameterType.KNOB, [-64, 63], 0),
    DspParameter(12, "Reverb Send",
                 "Specifies how much reverb is applied to a tone.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(13, "Chorus Send",
                 "Specifies how much chorus is applied to a tone.",
                 ParameterType.KNOB, [0, 127], 0),
    DspParameter(14, "Delay Send",
                 "Specifies how much delay is applied to a tone.",
                 ParameterType.KNOB, [0, 127], 0))

# MORE:
# reverb params, chorus params, delay params, pitch bend wheel, modulation wheel, sustain pedal
