from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget, QFormLayout, QLineEdit, QDial, \
    QLabel, QListWidget, QHBoxLayout, QSpinBox, QSizePolicy

from enums.enums import ParameterType
from model.DspEffect import DspEffect
from model.MainModel import MainModel

KNOB_SIZE = 40


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_model = MainModel()
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)
        tab_widget = QTabWidget(self)
        tab_widget.addTab(self.create_dsp_page(main_model.currentDsp1), 'DSP 1')
        tab_widget.addTab(self.create_dsp_page(main_model.currentDsp2), 'DSP 2')
        tab_widget.addTab(self.create_dsp_page(main_model.currentDsp3), 'DSP 3')
        tab_widget.addTab(self.create_dsp_page(main_model.currentDsp4), 'DSP 4')
        tab_widget.addTab(self.create_main_params_page(), 'Main parameters')  # TODO: should be the first tab

        main_layout.addWidget(tab_widget, 0, 0, 2, 1)

    def create_dsp_page(self, current_dsp: DspEffect):
        dsp_page = QWidget(self)

        hbox_layout = QHBoxLayout(self)
        dsp_page.setLayout(hbox_layout)
        list_widget = QListWidget(self)
        list_widget.insertItem(0, "OFF")
        list_widget.insertItem(1, "Red")
        list_widget.insertItem(2, "Orange")
        list_widget.insertItem(3, "Blue")
        list_widget.insertItem(4, "White")
        list_widget.insertItem(5, "Green")
        # list_widget.clicked.connect(self.clicked)
        hbox_layout.addWidget(list_widget)

        qgrid_layout = QGridLayout(self)
        for idx, dsp_parameter in enumerate(current_dsp.dsp_parameter_list):
            print(dsp_parameter.name)
            if dsp_parameter.type == ParameterType.COMBO:
                print("COMBO")
                qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
                qgrid_layout.addWidget(QLineEdit(), idx, 1)
            elif dsp_parameter.type == ParameterType.KNOB:
                self.create_knob_input(dsp_parameter, idx, qgrid_layout)
            elif dsp_parameter.type == ParameterType.KNOB_WITH_MIDDLE:
                self.create_knob_with_middle_input(dsp_parameter, idx, qgrid_layout)

        empty_filler = QWidget(self)
        empty_filler.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        qgrid_layout.addWidget(empty_filler)
        hbox_layout.addLayout(qgrid_layout)
        return dsp_page

    def create_knob_input(self, dsp_parameter, idx, qgrid_layout):
        print("KNOB")
        knob_value_input = QSpinBox(self)
        knob_value_input.setMinimum(dsp_parameter.settings[0])
        knob_value_input.setMaximum(dsp_parameter.settings[1])
        knob = QDial(self)
        knob.setMinimum(knob_value_input.minimum())
        knob.setMaximum(knob_value_input.maximum())
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda state, kn=knob, inp=knob_value_input: self.on_knob_changed(kn, inp))
        hbox = QHBoxLayout(self)
        hbox.addWidget(knob_value_input)
        hbox.addWidget(knob)
        qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
        qgrid_layout.addLayout(hbox, idx, 1)

    def create_knob_with_middle_input(self, dsp_parameter, idx, qgrid_layout):
        print("KNOB_WITH_MIDDLE")
        knob_value_input = QSpinBox(self)
        knob_value_input.setMinimum(dsp_parameter.settings[0])
        knob_value_input.setMaximum(dsp_parameter.settings[2])
        knob = QDial(self)
        knob.setMinimum(knob_value_input.minimum())
        knob.setMaximum(knob_value_input.maximum())
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda state, kn=knob, inp=knob_value_input: self.on_knob_changed(kn, inp))
        hbox = QHBoxLayout(self)
        hbox.addWidget(knob_value_input)
        hbox.addWidget(knob)
        qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
        qgrid_layout.addLayout(hbox, idx, 1)

    @staticmethod
    def on_knob_changed(knob, knob_value_input):
        knob_value_input.setValue(knob.value())

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
