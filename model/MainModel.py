from enum import Enum

from enums.enums import ParameterType, TabName
from model.DspEffect import DspEffect
from model.DspParameter import DspParameter

mainParamsTuple: tuple = (DspParameter(100, "Atk. time", "Atk. time - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(101, "Rel. time", "Rel. time - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Cutoff F", "Cutoff F - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Resonance", "Resonance - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Vibrato", "Vibrato - description.", ParameterType.KNOB, [0, 127], 0),
                          DspParameter(102, "Oct. shift", "Oct. shift - description.", ParameterType.KNOB, [0, 127], 0),
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

dspEffectsTuple: tuple = (
    DspEffect(27, "Mono 1-Band EQ", "This is a single-band monaural equalizer.",
              [DspParameter(1, "EQ Frequency", "Adjusts the center frequency of Equalizer.", ParameterType.COMBO,
                            ["100Hz", "125Hz", "160Hz", "200Hz", "250Hz", "315Hz", "400Hz", "500Hz", "630Hz", "800Hz",
                             "1.0kHz", "1.3kHz", "1.6kHz", "2.0kHz", "2.5kHz", "3.2kHz",
                             "4.0kHz", "5.0kHz", "6.3kHz", "8.0kHz"], 11),
               DspParameter(2, "EQ Gain", "Adjusts the gain of Equalizer.", ParameterType.KNOB, [-12, 12], 0),
               DspParameter(3, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                            100),
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
    DspEffect(9, "Tremolo", "Shifts the volume of the input signal using an LFO.", [
        DspParameter(1, "LFO Rate", "Adjusts the LFO rate.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(2, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "LFO Waveform", "Selects the LFO waveform.", ParameterType.COMBO,
                     ["Sine", "Triangle", "Trapezoid"], 0),
        DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(10, "Auto Pan", "Shifts the continual left-right panning of the input signal using an LFO.", [
        DspParameter(1, "LFO Rate", "Adjusts the LFO rate.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(2, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "LFO Waveform", "Selects the LFO waveform.", ParameterType.COMBO,
                     ["Sine", "Triangle", "Trapezoid"], 0),
        DspParameter(4, "Manual", "Adjusts the pan (stereo position).", ParameterType.KNOB, [-64, 63], 0),
        DspParameter(5, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(6, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(2, "Compressor", "Compresses the input signal, which can have the effect of suppressing level variation.",
              [DspParameter(1, "Attack",
                            "Adjusts the time until compression goes into effect. A smaller value causes prompt compressor operation, which suppresses the attack of the input signal. A larger values delays compressor operation, which causes the attack of the input signal to be output as-is.",
                            ParameterType.KNOB, [0, 127], 0),
               DspParameter(2, "Release",
                            "Adjusts the time until compression is released after the input signal drops below a prescribed level. When an attack feeling is desired (no compression at the onset of the sound), set this parameter to as low a value as possible. To have compression applied at all times, set a high value.",
                            ParameterType.KNOB, [0, 127], 0),
               DspParameter(3, "Ratio", "Adjusts the compression ratio of the audio signal.", ParameterType.COMBO,
                            ["1:1", "2:1", "4:1", "8:1", "16:1", "32:1", "Inf:1"], 0),
               DspParameter(4, "Wet Level",
                            "Adjusts the level of the effect sound. Output volume changes in accordance with the Ratio setting and the characteristics of the input tone.",
                            ParameterType.KNOB, [0, 127],
                            0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(3, "Limiter", "Limits the input signal level so it does not rise above a preset level.", [
        DspParameter(1, "Limit", "Adjusts the volume level of the limit at which limiting is applied.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(2, "Attack",
                     "Adjusts the time until the compression effect starts. A smaller value causes prompt limiter operation, which suppresses the attack of the input signal. A larger values delays limiter operation, which causes the attack of the input signal to be output as-is.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "Release",
                     "Adjusts the time until compression is released after the input signal drops below a prescribed level.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(4, "Wet Level",
                     "Adjusts the level of the effect sound. Output volume changes in accordance with the Limit setting and the characteristics of the input tone. Use this parameter to correct for such changes.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(4, "Enhancer", "Enhances the profiles of the low range and high range of the input signal.", [
        DspParameter(1, "Low Frequency", "Adjusts the low range enhancer frequency.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(2, "Low Gain", "Adjusts the low range enhancer gain.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "High Frequency", "Adjusts the high range enhancer frequency.", ParameterType.KNOB, [0, 127],
                     0),
        DspParameter(4, "High Gain", "Adjusts the high range enhancer gain.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(6, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(7, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(6, "Phaser",
              "Produces a distinctive pulsating, broad sound by using an LFO to change the phase of the input signal and then mixes it with the original input signal.",
              [
                  DspParameter(1, "Resonance", "Adjusts the strength of feedback.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(2, "Manual", "Adjusts the reference phaser shift amount.", ParameterType.KNOB, [-64, 63],
                               0),
                  DspParameter(3, "LFO Rate", "Adjusts the LFO rate.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(4, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(5, "LFO Waveform", "Selects the LFO waveform.", ParameterType.COMBO,
                               ["Sine", "Triangle", "Random"], 0),
                  DspParameter(6, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(7, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                               0),
                  DspParameter(8, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                               0)]),
    DspEffect(7, "Chorus", "Gives notes depth and breadth.", [
        DspParameter(1, "LFO Rate", "Adjusts the LFO rate.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(2, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "LFO Waveform", "Selects the LFO waveform.", ParameterType.COMBO,
                     ["Sine", "Triangle"], 0),
        DspParameter(4, "Feedback", "Adjusts the strength of feedback.", ParameterType.KNOB, [-64, 63], 0),
        DspParameter(5, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                     0),
        DspParameter(6, "Polarity", "Inverts the LFO of one channel.", ParameterType.COMBO,
                     ["Negative", "Positive"], 0),
        DspParameter(7, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(8, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                     0)]),
    DspEffect(8, "Flanger", "Applies wildly pulsating and metallic reverberation to notes. Selects the LFO waveform.",
              [DspParameter(1, "LFO Rate", "Adjusts the LFO rate.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(2, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(3, "LFO Waveform", "Selects the LFO waveform.", ParameterType.COMBO,
                            ["Sine", "Triangle", "Random"], 0),
               DspParameter(4, "Feedback", "Adjusts the strength of feedback.", ParameterType.KNOB, [-64, 63], 0),
               DspParameter(5, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                            0),
               DspParameter(6, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
               DspParameter(7, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(11, "Rotary", "This effect is a rotary speaker simulator.", [
        DspParameter(1, "Type", "Selects the rotary speaker type.", ParameterType.COMBO,
                     ["Type 0", "Type 1", "Type 2", "Type 3"], 0),
        DspParameter(2, "Speed", "Switches the speed mode between fast and slow.", ParameterType.COMBO,
                     ["Slow", "Fast"], 0),
        DspParameter(3, "Brake", "Stops speaker rotation.", ParameterType.COMBO,
                     ["Rotate", "Stop"], 0),
        DspParameter(4, "Fall Accel", "Adjusts acceleration when the speed mode is switched from fast to slow.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "Rise Accel", "Adjusts acceleration when the speed mode is switched from slow to fast.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(6, "Slow Rate", "Adjusts the speaker rotation speed in the slow speed mode.", ParameterType.KNOB,
                     [0, 127],
                     0),
        DspParameter(7, "Fast Rate", "Adjusts the speaker rotation speed in the fast speed mode.", ParameterType.KNOB,
                     [0, 127],
                     0),
        DspParameter(8, "Vibrato/Chorus", "Selects the vibrato and the chorus type.", ParameterType.COMBO,
                     ["Off", "Vibrato 1", "Chorus 1", "Vibrato 2", "Chorus 2", "Vibrato 3", "Chorus 3"], 0),
        DspParameter(9, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(10, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                     0)]),
    DspEffect(12, "Drive Rotary", "This is a rotary speaker simulator that makes overdrive possible.", [
        DspParameter(1, "Type", "Selects the rotary speaker type.", ParameterType.COMBO,
                     ["Type 0", "Type 1", "Type 2", "Type 3"], 0),
        DspParameter(2, "Overdrive Gain", "Adjusts overdrive gain.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "Overdrive Level", "Adjusts the overdrive output level.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(4, "Speed", "Switches the speed mode between fast and slow.", ParameterType.COMBO,
                     ["Slow", "Fast"], 0),
        DspParameter(5, "Brake", "Stops speaker rotation.", ParameterType.COMBO,
                     ["Rotate", "Stop"], 0),
        DspParameter(6, "Fall Accel", "Adjusts acceleration when the speed mode is switched from fast to slow.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(7, "Rise Accel", "Adjusts acceleration when the speed mode is switched from slow to fast.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(8, "Slow Rate", "Adjusts the speaker rotation speed in the slow speed mode.", ParameterType.KNOB,
                     [0, 127],
                     0),
        DspParameter(9, "Fast Rate", "Adjusts the speaker rotation speed in the fast speed mode.", ParameterType.KNOB,
                     [0, 127],
                     0),
        DspParameter(10, "Vibrato/Chorus", "Selects the vibrato and the chorus type.", ParameterType.COMBO,
                     ["Off", "Vibrato 1", "Chorus 1", "Vibrato 2", "Chorus 2", "Vibrato 3", "Chorus 3"], 0),
        DspParameter(11, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(12, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                     0)]),
    DspEffect(16, "Pitch Shifter", "This effect transforms the pitch of the input signal.", [
        DspParameter(1, "Pitch", "Adjusts the pitch shift amount in quarter tone steps.",
                     ParameterType.KNOB, [-24, 24], 0),
        DspParameter(2, "High Damp", "Adjusts the high-range damp. A smaller number increases damping.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "Feedback", "Adjusts the feedback amount.", ParameterType.KNOB, [0, 127],
                     0),
        DspParameter(4, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(6, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(7, "Fine",
                     "Adjusts the pitch shift amount. –50 is a quarter note decrease, while +50 is a quarter note increase.",
                     ParameterType.KNOB, [-50, 50], 0)]),
    DspEffect(18, "Ring Modulator",
              "Multiplies the input signal with an internal oscillator signal to create a metallic sound.", [
                  DspParameter(1, "OSC Frequency", "Sets the reference frequency of the internal oscillator.",
                               ParameterType.KNOB, [0, 127], 0),
                  DspParameter(2, "LFO Rate", "Adjusts the LFO rate.",
                               ParameterType.KNOB, [0, 127], 0),
                  DspParameter(3, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127],
                               0),
                  DspParameter(4, "Tone", "Adjusts the timbre of the ring modulator input sound.", ParameterType.KNOB,
                               [0, 127], 0),
                  DspParameter(5, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                               0),
                  DspParameter(6, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                               0)]),
    DspEffect(5, "Reflection",
              "Simulates the initial reflection of reverberation. Applies acoustic ambiance and presence to notes.",
              [DspParameter(1, "Wet Level", "Adjusts the level of the effect sound.",
                            ParameterType.KNOB, [0, 127], 0),
               DspParameter(2, "Feedback", "Adjusts the repeat of the reflected sound.",
                            ParameterType.KNOB, [0, 127], 0),
               DspParameter(3, "Tone", "Adjusts the tone of the reflected sound.", ParameterType.KNOB,
                            [0, 127], 0),
               DspParameter(4, "Input Level", "Adjusts the input level.", ParameterType.KNOB, [0, 127],
                            0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(19, "Delay", "Delays the input signal and feeds it back to create a repeating effect.", []),
    DspEffect(20, "Piano Effect", "This effect is suited to acoustic piano play.",
              [DspParameter(1, "Lid Type",
                            "Adjusts how sound resonates in accordance with the opening state of a piano lid.",
                            ParameterType.COMBO, ["Closed", "SemiOpen", "FullOpen"], 0),
               DspParameter(2, "Reflection Level", "Adjusts the level of the initial reflection.",
                            ParameterType.KNOB, [0, 127], 0),
               DspParameter(3, "Input Level", "Adjusts the input level.", ParameterType.KNOB,
                            [0, 127], 0),
               DspParameter(4, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                            0),
               DspParameter(5, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                            0)]),
    DspEffect(13, "LFO Wah", "This is a “wah” effect that can automatically affect the frequency using an LFO.", [
        DspParameter(1, "Input Level",
                     "Adjusts the input level. The input signal can become distorted when the level of the sound being input, the number of chords, or the Resonance value is large. Adjust this parameter to eliminate such distortion.",
                     ParameterType.KNOB, [0, 127], 0),
        DspParameter(2, "Resonance", "Adjusts the strength of feedback.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "Manual", "Adjusts the wah filter reference frequency.", ParameterType.KNOB, [0, 127],
                     0),
        DspParameter(4, "LFO Rate", "Adjusts the LFO rate.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "LFO Depth", "Adjusts the LFO depth.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(6, "LFO Waveform", "Selects the LFO waveform.", ParameterType.COMBO,
                     ["Sine", "Triangle", "Random"], 0),
        DspParameter(7, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                     0),
        DspParameter(8, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                     0)]),
    DspEffect(14, "Auto Wah",
              "This is a “wah” effect that can automatically shift the frequency in accordance with the level of the input signal.",
              []),
    DspEffect(30, "Modeling Wah",
              "Simulates various types of wah pedals. This effect can automatically shift the frequency in accordance with the level of the input signal.",
              []),
    DspEffect(15, "Distortion", "Distortion, wah, and amp simulator combined into a single effect.", []),
    DspEffect(23, "Drive", "Simulates the drive of a musical instrument amplifier.", []),
    DspEffect(24, "Amp Cabinet", "Simulates the amp and speaker cabinet without drive and distortion.", []),
    DspEffect(17, "Multi Chorus (hidden)", "Hidden DSP effect.", []),
    DspEffect(25, "Hollow Body (hidden)", "Hidden DSP effect. It represents guitar body types.", [
        DspParameter(1, "Body type", "Body type.", ParameterType.COMBO,
                     ["Thin body", "Mid body", "Thick body", "Roundback", "Acc bass"], 0),
        DspParameter(2, "Body level", "Body level.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(3, "Amb type", "Amb type.", ParameterType.COMBO,
                     ["Type 0", "Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6", "Type 7"], 0),
        DspParameter(4, "Amb Level", "Amb Level.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(5, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127], 0),
        DspParameter(6, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127], 0)]),
    DspEffect(26, "Piano Body (hidden)",
              "Hidden DSP effect. It represents piano body types. This effect is suited to acoustic piano play.", [
                  DspParameter(1, "Body type", "Body type.", ParameterType.COMBO,
                               ["Piano 1", "Piano 2", "Piano 3"], 0),
                  DspParameter(2, "Body level L", "Body level LEFT.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(3, "Body level R", "Body level RIGHT.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(4, "Amb type", "Amb type.", ParameterType.COMBO,
                               ["Type 0", "Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6", "Type 7"], 0),
                  DspParameter(5, "Amb Level", "Amb Level.", ParameterType.KNOB, [0, 127], 0),
                  DspParameter(6, "Lid type", "Lid type.", ParameterType.COMBO,
                               ["Closed", "Semi Open", "Full Open", "Removed"], 0),
                  DspParameter(7, "Wet Level", "Adjusts the level of the effect sound.", ParameterType.KNOB, [0, 127],
                               0),
                  DspParameter(8, "Dry Level", "Adjusts the level of the direct sound.", ParameterType.KNOB, [0, 127],
                               0)]))


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

    def get_current_dsp_id(self) -> int:
        if self.currentTabName == TabName.DSP_1:
            return 0
        elif self.currentTabName == TabName.DSP_2:
            return 1
        elif self.currentTabName == TabName.DSP_3:
            return 2
        elif self.currentTabName == TabName.DSP_4:
            return 3
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
        output: str = "Current tab: " + str(self.currentTabName.value) + "\n" \
                      + "\nDSP 1: " + str(self.selectedDsp1.name if self.selectedDsp1 is not None else "OFF") \
                      + self.get_params_info(self.selectedDsp1) \
                      + "\nDSP 2: " + str(self.selectedDsp2.name if self.selectedDsp2 is not None else "OFF") \
                      + self.get_params_info(self.selectedDsp2) \
                      + "\nDSP 3: " + str(self.selectedDsp3.name if self.selectedDsp3 is not None else "OFF") \
                      + self.get_params_info(self.selectedDsp3) \
                      + "\nDSP 4: " + str(self.selectedDsp4.name if self.selectedDsp4 is not None else "OFF") \
                      + self.get_params_info(self.selectedDsp4)
        return output

    @staticmethod
    def get_params_info(dsp_effect: DspEffect) -> str:
        output: str = ""
        if dsp_effect is not None:
            for parameter in dsp_effect.dsp_parameter_list:
                output = output + "\n\t" + parameter.name + ": " + str(parameter.value)
        return output

    def get_current_dsp_params_as_list(self) -> list:
        output = []
        dsp_effect = self.get_current_dsp()
        if dsp_effect is not None:
            for parameter in dsp_effect.dsp_parameter_list:
                if parameter.type == ParameterType.COMBO:
                    output.append(parameter.choices.index(parameter.value))
                elif parameter.type == ParameterType.KNOB:
                    output.append(parameter.value - parameter.choices[0])
        return output

    # @staticmethod
    # def print_updated_parameter_value(dsp_parameter: DspParameter):
    #     print("Setting " + dsp_parameter.name + ": " + str(dsp_parameter.value))

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
