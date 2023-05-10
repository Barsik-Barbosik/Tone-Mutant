from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QTabWidget, QFormLayout, QDial, \
    QLabel, QListWidget, QHBoxLayout, QSpinBox, QSizePolicy, QComboBox, QListWidgetItem, QTextBrowser, QSpacerItem

from enums.enums import ParameterType, TabName
from model.DspEffect import DspEffect
from model.DspParameter import DspParameter
from model.MainModel import MainModel
from my_midi import Midi

KNOB_SIZE = 40


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.midi = Midi()
        self.main_model = MainModel()
        self.output_tab_textbox = QTextBrowser()

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.create_main_params_page(), TabName.MAIN_PARAMETERS.value)
        self.tab_widget.addTab(self.create_dsp_page(QGridLayout(self)), TabName.DSP_1.value)
        self.tab_widget.addTab(self.create_dsp_page(QGridLayout(self)), TabName.DSP_2.value)
        self.tab_widget.addTab(self.create_dsp_page(QGridLayout(self)), TabName.DSP_3.value)
        self.tab_widget.addTab(self.create_dsp_page(QGridLayout(self)), TabName.DSP_4.value)
        self.tab_widget.addTab(self.create_output_page(), TabName.OUTPUT.value)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tab_widget, 0, 0, 2, 1)

    def on_tab_changed(self, i):
        self.main_model.currentTabName = TabName(self.tab_widget.tabText(self.tab_widget.currentIndex()))
        self.show_status_msg(self.main_model.currentTabName.value + ": " + self.main_model.get_current_dsp_name())
        if self.main_model.currentTabName == TabName.OUTPUT:
            self.output_tab_textbox.setPlainText(self.main_model.get_output_text())

    def create_dsp_page(self, qgrid_layout: QGridLayout) -> QWidget:
        dsp_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        dsp_page.setLayout(hbox_layout)

        list_widget = QListWidget(self)
        list_widget.insertItem(0, "OFF")
        for idx, dsp_effect in enumerate(self.main_model.get_dsp_effects_tuple()):
            item = QListWidgetItem()
            item.setText(dsp_effect.name)
            item.setData(Qt.UserRole, dsp_effect.id)
            list_widget.insertItem(idx + 1, item)
        list_widget.setCurrentRow(0)
        list_widget.itemClicked.connect(lambda state, lw=list_widget: self.on_list_widget_click(lw, qgrid_layout))
        hbox_layout.addWidget(list_widget)  # left side

        self.redraw_dsp_params_panel(qgrid_layout)
        hbox_layout.addLayout(qgrid_layout)  # right side

        return dsp_page

    def redraw_dsp_params_panel(self, qgrid_layout: QGridLayout):
        self.clear_layout(qgrid_layout)

        if self.main_model.get_current_dsp() is not None:
            for idx, dsp_parameter in enumerate(self.main_model.get_current_dsp().dsp_parameter_list):
                qgrid_layout.addWidget(QLabel(dsp_parameter.name + ":"), idx, 0)
                if dsp_parameter.type == ParameterType.COMBO:
                    qgrid_layout.addWidget(self.create_combo_input(dsp_parameter), idx, 1)
                elif dsp_parameter.type == ParameterType.KNOB:
                    qgrid_layout.addLayout(self.create_knob_input(dsp_parameter), idx, 1)
        else:
            qgrid_layout.addWidget(QLabel("------------------- OFF ----------------"), 0, 0)

        qgrid_layout.addWidget(self.get_spacer())

    def create_combo_input(self, dsp_parameter: DspParameter) -> QComboBox:
        combo_box = QComboBox(self)
        combo_box.addItems(dsp_parameter.choices)
        combo_box.setCurrentIndex(dsp_parameter.default_value)
        combo_box.currentIndexChanged.connect(lambda state: self.on_combo_changed(combo_box, dsp_parameter))
        return combo_box

    def create_knob_input(self, dsp_parameter: DspParameter) -> QHBoxLayout:
        knob_spinbox = QSpinBox(self)
        knob_spinbox.setMinimum(dsp_parameter.choices[0])
        knob_spinbox.setMaximum(dsp_parameter.choices[1])
        knob_spinbox.setValue(dsp_parameter.default_value)
        knob = QDial(self)
        knob.setMinimum(knob_spinbox.minimum())
        knob.setMaximum(knob_spinbox.maximum())
        knob.setValue(dsp_parameter.default_value)
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda state: self.on_knob_changed(knob, knob_spinbox, dsp_parameter))
        knob_spinbox.valueChanged.connect(
            lambda state: self.on_knob_spinbox_changed(knob_spinbox, knob, dsp_parameter))
        hbox = QHBoxLayout(self)
        hbox.addWidget(knob_spinbox)
        hbox.addWidget(knob)
        return hbox

    def on_list_widget_click(self, list_widget: QListWidget, qgrid_layout: QGridLayout):
        item_id: int = list_widget.currentItem().data(Qt.UserRole)
        print(str(item_id) + " - " + list_widget.currentItem().text())
        dsp_effect: DspEffect = self.main_model.get_dsp_effect_by_id(item_id)
        self.main_model.set_current_dsp(item_id)
        self.show_status_msg(dsp_effect.description if dsp_effect is not None else "")
        self.redraw_dsp_params_panel(qgrid_layout)

    def on_combo_changed(self, combo: QComboBox, dsp_parameter: DspParameter):
        dsp_parameter.value = combo.currentText()
        self.main_model.print_updated_parameter_value(dsp_parameter)

    def on_knob_changed(self, knob: QDial, linked_knob_spinbox: QSpinBox, dsp_parameter: DspParameter):
        if knob.value() != linked_knob_spinbox.value():
            linked_knob_spinbox.setValue(knob.value())
            dsp_parameter.value = knob.value()
            self.main_model.print_updated_parameter_value(dsp_parameter)

    def on_knob_spinbox_changed(self, knob_spinbox: QSpinBox, linked_knob: QDial, dsp_parameter: DspParameter):
        if knob_spinbox.value() != linked_knob.value():
            linked_knob.setValue(knob_spinbox.value())
            dsp_parameter.value = knob_spinbox.value()
            self.main_model.print_updated_parameter_value(dsp_parameter)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def show_status_msg(self, text: str):
        self.parent().status_bar.showMessage(text)

    def create_main_params_page(self) -> QWidget:
        main_params_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        left_layout = QFormLayout()
        right_layout = QFormLayout()

        for idx, parameter in enumerate(self.main_model.get_main_params_tuple()):
            if idx < 7:
                if parameter.type == ParameterType.COMBO:
                    left_layout.addRow(parameter.name + ":", self.create_combo_input(parameter))
                elif parameter.type == ParameterType.KNOB:
                    left_layout.addRow(parameter.name + ":", self.create_knob_input(parameter))
            else:
                if parameter.type == ParameterType.COMBO:
                    right_layout.addRow(parameter.name + ":", self.create_combo_input(parameter))
                elif parameter.type == ParameterType.KNOB:
                    right_layout.addRow(parameter.name + ":", self.create_knob_input(parameter))

        hbox_layout.addLayout(left_layout)
        hbox_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        hbox_layout.addLayout(right_layout)
        main_params_page.setLayout(hbox_layout)
        return main_params_page

    def create_output_page(self) -> QWidget:
        output_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        hbox_layout.addWidget(self.output_tab_textbox)
        output_page.setLayout(hbox_layout)
        return output_page

    def get_spacer(self):
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer