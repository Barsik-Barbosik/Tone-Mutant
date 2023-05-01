from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget, QFormLayout, QDial, \
    QLabel, QListWidget, QHBoxLayout, QSpinBox, QSizePolicy, QComboBox, QListWidgetItem

from enums.enums import ParameterType
from model.DspEffect import DspEffect
from model.DspParameter import DspParameter
from model.MainModel import MainModel

KNOB_SIZE = 40


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_model = MainModel()
        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        self.qgrid_layout1 = QGridLayout(self)
        self.qgrid_layout2 = QGridLayout(self)
        self.qgrid_layout3 = QGridLayout(self)
        self.qgrid_layout4 = QGridLayout(self)

        tab_widget = QTabWidget(self)
        tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp1), 'DSP 1')
        # tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp2), 'DSP 2')
        # tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp3), 'DSP 3')
        # tab_widget.addTab(self.create_dsp_page(self.main_model.currentDsp4), 'DSP 4')
        tab_widget.addTab(self.create_main_params_page(), 'Main parameters')  # TODO: should be the first tab

        main_layout.addWidget(tab_widget, 0, 0, 2, 1)

    def create_dsp_page(self, current_dsp: DspEffect):
        dsp_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        dsp_page.setLayout(hbox_layout)

        list_widget = QListWidget(self)
        list_widget.insertItem(0, "OFF")
        for idx, dsp_effect in enumerate(self.main_model.getDspList()):
            item = QListWidgetItem()
            item.setText(dsp_effect.name)
            item.setData(Qt.UserRole, dsp_effect.id)
            list_widget.insertItem(idx + 1, item)

        list_widget.itemClicked.connect(lambda state, lw=list_widget: self.on_list_widget_click(lw))
        hbox_layout.addWidget(list_widget)  # left side

        self.update_parameter_panel()
        hbox_layout.addLayout(self.qgrid_layout1)  # right side

        return dsp_page

    def update_parameter_panel(self):
        self.clear_layout(self.qgrid_layout1)

        if self.main_model.currentDsp1 is not None:
            for idx, dsp_parameter in enumerate(self.main_model.currentDsp1.dsp_parameter_list):
                if dsp_parameter.type == ParameterType.COMBO:
                    self.create_combo_input(dsp_parameter, idx, self.qgrid_layout1)
                elif dsp_parameter.type == ParameterType.KNOB:
                    self.create_knob_input(dsp_parameter, idx, self.qgrid_layout1)
        else:
            self.qgrid_layout1.addWidget(QLabel("------------------- OFF ----------------"), 0, 0)

        empty_filler = QWidget(self)
        empty_filler.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.qgrid_layout1.addWidget(empty_filler)

    def create_combo_input(self, dsp_parameter: DspParameter, idx: int, qgrid_layout: QGridLayout):
        print("creating combo for " + dsp_parameter.name)
        combo_box = QComboBox(self)
        combo_box.addItems(dsp_parameter.choices)
        combo_box.currentIndexChanged.connect(lambda state, cb=combo_box: self.on_combo_changed(cb, dsp_parameter.name))
        qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
        qgrid_layout.addWidget(combo_box, idx, 1)

    def create_knob_input(self, dsp_parameter: DspParameter, idx: int, qgrid_layout: QGridLayout):
        print("creating knob for " + dsp_parameter.name)
        knob_value_input = QSpinBox(self)
        knob_value_input.setMinimum(dsp_parameter.choices[0])
        knob_value_input.setMaximum(dsp_parameter.choices[1])
        knob = QDial(self)
        knob.setMinimum(knob_value_input.minimum())
        knob.setMaximum(knob_value_input.maximum())
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda state, kn=knob, inp=knob_value_input: self.on_knob_changed(kn, inp, dsp_parameter.name))
        knob_value_input.valueChanged.connect(lambda state, inp=knob_value_input, kn=knob: self.on_knob_spinbox_changed(inp, kn, dsp_parameter.name))
        hbox = QHBoxLayout(self)
        hbox.addWidget(knob_value_input)
        hbox.addWidget(knob)
        qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
        qgrid_layout.addLayout(hbox, idx, 1)

    def on_list_widget_click(self, list_widget: QListWidget):
        item_id: int = list_widget.currentItem().data(Qt.UserRole)
        print(str(item_id) + " - " + list_widget.currentItem().text())
        self.main_model.setCurrentDsp1(item_id)
        self.update_parameter_panel()

    @staticmethod
    def on_combo_changed(combo: QComboBox, dsp_parameter_name: str):
        print("setting " + dsp_parameter_name)
        print(combo.currentText())

    @staticmethod
    def on_knob_changed(knob: QDial, knob_value_input: QSpinBox, dsp_parameter_name: str):
        if knob.value() != knob_value_input.value():
            print("setting " + dsp_parameter_name)
            print(knob.value())
            knob_value_input.setValue(knob.value())

    @staticmethod
    def on_knob_spinbox_changed(knob_value_input: QSpinBox, knob: QDial, dsp_parameter_name: str):
        if knob_value_input.value() != knob.value():
            print("setting " + dsp_parameter_name)
            print(knob_value_input.value())
            knob.setValue(knob_value_input.value())

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

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
