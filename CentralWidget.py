from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget, QFormLayout, QDial, \
    QLabel, QListWidget, QHBoxLayout, QSpinBox, QSizePolicy, QComboBox

from enums.enums import ParameterType
from model.DspEffect import DspEffect
from model.MainModel import MainModel

KNOB_SIZE = 40


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_model = MainModel()
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        tab_widget = QTabWidget(self)
        tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp1), 'DSP 1')
        tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp2), 'DSP 2')
        tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp3), 'DSP 3')
        tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp4), 'DSP 4')
        tab_widget.addTab(self.create_main_params_page(), 'Main parameters')  # TODO: should be the first tab

        main_layout.addWidget(tab_widget, 0, 0, 2, 1)

    def create_dsp_page(self, current_dsp: DspEffect):
        dsp_page = QWidget(self)

        hbox_layout = QHBoxLayout(self)
        dsp_page.setLayout(hbox_layout)
        list_widget = QListWidget(self)
        list_widget.insertItem(0, "OFF")
        for dsp_effect in self.main_model.getDspList():
            list_widget.insertItem(dsp_effect.id, dsp_effect.name)

        # list_widget.clicked.connect(self.clicked)
        hbox_layout.addWidget(list_widget)

        qgrid_layout = QGridLayout(self)
        for idx, dsp_parameter in enumerate(current_dsp.dsp_parameter_list):
            if dsp_parameter.type == ParameterType.COMBO:
                self.create_combo_input(dsp_parameter, idx, qgrid_layout)
            elif dsp_parameter.type == ParameterType.KNOB:
                self.create_knob_input(dsp_parameter, idx, qgrid_layout)

        empty_filler = QWidget(self)
        empty_filler.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        qgrid_layout.addWidget(empty_filler)
        hbox_layout.addLayout(qgrid_layout)
        return dsp_page

    def create_combo_input(self, dsp_parameter, idx, qgrid_layout):
        combo_box = QComboBox(self)
        combo_box.addItems(dsp_parameter.choices)
        combo_box.currentIndexChanged.connect(lambda state, cb=combo_box: self.on_combo_changed(cb))
        qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
        qgrid_layout.addWidget(combo_box, idx, 1)

    def create_knob_input(self, dsp_parameter, idx, qgrid_layout):
        knob_value_input = QSpinBox(self)
        knob_value_input.setMinimum(dsp_parameter.choices[0])
        knob_value_input.setMaximum(dsp_parameter.choices[1])
        knob = QDial(self)
        knob.setMinimum(knob_value_input.minimum())
        knob.setMaximum(knob_value_input.maximum())
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda state, kn=knob, inp=knob_value_input: self.on_knob_changed(kn, inp))
        knob_value_input.valueChanged.connect(lambda state, inp=knob_value_input, kn=knob: self.on_knob_spinbox_changed(inp, kn))
        hbox = QHBoxLayout(self)
        hbox.addWidget(knob_value_input)
        hbox.addWidget(knob)
        qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
        qgrid_layout.addLayout(hbox, idx, 1)

    @staticmethod
    def on_combo_changed(combo):
        print(combo.currentText())

    @staticmethod
    def on_knob_changed(knob, knob_value_input):
        if knob.value() != knob_value_input.value():
            print(knob.value())
            knob_value_input.setValue(knob.value())

    @staticmethod
    def on_knob_spinbox_changed(knob_value_input, knob):
        if knob_value_input.value() != knob.value():
            print(knob_value_input.value())
            knob.setValue(knob_value_input.value())

    def create_main_params_page(self):
        main_params_page = QWidget(self)
        layout = QFormLayout()
        layout.addRow('Atk. time:', QSpinBox(self))
        layout.addRow('Rel. time:', QSpinBox(self))
        layout.addRow('Cutoff F:', QSpinBox(self))
        layout.addRow('Resonance:', QSpinBox(self))
        layout.addRow('Vibrato:', QSpinBox(self))
        layout.addRow('Oct. shift:', QSpinBox(self))
        layout.addRow('Volume:', QSpinBox(self))
        layout.addRow('Velocity sensitivity:', QSpinBox(self))
        layout.addRow('Rev. send:', QSpinBox(self))
        layout.addRow('Cho. send:', QSpinBox(self))
        layout.addRow('Dly. send:', QSpinBox(self))
        layout.addRow('Pitch band:', QSpinBox(self))
        layout.addRow('Modulation:', QSpinBox(self))
        main_params_page.setLayout(layout)
        return main_params_page
