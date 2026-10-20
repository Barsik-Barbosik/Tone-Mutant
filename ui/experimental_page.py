"""Accessible research workspace: captured evidence, bounded reads and opt-in editors."""
import json
from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QPushButton, QTextBrowser,
    QCheckBox, QGridLayout, QComboBox, QFileDialog, QMessageBox)

from constants import constants
from ui.gui_helper import GuiHelper
from ui.i18n import tr
from utils.utils import resource_path

DOCUMENTED_ADVANCED = {42, 44, 80}


class ExperimentalPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.core = parent.core
        self.pending = None
        self.observations = {}
        layout = QVBoxLayout(self)
        intro = QLabel("Investigación del CT-X800: una respuesta de lectura no confirma la función ni el rango de un parámetro.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        self.tabs = QTabWidget()
        self.tabs.setAccessibleName("Secciones de investigación experimental")
        layout.addWidget(self.tabs)
        self._create_observations()
        self._create_editors()
        self._create_questions()
        self.core.raw_parameter_signal.connect(self.receive_parameter)
        self.timeout_timer = QTimer(self)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self._read_timeout)

    def _create_observations(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.table = QTableWidget(126, 5)
        self.table.setAccessibleName("Parámetros por investigar y lecturas registradas")
        self.table.setAccessibleDescription("Tabla de solo lectura. Use las flechas para elegir un parámetro y Tab para consultar su valor actual.")
        self.table.setHorizontalHeaderLabels(["Parámetro", "Bloque", "Datos hexadecimales", "Origen y estado", "Interpretación"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        for column, width in enumerate((100, 65, 185, 185)):
            self.table.setColumnWidth(column, width)
        self.row_for = {}
        path = Path(resource_path("captures/ctx800-survey-20261019.json"))
        capture = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"requests": []}
        entries = {entry["parameter"]: entry for entry in capture["requests"]}
        known = {p.param_number: tr(p.name) for p in self.core.tone.main_parameter_list + self.core.tone.advanced_parameter_list if p.block0 == 0}
        for row, parameter in enumerate(list(range(123)) + [200, 201, 202]):
            self.row_for[(parameter, 0)] = row
            entry = entries.get(parameter, {})
            reply = entry.get("reply")
            values = reply["data"] if reply else None
            self.observations[(parameter, 0)] = {"parameter": parameter, "block": 0, "data": values,
                                                "origin": "captura inicial del 19/10/2026" if entry else "sin consultar"}
            cells = [str(parameter), "0", self._hex(values),
                     "Captura inicial" if reply else "Sin respuesta en la captura" if entry else "Sin consultar",
                     known.get(parameter, "Función o escala pendiente de identificar")]
            for column, text in enumerate(cells):
                self.table.setItem(row, column, QTableWidgetItem(text))
        self.table.setCurrentCell(0, 0)
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        self.read_button = QPushButton("Consultar seleccionado")
        self.read_button.setAccessibleDescription("Solicita el valor actual del parámetro seleccionado. Esta consulta no escribe valores.")
        self.read_button.clicked.connect(self.read_selected)
        save = QPushButton("Guardar instantánea…")
        save.clicked.connect(self.save_snapshot)
        compare = QPushButton("Comparar con instantánea…")
        compare.clicked.connect(self.compare_snapshot)
        for button in (self.read_button, save, compare):
            buttons.addWidget(button)
        layout.addLayout(buttons)
        self.result = QTextBrowser()
        self.result.setAccessibleName("Resultado de la consulta o comparación experimental")
        self.result.setMaximumHeight(130)
        self.result.setPlainText("Las lecturas iniciales pertenecen a la sesión del 19 de octubre de 2026. Consulte un parámetro para actualizarlo. Puede cambiar un ajuste manualmente en el teclado y comparar instantáneas.")
        layout.addWidget(self.result)
        self.tabs.addTab(page, "Lecturas e instantáneas")

    @staticmethod
    def _hex(values):
        return " ".join("{:02X}".format(value) for value in values) if values is not None else "Sin datos"

    def _announce(self, text):
        self.result.setPlainText(text)
        self.core.show_status_msg(text, 6000)

    def read_selected(self):
        row = self.table.currentRow()
        if row < 0 or self.pending is not None:
            return
        parameter, block = int(self.table.item(row, 0).text()), int(self.table.item(row, 1).text())
        self.pending = (parameter, block)
        self.read_button.setEnabled(False)
        self._announce("Consultando el parámetro {} del bloque {}…".format(parameter, block))
        self.timeout_timer.start(1500)
        # The finite list uses the same addresses as the original TON reader.
        length_field = 15 if parameter in (0, 84) else 13 if parameter == 87 else 0
        self.core.request_custom_parameter(parameter, block, 3, 3, 0, length_field)

    @Slot(int, int, object)
    def receive_parameter(self, parameter, block, values):
        if (parameter, block) != self.pending:
            return
        self.timeout_timer.stop()
        row = self.row_for[(parameter, block)]
        old = self.observations[(parameter, block)]["data"]
        self.observations[(parameter, block)] = {"parameter": parameter, "block": block, "data": list(values),
                                                "origin": datetime.now(timezone.utc).isoformat()}
        self.table.item(row, 2).setText(self._hex(values))
        self.table.item(row, 3).setText("Lectura actual")
        self.pending = None
        self.read_button.setEnabled(True)
        self._announce("Parámetro {}: {}. {}".format(parameter, self._hex(values),
                       "Cambió respecto de la lectura anterior." if old != list(values) else "Sin cambios respecto de la lectura anterior."))

    def _read_timeout(self):
        if self.pending:
            parameter, block = self.pending
            self.table.item(self.row_for[self.pending], 3).setText("Sin respuesta en 1,5 segundos")
            self.pending = None
            self.read_button.setEnabled(True)
            self._announce("El parámetro {} no respondió dentro del plazo. Esto no confirma que no exista.".format(parameter))

    def snapshot(self):
        return {"format": "ToneMutant experimental v1", "model": self.core.tone.synthesizer_model,
                "values": list(self.observations.values())}

    def save_snapshot(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar instantánea experimental", "instantanea.json", "Archivos JSON (*.json)")
        if filename:
            try:
                Path(filename).write_text(json.dumps(self.snapshot(), ensure_ascii=False, indent=2), encoding="utf-8")
                self._announce("Instantánea guardada.")
            except OSError as error:
                QMessageBox.warning(self, "No se pudo guardar", str(error))

    def compare_snapshot(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Comparar con instantánea experimental", "", "Archivos JSON (*.json)")
        if filename:
            try:
                data = json.loads(Path(filename).read_text(encoding="utf-8"))
                if data.get("format") != "ToneMutant experimental v1":
                    raise ValueError("El archivo no es una instantánea experimental de Tone Mutant.")
                differences = []
                for old in data["values"]:
                    key = (old["parameter"], old["block"])
                    current = self.observations.get(key)
                    if current and current["data"] != old["data"]:
                        differences.append("Parámetro {}, bloque {}: {} → {}".format(*key, self._hex(old["data"]), self._hex(current["data"])))
                self._announce("\n".join(differences) if differences else "No hay diferencias con la instantánea seleccionada.")
            except (OSError, ValueError, KeyError, TypeError) as error:
                QMessageBox.warning(self, "No se pudo comparar", str(error))

    def _create_editors(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.enable_editing = QCheckBox("Habilitar edición de controles en investigación")
        self.enable_editing.setAccessibleDescription("Activa los parámetros heredados cuya función o escala aún no se ha comprobado en el CT-X800. Las direcciones sin identificar siguen siendo de solo lectura.")
        layout.addWidget(self.enable_editing)
        self.editors = QWidget()
        self.editor_grid = QGridLayout(self.editors)
        layout.addWidget(self.editors)
        self.editors.setEnabled(False)
        self.enable_editing.toggled.connect(self.editors.setEnabled)
        self.refresh_editors()
        effects = QHBoxLayout()
        label = QLabel("Efecto experimental:")
        self.effect_combo = QComboBox()
        self.effect_combo.setAccessibleName("Efecto DSP experimental")
        for module in constants.ALL_DSP_MODULES:
            if "(hidden)" in module.name:
                self.effect_combo.addItem(tr(module.name), module.id)
        label.setBuddy(self.effect_combo)
        self.layer_combo = QComboBox()
        self.layer_combo.setAccessibleName("Ranura DSP para el efecto experimental")
        for index in range(4):
            self.layer_combo.addItem("DSP {}".format(index + 1), index)
        self.apply_effect = QPushButton("Aplicar efecto experimental")
        self.apply_effect.setEnabled(False)
        self.enable_editing.toggled.connect(self.apply_effect.setEnabled)
        self.apply_effect.clicked.connect(self._apply_effect)
        for widget in (label, self.effect_combo, self.layer_combo, self.apply_effect):
            effects.addWidget(widget)
        layout.addLayout(effects)
        layout.addStretch()
        self.tabs.addTab(page, "Controles en investigación")

    def refresh_editors(self):
        GuiHelper.clear_layout(self.editor_grid)
        parameters = [p for p in self.core.tone.advanced_parameter_list if p.param_number not in DOCUMENTED_ADVANCED]
        GuiHelper.fill_qgrid_with_params(self.editor_grid, parameters, constants.RIGHT_SIDE_ADVANCED_PARAMS,
                                        self._change_parameter)

    def _change_parameter(self, parameter):
        if self.enable_editing.isChecked():
            self.core.send_parameter_change_sysex(parameter)

    def _apply_effect(self):
        if self.enable_editing.isChecked():
            self.core.update_dsp_module_from_list(self.layer_combo.currentData(), self.effect_combo.currentData())

    def _create_questions(self):
        questions = QTextBrowser()
        questions.setAccessibleName("Preguntas pendientes de investigación del CT-X800")
        questions.setHtml("""<h2>Preguntas de investigación</h2>
        <p><b>Direcciones sin identificar.</b> ¿Qué cambia al modificar manualmente un único ajuste del teclado? Compare lecturas antes y después. Una respuesta no confirma una función audible.</p>
        <p><b>Parámetros 100, 101 y 106.</b> Devuelven cinco bytes. Su significado, escala y posibilidad de escritura no están confirmados.</p>
        <p><b>Ataque y liberación.</b> La tabla de conversión procede del proyecto original. Falta contrastarla con ajustes manuales conocidos del CT-X800.</p>
        <p><b>Ranuras DSP.</b> Las cuatro ranuras responden, pero eso no demuestra que el CT-X800 procese cuatro efectos simultáneos.</p>
        <p><b>Efectos heredados ocultos.</b> Chorus múltiple, cuerpo de piano y cuerpo hueco necesitan comprobación auditiva y de rangos.</p>
        <p><b>Tablas de ondas, timbres A/B y eventos.</b> Leer sus valores no confirma que los cambios se apliquen en tiempo real.</p>
        <p><b>Direcciones 200 a 202.</b> No respondieron en la captura inicial. Pueden requerir otra categoría, memoria, bloque o contexto.</p>
        <p><b>Reglas de esta sección.</b> Las direcciones sin identificar solo se consultan. Los controles heredados requieren habilitar su edición expresamente. Las instantáneas experimentales no se cargan como tonos.</p>""")
        self.tabs.addTab(questions, "Preguntas pendientes")
