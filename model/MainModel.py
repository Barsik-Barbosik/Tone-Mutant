from enums.enums import ParameterType
from model.DspEffect import DspEffect
from model.DspParameter import DspParameter

dspEffectList = [  # DspEffect(0, "!!ERROR!!"),
    DspEffect(27, "Mono 1-Band EQ", "This is a single-band monaural equalizer.",
              [DspParameter(1, "EQ Frequency", "Adjusts the center frequency of Equalizer.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ Gain", "Adjusts the gain of Equalizer.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(28, "Mono 2-Band EQ", "This is a dual-band monaural equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(6, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(7, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(29, "Mono 3-Band EQ", "This is a three-band monaural equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "EQ3 Frequency", "Adjusts the center frequency of Equalizer 3.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(6, "EQ3 Gain", "Adjusts the gain of Equalizer 3.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(8, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(9, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(21, "Stereo 1-Band EQ", "This is a single-band stereo equalizer",
              [DspParameter(1, "EQ Frequency", "Adjusts the center frequency of Equalizer.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ Gain", "Adjusts the gain of Equalizer.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(22, "Stereo 2-Band EQ", "This is a dual-band stereo equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(6, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(7, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(1, "Stereo 3-Band EQ", "This is a three-band stereo equalizer.",
              [DspParameter(1, "EQ1 Frequency", "Adjusts the center frequency of Equalizer 1.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ1 Gain", "Adjusts the gain of Equalizer 1.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "EQ2 Frequency", "Adjusts the center frequency of Equalizer 2.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "EQ2 Gain", "Adjusts the gain of Equalizer 2.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "EQ3 Frequency", "Adjusts the center frequency of Equalizer 3.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(6, "EQ3 Gain", "Adjusts the gain of Equalizer 3.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(8, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(9, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(31, "Tone Control", "Provides monaural tone control for adjusting low-range, mid-range, and high-range frequencies.",
              [DspParameter(1, "Low Frequency", "Adjusts the cutoff frequency of Low-range.", ParameterType.COMBO,
                            ["50Hz", "63Hz", "80Hz", "100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz"], 0),
               DspParameter(2, "Low Gain", "Adjusts the Low-range gain.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Mid Frequency", "Adjusts the center frequency of Mid-range.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz", "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(4, "Mid Gain", "Adjusts the Mid-range gain.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(5, "High Frequency", "Adjusts the cutoff frequency of High-range.", ParameterType.COMBO,
                            ["2.0kHz", "2.5kHz", "3.2kHz", "4.0kHz", "5.0kHz", "6.0kHz", "8.0kHz", "10kHz", "13kHz", "16kHz"], 9),
               DspParameter(6, "High Gain", "Adjusts the High-range gain.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(8, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(9, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(9, "Tremolo", "Shifts the volume of the input signal using an LFO.", []),
    DspEffect(10, "Auto Pan", "Shifts the continual left-right panning of the input signal using an LFO.", []),
    DspEffect(2, "Compressor", "Compresses the input signal, which can have the effect of suppressing level variation.", []),
    DspEffect(3, "Limiter", "Limits the input signal level so it does not rise above a preset level.", []),
    DspEffect(4, "Enhancer", "Enhances the profiles of the low range and high range of the input signal.", []),
    DspEffect(6, "Phaser",
              "Produces a distinctive pulsating, broad sound by using an LFO to change the phase of the input signal and then mixes it with the original input signal.", []),
    DspEffect(7, "Chorus", "Gives notes depth and breadth.", []),
    DspEffect(8, "Flanger", "Applies wildly pulsating and metallic reverberation to notes. Selects the LFO waveform.", []),
    DspEffect(11, "Rotary", "This effect is a rotary speaker simulator.", []),
    DspEffect(12, "Drive Rotary", "This is a rotary speaker simulator that makes overdrive possible.", []),
    DspEffect(16, "Pitch Shifter", "This effect transforms the pitch of the input signal.", []),
    DspEffect(18, "Ring Modulator", "Multiplies the input signal with an internal oscillator signal to create a metallic sound.", []),
    DspEffect(5, "Reflection", "Simulates the initial reflection of reverberation. Applies acoustic ambiance and presence to notes.", []),
    DspEffect(19, "Delay", "Delays the input signal and feeds it back to create a repeating effect.", []),
    DspEffect(20, "Piano Effect", "This effect is suited to acoustic piano play.", []),
    DspEffect(13, "LFO Wah", "This is a “wah” effect that can automatically affect the frequency using an LFO.", []),
    DspEffect(14, "Auto Wah", "This is a “wah” effect that can automatically shift the frequency in accordance with the level of the input signal.", []),
    DspEffect(30, "Modeling Wah", "Simulates various types of wah pedals. This effect can automatically shift the frequency in accordance with the level of the input signal.", []),
    DspEffect(15, "Distortion", "Distortion, wah, and amp simulator combined into a single effect.", []),
    DspEffect(23, "Drive", "Simulates the drive of a musical instrument amplifier.", []),
    DspEffect(24, "Amp Cabinet", "Simulates the amp and speaker cabinet without drive and distortion.", []),
    DspEffect(17, "* Multi Chorus", "Unknown secret DSP effect", []),
    DspEffect(25, "* Holw Body", "Unknown secret DSP effect", []),
    DspEffect(26, "* Pino Body", "Unknown secret DSP effect", [])]


class MainModel:
    def __init__(self):
        self.currentDsp1 = None
        self.currentDsp2 = None
        self.currentDsp3 = None
        self.currentDsp4 = None

    def setCurrentDsp1(self, id: int):
        self.currentDsp1 = self.getDspEffectById(id)

    @staticmethod
    def getDspEffectById(id: int):
        for dspEffect in dspEffectList:
            if dspEffect.id == id:
                return dspEffect
        return None

    @staticmethod
    def getDspList():
        return dspEffectList
