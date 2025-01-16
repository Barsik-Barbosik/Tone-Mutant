from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton

from constants import constants
from ui.gui_helper import GuiHelper
from utils.utils import resource_path


class TopWidget(QWidget):
    # redraw_upper_volume_knob_signal = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core

        self.channel = 0
        self.layout = QHBoxLayout(self)

        label = QLabel("UPPER 1 Volume:")
        self.layout.addWidget(label)
        self.outer_upper_volume_knob_layout = QHBoxLayout()
        self.inner_upper_volume_knob_layout = GuiHelper.create_knob_input(self.core.tone.upper_volume,
                                                                          self.on_volume_change)
        self.outer_upper_volume_knob_layout.addLayout(self.inner_upper_volume_knob_layout)
        self.layout.addLayout(self.outer_upper_volume_knob_layout)

        self.layout.addWidget(GuiHelper.get_spacer())  # --------------------------

        self.tone_name_label = QLabel(constants.DEFAULT_TONE_NAME)
        self.tone_name_label.setObjectName("tone-name-label")
        self.layout.addWidget(self.tone_name_label)

        self.layout.addWidget(GuiHelper.get_spacer())  # --------------------------

        synchronize_tone_button = QPushButton(" Synchronize Tone", self)
        synchronize_tone_button.setIcon(QIcon(resource_path("resources/piano.png")))
        synchronize_tone_button.setObjectName("top-widget-button")
        synchronize_tone_button.clicked.connect(self.core.synchronize_tone_with_synth)
        self.layout.addWidget(synchronize_tone_button)

        randomize_tone_button = QPushButton(" Randomize Tone", self)
        randomize_tone_button.setIcon(QIcon(resource_path("resources/random_wand.png")))
        randomize_tone_button.setObjectName("top-widget-button")
        # randomize_tone_button.clicked.connect(self.on_randomize_tone_button_pressed)
        self.layout.addWidget(randomize_tone_button)

        # self.redraw_volume_knob_signal.connect(self.redraw_upper_volume_knob)

    def on_volume_change(self, parameter):
        self.core.send_parameter_change_sysex(parameter)

    # def on_randomize_tone_button_pressed(self):
    #     msg = "Setting random main parameters and selecting 1–2 random DSP modules"
    #     self.core.log(f"[INFO] {msg}...")
    #     self.core.main_window.loading_animation.start()
    #
    #     self.core.main_window.central_widget.on_random_button_pressed()
    #
    #     # Random DSP modules
    #     random_dsp_1 = random.randint(0, self.core.main_window.central_widget.dsp_page_1.list_widget.count() - 1)
    #     random_dsp_2 = random.randint(0, self.core.main_window.central_widget.dsp_page_2.list_widget.count() - 1)
    #
    #     if random_dsp_1 == 0 and random_dsp_2 > 0:  # swap
    #         random_dsp_1, random_dsp_2 = random_dsp_2, random_dsp_1
    #
    #     self.core.main_window.central_widget.dsp_page_1.list_widget.setCurrentRow(random_dsp_1)
    #     self.core.main_window.central_widget.dsp_page_2.list_widget.setCurrentRow(random_dsp_2)
    #
    #     if random_dsp_1 > 0 or random_dsp_2 > 0:
    #         msg += ": " + ", ".join(filter(None, [
    #             self.core.tone.dsp_module_1.name if random_dsp_1 > 0 else None,
    #             self.core.tone.dsp_module_2.name if random_dsp_2 > 0 else None
    #         ]))
    #
    #     self.core.show_status_msg(msg, 3000)
    #     self.core.pause_status_bar_updates(True)
    #
    #     # Random DSP params
    #     worker = Worker(self.randomize_dsp_params, random_dsp_1, random_dsp_2)
    #     worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
    #     worker.start()

    # def randomize_dsp_params(self, random_dsp_1, random_dsp_2):
    #     if random_dsp_1 > 0:
    #         time.sleep(0.3)
    #         self.core.main_window.central_widget.dsp_page_1.on_random_button_pressed(
    #             self.core.main_window.central_widget.dsp_page_1.block_id)
    #
    #     if random_dsp_2 > 0:
    #         time.sleep(0.3)
    #         self.core.main_window.central_widget.dsp_page_2.on_random_button_pressed(
    #             self.core.main_window.central_widget.dsp_page_2.block_id)
    #
    #     self.core.pause_status_bar_updates(False)
    #     self.core.main_window.loading_animation.stop()

    # @Slot()
    # def redraw_upper_volume_knob(self):
    #     GuiHelper.clear_layout(self.inner_upper_volume_knob_layout)
    #     self.inner_upper_volume_knob_layout = GuiHelper.create_knob_input(self.core.tone.upper_volume,
    #                                                                       self.on_volume_change)
    #     self.outer_upper_volume_knob_layout.addLayout(self.inner_upper_volume_knob_layout)
