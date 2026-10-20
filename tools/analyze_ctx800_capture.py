"""Summarize recorded observations without contacting the keyboard."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from constants import constants
from constants.enums import ParameterType
from models.tone import Tone


def analyze():
    root = Path(__file__).resolve().parents[1]
    baseline = json.loads((root / "captures/ctx800-readonly-20261019.json").read_text(encoding="utf-8"))
    survey = json.loads((root / "captures/ctx800-survey-20261019.json").read_text(encoding="utf-8"))
    tone = Tone()
    descriptors = tone.main_parameter_list + tone.advanced_parameter_list
    known = {(parameter.param_number, parameter.block0): parameter.name for parameter in descriptors}
    known.update({(0, 0): "Tone name", (85, 0): "DSP module", (86, 0): "DSP bypass", (87, 0): "DSP data"})
    checks = descriptors + [p for module in constants.ALL_DSP_MODULES for p in module.dsp_parameter_list + [module.bypass]]
    value_checks = sum(len(p.choices) if p.type == ParameterType.COMBO else p.choices[1] - p.choices[0] + 1
                       for p in checks if p.type != ParameterType.SPECIAL_DELAY_KNOB)
    total = len(baseline["requests"]) + len(survey["requests"])
    answered = sum(entry["reply"] is not None for capture in (baseline, survey) for entry in capture["requests"])
    lines = [
        "# Resultados del CT-X800: lecturas y pruebas automatizadas",
        "",
        "Fecha: 19 de octubre de 2026. Instrumento identificado por el usuario como CT-X800.",
        "Puertos detectados: CASIO USB-MIDI 0 (entrada) y CASIO USB-MIDI 1 (salida).",
        "Los mensajes de prueba usaron IPR (acción 00), categoría 3, memoria 3 y conjunto 0.",
        "No se enviaron escrituras IPS, cambios de programa ni notas durante estas capturas.",
        "",
        "## Evidencia del instrumento",
        "",
        f"- {total} consultas transmitidas y {answered} respuestas coincidentes.",
        "- Primera captura: 40 consultas contestadas, con parámetros de la interfaz, Line Select y datos DSP.",
        "- Exploración posterior: respondieron 123 direcciones, de 0 a 122, bloque 0. No respondieron 200, 201 ni 202 dentro de 0,3 segundos por consulta.",
        "- Las direcciones exploradas proceden del lector TON original. No son descubrimientos nuevos del protocolo.",
        "- Line Select (44) devolvió 1. Está documentado por Casio; tras esta captura se incorporó como Ruta de salida en Avanzados.",
        "- Los parámetros 100, 101 y 106 devolvieron cinco bytes de datos. Su significado y rango no se han confirmado.",
        "- DSP 1 devolvió ID 1; DSP 2, 3 y 4 devolvieron 7F 7F. Consultar esas ranuras no demuestra cuatro efectos utilizables simultáneamente.",
        "",
        "Una respuesta acredita lectura de esa dirección con esta configuración. No prueba que admita escritura, que su función sea audible ni cuáles son sus extremos válidos. La ausencia de respuesta tampoco prueba inexistencia del parámetro.",
        "",
        "## Correcciones verificadas en software",
        "",
        "1. Ataque/liberación: el decodificador podía devolver -1 o volver a 0 para datos fuera de su tabla. Ahora limita el resultado a los extremos 0 y 127.",
        "2. MIDI entrante: mensajes vacíos o truncados provocaban IndexError; ecos de solicitudes y otros modelos podían interpretarse como valores. Ahora se comprueban cabecera, acción, tamaño y categoría antes de actualizar controles.",
        "3. Archivos TON: se leían en orden incorrecto los campos de cabecera y no se verificaba el CRC. Ahora se verifican tamaño y checksum antes de aceptar el archivo.",
        "4. Empaquetado de datos vacíos: generaba un byte extra. Corregido y contrastado con un codificador independiente.",
        "5. Mensajes MIDI de tiempo real intercalados: invalidaban una trama SysEx parcial en el lector TON. Ahora se conservan los datos de esa trama.",
        "6. Delay: concatenar texto perdía ceros, por ejemplo 100 se convertía en 10. Se comprobó ida y vuelta de 1 a 1099 contra el formato existente, sin escribir esos valores en el instrumento.",
        "7. Índice y longitud de arrays: el constructor TON usaba pares de 8 bits; a partir de 128 generaba bytes incompatibles con el formato de 7 bits. Corregido.",
        "8. Límites de modelo: Octave Shift usa -2 a +2 y Note-off Velocity tres opciones en CT-X700/800, conservando los valores MIDI centrales correctos. Otros modelos conservan sus opciones anteriores.",
        "",
        "Las dos últimas restricciones de modelo se contrastaron con las tablas de parámetros del [manual MIDI oficial de Casio, páginas 27–28](https://www.casio.com/content/dam/casio/global/support/manuals/electronic-musical-instruments/pdf/008-en/c/CT-X800-midi-imple_EN.pdf). No se ensayaron los límites mediante escrituras al teclado.",
        "",
        "## Pruebas reproducibles",
        "",
        "La etapa de diagnóstico pasó 35 pruebas, incluidas las 19 iniciales de accesibilidad. La ampliación posterior en español y con Experimental se documenta en ACCESIBILIDAD.md.",
        f"La suite comprueba {value_checks} valores de los descriptores, todos los 16384 enteros representables en dos bytes de 7 bits, otros 16384 valores de entrada del decodificador de ataque/liberación, 1099 valores de delay y más de 4000 mensajes incompletos o aleatorios. Estos son casos de software, no un barrido de valores escrito en el hardware.",
        "También se reproducen las capturas mediante MidiService y Core, con una ventana Qt real y dispositivos sustituidos. Los valores de los controles quedan dentro de sus opciones/rangos y esa reproducción no genera escrituras de parámetros.",
        "",
        "```powershell",
        r".\.runtime\python310\python.exe -m unittest discover -s tests -v",
        "```",
        "",
        "Las capturas originales están en `captures/ctx800-readonly-20261019.json` y `captures/ctx800-survey-20261019.json`. Contienen paquetes transmitidos, recibidos y resultados por consulta. Este informe se regenera con `tools/analyze_ctx800_capture.py` sin conectar el teclado.",
        "",
        "## Pendientes para investigar funciones y rangos",
        "",
        "- Asociar direcciones sin control visible con cambios manuales de un único ajuste del teclado y comparar capturas antes/después.",
        "- Confirmar el significado de Line Select en el sonido actual antes de exponerlo como un control nuevo.",
        "- Contrastar la tabla especial de ataque/liberación con ajustes manuales conocidos: la ida/vuelta de su código no demuestra que la escala coincida con la del CT-X800.",
        "- Probar cambios de un parámetro documentado y restaurar su valor inicial; guardar ambas lecturas y la observación auditiva.",
        "- Comprobar NVDA con la aplicación real. Los tests de propiedades Qt no sustituyen escuchar el lector de pantalla.",
        "",
        "## Inventario bruto de la exploración",
        "",
        "Los nombres solo identifican controles ya existentes. No se atribuyen funciones a los valores restantes.",
        "",
        "| ID decimal | Control existente, si coincide en bloque 0 | Bytes | Datos hexadecimales |",
        "| --- | --- | --- | --- |",
    ]
    for entry in survey["requests"]:
        reply = entry["reply"]
        values = reply["data"] if reply else None
        raw = bytes(values).hex(" ").upper() if values is not None else "Sin respuesta en el plazo"
        lines.append("| {} | {} | {} | {} |".format(entry["parameter"],
                     known.get((entry["parameter"], entry["block"]), "Sin control identificado"),
                     len(values) if values is not None else "—", raw))
    target = root / "docs" / "RESULTADOS_CTX800.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("{}; {} sent, {} answered; {} descriptor cases".format(target, total, answered, value_checks))


if __name__ == "__main__":
    analyze()
