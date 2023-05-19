from model.dsp_module import DspModule
from model.main_parameters_module import MainParametersModule


class Tone:
    def __init__(self):
        self.main_parameters_module: MainParametersModule = MainParametersModule()
        self.dsp_module_1: DspModule = None
        self.dsp_module_2: DspModule = None
        self.dsp_module_3: DspModule = None
        self.dsp_module_4: DspModule = None

    def to_json(self):
        obj = {
            "main": self.main_parameters_module.main_parameter_list,
            "DSP": [
                {"DSP_1": self.dsp_module_1,
                 "DSP_2": self.dsp_module_2,
                 "DSP_3": self.dsp_module_3,
                 "DSP_4": self.dsp_module_4
                 }
            ]}
        return obj
