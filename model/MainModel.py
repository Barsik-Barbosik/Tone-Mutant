from enum import Enum

from enums.enums import ParameterType, TabName
from model.DspEffect import DspEffect
from model.DspParameter import DspParameter

mainParamsTuple: tuple = (DspParameter(100, "Atk. time", "Atk. time - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(101, "Rel. time", "Rel. time - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Cutoff F", "Cutoff F - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Resonance", "Resonance - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Vibrato", "Vibrato - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Oct. shif", "Oct. shif - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Volume", "Volume - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Velocity sensitivity", "Velocity sensitivity - description.",
                                       ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Rev. send", "Rev. send - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Cho. send", "Cho. send - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Dly. send", "Dly. send - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Pitch band", "Pitch band - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Modulation", "Modulation - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Sustain pedal", "Sustain pedal - description.", ParameterType.COMBO,
                                       ["OFF", "ON"], 0))

dspEffectsTuple: tuple = (  # DspEffect(0, "!!ERROR!!"),
    DspEffect(27, "Mono 1-Band EQ", "This is a single-band monaural equalizer.",
              [DspParameter(1, "EQ Frequency", "Adjusts the center frequency of Equalizer.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ Gain", "Adjusts the gain of Equalizer.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(28, "Mono 2-Band EQ", "This is a dual-band monaural equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(6, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(7, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(29, "Mono 3-Band EQ", "This is a three-band monaural equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "EQ3 Frequency", "Adjusts the center frequency of Equalizer 3.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(6, "EQ3 Gain", "Adjusts the gain of Equalizer 3.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(8, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(9, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(21, "Stereo 1-Band EQ", "This is a single-band stereo equalizer",
              [DspParameter(1, "EQ Frequency", "Adjusts the center frequency of Equalizer.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ Gain", "Adjusts the gain of Equalizer.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(22, "Stereo 2-Band EQ", "This is a dual-band stereo equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(6, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(7, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(1, "Stereo 3-Band EQ", "This is a three-band stereo equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "EQ3 Frequency", "Adjusts the center frequency of Equalizer 3.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(6, "EQ3 Gain", "Adjusts the gain of Equalizer 3.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(8, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(9, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(31, "Tone Control",
              "Provides monaural tone control for adjusting low-range, mid-range, and high-range frequencies.",
              [DspParameter(1, "Low Frequency", "Adjusts the cutoff frequency of Low-range.", ParameterType.COMBO,
                            ["50Hz", "63Hz", "80Hz", "100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz",
                             "500Hz", "630Hz", "800Hz"], 0),
               DspParameter(2, "Low Gain", "Adjusts the Low-range gain.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Mid Frequency", "Adjusts the center frequency of Mid-range.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "Mid Gain", "Adjusts the Mid-range gain.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "High Frequency", "Adjusts the cutoff frequency of High-range.", ParameterType.COMBO,
                            ["2.0kHz", "2.5kHz", "3.2kHz", "4.0kHz", "5.0kHz", "6.0kHz", "8.0kHz", "10kHz", "13kHz",
                             "16kHz"], 9),
               DspParameter(6, "High Gain", "Adjusts the High-range gain.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(8, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(9, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(9, "Tremolo", "Shifts the volume of the input signal using an LFO.", []),
    DspEffect(10, "Auto Pan", "Shifts the continual left-right panning of the input signal using an LFO.", []),
    DspEffect(2, "Compressor", "Compresses the input signal, which can have the effect of suppressing level variation.",
              []),
    DspEffect(3, "Limiter", "Limits the input signal level so it does not rise above a preset level.", []),
    DspEffect(4, "Enhancer", "Enhances the profiles of the low range and high range of the input signal.", []),
    DspEffect(6, "Phaser",
              "Produces a distinctive pulsating, broad sound by using an LFO to change the phase of the input signal and then mixes it with the original input signal.",
              []),
    DspEffect(7, "Chorus", "Gives notes depth and breadth.", []),
    DspEffect(8, "Flanger", "Applies wildly pulsating and metallic reverberation to notes. Selects the LFO waveform.",
              []),
    DspEffect(11, "Rotary", "This effect is a rotary speaker simulator.", []),
    DspEffect(12, "Drive Rotary", "This is a rotary speaker simulator that makes overdrive possible.", []),
    DspEffect(16, "Pitch Shifter", "This effect transforms the pitch of the input signal.", []),
    DspEffect(18, "Ring Modulator",
              "Multiplies the input signal with an internal oscillator signal to create a metallic sound.", []),
    DspEffect(5, "Reflection",
              "Simulates the initial reflection of reverberation. Applies acoustic ambiance and presence to notes.",
              []),
    DspEffect(19, "Delay", "Delays the input signal and feeds it back to create a repeating effect.", []),
    DspEffect(20, "Piano Effect", "This effect is suited to acoustic piano play.", []),
    DspEffect(13, "LFO Wah", "This is a “wah” effect that can automatically affect the frequency using an LFO.", []),
    DspEffect(14, "Auto Wah",
              "This is a “wah” effect that can automatically shift the frequency in accordance with the level of the input signal.",
              []),
    DspEffect(30, "Modeling Wah",
              "Simulates various types of wah pedals. This effect can automatically shift the frequency in accordance with the level of the input signal.",
              []),
    DspEffect(15, "Distortion", "Distortion, wah, and amp simulator combined into a single effect.", []),
    DspEffect(23, "Drive", "Simulates the drive of a musical instrument amplifier.", []),
    DspEffect(24, "Amp Cabinet", "Simulates the amp and speaker cabinet without drive and distortion.", []),
    DspEffect(17, "* Multi Chorus", "Unknown secret DSP effect", []),
    DspEffect(25, "* Holw Body", "Unknown secret DSP effect", []),
    DspEffect(26, "* Pino Body", "Unknown secret DSP effect", []))


class MainModel:
    def __init__(self):
        self.currentTabName: Enum = TabName.MAIN_PARAMETERS
        self.selectedDsp1: DspEffect = None
        self.selectedDsp2: DspEffect = None
        self.selectedDsp3: DspEffect = None
        self.selectedDsp4: DspEffect = None

    def get_current_dsp(self) -> DspEffect:
        if self.currentTabName == TabName.DSP_1:
            return self.selectedDsp1
        elif self.currentTabName == TabName.DSP_2:
            return self.selectedDsp2
        elif self.currentTabName == TabName.DSP_3:
            return self.selectedDsp3
        elif self.currentTabName == TabName.DSP_4:
            return self.selectedDsp4
        else:
            return None

    def get_current_dsp_name(self) -> str:
        return self.get_current_dsp().name if self.get_current_dsp() is not None else "OFF"

    def set_current_dsp(self, id: int):
        new_dsp_effect: DspEffect = self.get_dsp_effect_by_id(id)
        if self.currentTabName == TabName.DSP_1:
            self.selectedDsp1 = new_dsp_effect
        elif self.currentTabName == TabName.DSP_2:
            self.selectedDsp2 = new_dsp_effect
        elif self.currentTabName == TabName.DSP_3:
            self.selectedDsp3 = new_dsp_effect
        elif self.currentTabName == TabName.DSP_4:
            self.selectedDsp4 = new_dsp_effect

    def get_output_text(self) -> str:
        output: str = "currentTabName: " + str(self.currentTabName.value) \
                      + "\nselectedDsp1: " + str(self.selectedDsp1.name if self.selectedDsp1 is not None else "OFF") \
                      + "\nselectedDsp2: " + str(self.selectedDsp2.name if self.selectedDsp2 is not None else "OFF") \
                      + "\nselectedDsp3: " + str(self.selectedDsp3.name if self.selectedDsp3 is not None else "OFF") \
                      + "\nselectedDsp4: " + str(self.selectedDsp4.name if self.selectedDsp4 is not None else "OFF")
        return output

    @staticmethod
    def get_dsp_effect_by_id(id: int) -> DspEffect:
        for dspEffect in dspEffectsTuple:
            if dspEffect.id == id:
                return dspEffect
        return None

    @staticmethod
    def get_dsp_effects_tuple() -> tuple:
        return dspEffectsTuple

    @staticmethod
    def get_main_params_tuple() -> tuple:
        return mainParamsTuple
