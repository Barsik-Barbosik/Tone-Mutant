"""Spanish presentation strings. Protocol names and JSON keys remain stable."""
import re
from functools import lru_cache

STRINGS = {
    "Pure sine note": "Nota senoidal pura", "Pure sine note (variation)": "Nota senoidal pura, variante", "Pure sine at precisely 1kHz": "Nota senoidal pura de exactamente 1 kHz", "Pure sine at precisely 1kHz (variation)": "Nota senoidal pura de 1 kHz, variante", "White noise": "Ruido blanco", "Pink noise": "Ruido rosa", "Pure sine swept through all octaves": "Barrido senoidal de todas las octavas", "Pure sine swept through multiple octaves": "Barrido senoidal de varias octavas", "Pure sine swept through one octave": "Barrido senoidal de una octava", "No-frills piano sound": "Sonido de piano sencillo", "Spoken digits 1-5": "Voz que pronuncia los números del 1 al 5",
    "<h2>Settings</h2>": "<h2>Configuración</h2>", "<h2>Delete a Tone</h2>": "<h2>Borrar un tono</h2>", "<h2>Rename a Tone</h2>": "<h2>Renombrar un tono</h2>", "<h2>Request a Parameter</h2>": "<h2>Consultar un parámetro</h2>", "<h2>Save Current Tone</h2>": "<h2>Guardar el tono actual</h2>", "<h2>User Tone Manager</h2>": "<h2>Gestor de tonos de usuario</h2>",
    "Tone successfully saved!": "Tono guardado correctamente.", "Tone successfully renamed!": "Tono renombrado correctamente.", "Tone successfully deleted!": "Tono borrado correctamente.", "Tone successfully uploaded!": "Tono enviado correctamente al teclado.", "Renaming... Please wait!": "Renombrando… Espere.", "Deleting... Please wait!": "Borrando… Espere.", "Setting random main parameters and selecting 1–2 random DSP modules": "Generando parámetros y seleccionando uno o dos efectos DSP aleatorios",
    "7STR: 7-string compatible range": "7STR: rango para guitarra de 7 cuerdas", "FAT: Bold Wah sound tone": "FAT: wah de sonido grueso", "LIGHT: Light Wah sound tone": "LIGHT: wah de sonido ligero", "RESO: Enhanced resonance": "RESO: resonancia reforzada", "Overdrive": "Saturación", "LPF": "Filtro paso bajo", "Inf:1": "Infinito:1",
    "Cal Sine": "Calibración senoidal", "Cal Sine 2": "Calibración senoidal 2", "Cal Sine 3": "Calibración senoidal 3", "Cal Sine 4": "Calibración senoidal 4", "Cal Sine 5": "Calibración senoidal 5", "Cal 1kHz": "Calibración a 1 kHz", "Cal 1kHz 2": "Calibración a 1 kHz, variante", "Cal White Noise": "Calibración con ruido blanco", "Cal Pink Noise": "Calibración con ruido rosa", "Cal All Octave Sweep": "Barrido de todas las octavas", "Cal Multi-octave Sweep": "Barrido de varias octavas", "Cal Single Octave Sweep": "Barrido de una octava", "Cal Piano": "Piano de calibración", "Drum Kit ICH-NI-SAN": "Voz de calibración ICH-NI-SAN",
    "Amp": "Amplificador", "Amp Cabinet": "Amplificador y caja acústica", "Brake": "Freno", "Body Type": "Tipo de cuerpo", "Body Level": "Nivel del cuerpo", "Body Level L": "Nivel izquierdo del cuerpo", "Body Level R": "Nivel derecho del cuerpo", "Amb Type": "Tipo de ambiente", "Amb Level": "Nivel de ambiente",
    "EQ1 Frequency": "Frecuencia del ecualizador 1", "EQ2 Frequency": "Frecuencia del ecualizador 2", "EQ3 Frequency": "Frecuencia del ecualizador 3", "EQ1 Gain": "Ganancia del ecualizador 1", "EQ2 Gain": "Ganancia del ecualizador 2", "EQ3 Gain": "Ganancia del ecualizador 3",
    "Send the tone directly to the output or through the DSP effect.": "Envía el tono directamente a la salida o a través del efecto DSP.",
    "UPPER 1 Tone": "Tono de la capa superior 1", "UPPER 2 Tone": "Tono de la capa superior 2", "LOWER 1 Tone": "Tono de la capa inferior 1", "LOWER 2 Tone": "Tono de la capa inferior 2",
    "UPPER 1 Volume": "Volumen de la capa superior 1", "UPPER 2 Volume": "Volumen de la capa superior 2", "LOWER 1 Volume": "Volumen de la capa inferior 1", "LOWER 2 Volume": "Volumen de la capa inferior 2",
    "UPPER 1 Pan": "Panorámica de la capa superior 1", "UPPER 2 Pan": "Panorámica de la capa superior 2", "LOWER 1 Pan": "Panorámica de la capa inferior 1", "LOWER 2 Pan": "Panorámica de la capa inferior 2",
    "Saving... Please wait!": "Guardando… Espere.", "Select a parent tone to proceed": "Seleccione un tono base para continuar", "Unable to open MIDI port. Please check the MIDI settings.": "No se pudo abrir el puerto MIDI. Revise la configuración.",
    "&File": "&Archivo", "&Synthesizer Tools": "&Herramientas del teclado", "&Help": "A&yuda", "&Actions": "Accio&nes",
    "Settings": "Configuración", "Open settings": "Abrir la configuración", "Exit": "Salir", "Exit application": "Salir de la aplicación",
    "Open Tone (JSON)": "Abrir tono (JSON)", "Save Tone (JSON)": "Guardar tono (JSON)", "Save Tone (TON)": "Exportar tono (TON)",
    "Open JSON File": "Abrir archivo JSON", "Save JSON File": "Guardar archivo JSON", "Save TON File": "Exportar archivo TON",
    "JSON Files (*.json);;All Files (*)": "Archivos JSON (*.json);;Todos los archivos (*)",
    "TON Files (*.ton);;All Files (*)": "Archivos TON (*.ton);;Todos los archivos (*)",
    "Read tone information from a JSON-formatted file": "Leer los ajustes de un archivo JSON",
    "Save tone information as a JSON-formatted file": "Guardar los ajustes del tono en un archivo JSON",
    "Save tone as a TON file": "Exportar el tono como archivo TON",
    "Save Tone to Synthesizer's Memory": "Guardar tono en la memoria del teclado",
    "Save current tone to the synthesizer's user memory section (801–900)": "Guardar el tono actual en una memoria de usuario (801–900)",
    "Rename Tone": "Renombrar tono", "Delete Tone": "Borrar tono", "User Tone Manager": "Gestor de tonos de usuario",
    "Rename user tone (801–900)": "Renombrar un tono de usuario (801–900)", "Delete user tone (801–900)": "Borrar un tono de usuario (801–900)",
    "User Tone Manager allows you to save, rename, delete, and move tones within the synthesizer's user tone memory.": "Permite guardar, renombrar, borrar y mover tonos en la memoria de usuario del teclado.",
    "Request Parameter": "Consultar parámetro", "Request a parameter from synthesizer": "Consultar un parámetro del teclado",
    "Saving a TON File Using Synthesizer": "Cómo guardar un archivo TON desde el teclado",
    "Instructions on how to use the synthesizer to save and export the tone": "Instrucciones para guardar y exportar tonos",
    "Select Calibration Tone": "Seleccionar tono de calibración", "Toolbar": "Barra de herramientas",
    "Refresh": "Sincronizar", "Generate Tone": "Generar tono", "Random Name": "Nombre aleatorio",
    "Generate random tone name": "Generar un nombre de tono aleatorio", "Random Parent Tone": "Tono base aleatorio",
    "When selected, the parent tone is randomly chosen before tone generation": "Elegir un tono base aleatorio antes de generar el sonido",
    "Synchronize params from the synthesizer to the computer": "Leer los parámetros actuales del teclado",
    "Generate Random Tone: set random main parameters and select 1–2 random DSP modules": "Generar valores aleatorios y seleccionar uno o dos efectos DSP",
    "Layer Mixer": "Mezclador de capas", "Right Dock": "Panel de información", "Info / Help": "Información y ayuda", "Log": "Registro",
    "Main Params": "Principales", "Advanced Params": "Avanzados", "Ready": "Listo", "Experimental": "Experimental",
    "Latest status message": "Último mensaje de estado", "F8 opens the latest message. Escape returns to the editor.": "F8 permite leer el último mensaje. Escape vuelve al control anterior.",
    "Parameter information and help": "Información y ayuda de los parámetros", "MIDI message log": "Registro de mensajes MIDI",
    "Tone JSON": "Tono en formato JSON", "Parent tone": "Tono base", "Parent Tone:": "Tono base:", "Current tone name": "Nombre del tono actual",
    "Up to 8 characters.": "Hasta 8 caracteres.", "Custom MIDI message": "Mensaje MIDI personalizado", "MIDI message...": "Mensaje MIDI…",
    "Hexadecimal bytes. Tab moves to Send MIDI Message.": "Bytes hexadecimales. Tab lleva al botón Enviar mensaje MIDI.",
    "Send MIDI Message": "Enviar mensaje MIDI", "Randomize Parameters": "Aleatorizar parámetros", "Randomize DSP Values": "Aleatorizar valores del efecto",
    "{} Range {} to {}. Type a value or use Up and Down.": "{} Rango de {} a {}. Escriba un valor o use las flechas arriba y abajo.",
    " dial": " dial", "DSP {} effect": "Efecto DSP {}", "Parameters for ": "Parámetros de ", " module": " módulo",
    "Advanced parameters for editing tone": "Parámetros avanzados del tono", "Tone information in JSON-format": "Información del tono en formato JSON",
    "The DSP module is not selected.": "No hay un efecto DSP seleccionado.",
    "It may be necessary to adjust the volume level and octave shift after setting random values.": "Tras aleatorizar puede ser necesario ajustar el volumen y la octava.",
    "It might be necessary to adjust the volume levels after setting random values.": "Tras aleatorizar puede ser necesario ajustar el volumen.",
    "Synthesizer Model:": "Modelo de teclado:", "MIDI Input Port:": "Puerto MIDI de entrada:", "MIDI Output Port:": "Puerto MIDI de salida:", "Expert Mode:": "Modo experto:",
    "Synthesizer Model": "Modelo de teclado", "MIDI Input Port": "Puerto MIDI de entrada", "MIDI Output Port": "Puerto MIDI de salida", "Expert Mode": "Modo experto",
    "OK": "Aceptar", "CANCEL": "Cancelar", "SAVE": "Guardar", "RENAME": "Renombrar", "DELETE": "Borrar", "Clear": "Limpiar",
    "Restart Required": "Es necesario reiniciar", "Changes to Expert Mode will take effect after restarting the application.": "Los cambios del modo experto se aplicarán al reiniciar la aplicación.",
    "Unable to open MIDI port: ": "No se pudo abrir el puerto MIDI: ", "Input Error": "Valor incorrecto",
    "The 'Tone Number' field must contain a valid integer.": "El número de tono debe ser un entero válido.",
    "The 'Tone Number' must be in the range of 801 to 900.": "El número de tono debe estar entre 801 y 900.",
    "All fields must contain valid integers.": "Todos los campos deben contener números enteros válidos.",
    "Delete a tone in memory": "Borrar un tono de la memoria", "Rename a tone in memory": "Renombrar un tono de la memoria",
    "Save a tone to the synth's memory": "Guardar un tono en la memoria del teclado",
    "Tone Number:": "Número de tono:", "Tone Name:": "Nombre del tono:", "New Name:": "Nuevo nombre:",
    "Tone Number": "Número de tono", "Tone Name": "Nombre del tono", "New Tone Name": "Nuevo nombre del tono", "Tone Number to delete": "Número del tono que se borrará",
    "User Memory... (801-900)": "Memoria de usuario… (801–900)", "Tone Name... (8 symbols)": "Nombre del tono… (8 caracteres)", "New Name... (8 symbols)": "Nuevo nombre… (8 caracteres)",
    "User memory slot, 801 to 900.": "Posición de memoria de usuario: 801 a 900.", "User tone name": "Nombre del tono de usuario",
    "Parameter Number": "Número de parámetro", "Parameter Number...": "Número de parámetro…", "Number:": "Número:",
    "Block 0": "Bloque 0", "Block 0:": "Bloque 0:", "Block 0...": "Bloque 0…", "Category": "Categoría", "Category:": "Categoría:", "Category... (0-65)": "Categoría… (0–65)",
    "Memory Area ID": "Área de memoria", "Memory Area ID:": "Área de memoria:", "Memory... (0-4)": "Memoria… (0–4)",
    "Parameter Set": "Conjunto de parámetros", "Parameter Set:": "Conjunto de parámetros:", "Parameter Set...": "Conjunto de parámetros…",
    "Size": "Tamaño", "Size:": "Tamaño:", "Size...": "Tamaño…", "Get Parameter!": "Consultar parámetro",
    "Integer, {} to {}.": "Número entero de {} a {}.", "Check the value for ": "Revise el valor de ", "The result will appear in the 'Log' tab.": "La respuesta aparecerá en la pestaña Registro.",
    "PC Folder": "Carpeta del PC", "Upload": "Subir al teclado", "Download": "Descargar al PC", "Save Here": "Guardar aquí", "Rename": "Renombrar", "Delete": "Borrar",
    "Move Up": "Subir posición", "Move Down": "Bajar posición", "Upload Tone": "Subir tono al teclado", "Select Folder": "Seleccionar carpeta",
    "Destination user memory slot (801-900):": "Memoria de destino (801–900):", "File Name": "Nombre de archivo", "User Tone": "Tono de usuario",
    "PC User Data Files": "Archivos de tonos del PC", "Synthesizer's Internal Memory": "Memoria interna del teclado", "PC tone files": "Archivos de tonos del PC",
    "Synthesizer user memory": "Memoria de usuario del teclado", "Select a file, then Tab to Upload to copy it to the synthesizer.": "Seleccione un archivo. Use Tab para llegar a Subir al teclado.",
    "Select a tone. F2 or Enter renames it. Tab to Move Up, Move Down or Download.": "Seleccione un tono. F2 o Intro permite renombrarlo. Use Tab para moverlo o descargarlo.",
    "File successfully saved!": "Archivo guardado correctamente.", "No Data": "Sin datos",
    "Attack Time": "Tiempo de ataque", "Release Time": "Tiempo de liberación", "Cutoff Frequency": "Frecuencia de corte", "Resonance": "Resonancia",
    "Vibrato Type": "Forma del vibrato", "Vibrato Depth": "Profundidad del vibrato", "Vibrato Rate": "Velocidad del vibrato", "Vibrato Delay": "Retardo del vibrato",
    "Octave Shift": "Desplazamiento de octava", "Volume": "Volumen", "Velocity Sense": "Sensibilidad a la pulsación", "Reverb Send": "Envío a reverberación", "Chorus Send": "Envío a chorus", "Delay Send": "Envío a delay",
    "Sound A Timbre Type": "Tipo de timbre del sonido A", "Sound B Timbre Type": "Tipo de timbre del sonido B", "Sound A Wavetable": "Tabla de ondas del sonido A", "Sound B Wavetable": "Tabla de ondas del sonido B",
    "Monophonic Mode": "Modo monofónico", "Portamento Time": "Tiempo de portamento", "Velocity to Cutoff": "Pulsación sobre el filtro", "Sound B for Note-off": "Sonido B al soltar la tecla", "Note-off velocity": "Pulsación al soltar la tecla",
    "Sound B for Double-stop": "Sonido B al tocar dos notas", "Stretch Tuning": "Afinación extendida", "Output Route": "Ruta de salida",
    "Direct": "Directa", "Both": "Ambas", "Minimum of Both": "Mínimo de ambas", "Unknown": "Desconocido", "Note-off Velocity": "Al soltar la tecla", "Note-on Velocity": "Al pulsar la tecla",
    "UPPER 1": "SUPERIOR 1", "UPPER 2": "SUPERIOR 2", "LOWER 1": "INFERIOR 1", "LOWER 2": "INFERIOR 2", "Pan": "Panorámica", "Vol:": "Vol:", "Tone": "Tono",
    "Sine": "Senoidal", "Triangle": "Triangular", "Sawtooth": "Diente de sierra", "Square": "Cuadrada", "Trapezoid": "Trapezoidal", "Random": "Aleatoria",
    "OFF": "Desactivado", "ON": "Activado", "Off": "Desactivado", "Melody": "Melódico", "Drum": "Percusión", "Versatile": "Versátil",
    "Mono 1-Band EQ": "Ecualizador mono de 1 banda", "Mono 2-Band EQ": "Ecualizador mono de 2 bandas", "Mono 3-Band EQ": "Ecualizador mono de 3 bandas",
    "Stereo 1-Band EQ": "Ecualizador estéreo de 1 banda", "Stereo 2-Band EQ": "Ecualizador estéreo de 2 bandas", "Stereo 3-Band EQ": "Ecualizador estéreo de 3 bandas",
    "Tone Control": "Control de tono", "Compressor": "Compresor", "Limiter": "Limitador", "Enhancer": "Realce", "Reflection": "Reflexiones", "Tremolo": "Trémolo", "Auto Pan": "Panorámica automática",
    "Distortion": "Distorsión", "Pitch Shifter": "Transpositor", "Ring Modulator": "Modulador en anillo", "Rotary": "Altavoz giratorio", "Drive Rotary": "Altavoz giratorio con saturación",
    "Delay": "Retardo", "LFO Wah": "Wah por LFO", "Auto Wah": "Wah automático", "Modeling Wah": "Wah modelado", "Distortion-Wah": "Distorsión–wah", "Wah-Distortion": "Wah–distorsión",
    "Multi Chorus (hidden)": "Chorus múltiple (experimental)", "Piano Body (hidden)": "Cuerpo de piano (experimental)", "Hollow Body (hidden)": "Cuerpo hueco (experimental)", "Piano Effect": "Efecto de piano",
    "EQ Frequency": "Frecuencia del ecualizador", "EQ Gain": "Ganancia del ecualizador", "Input Level": "Nivel de entrada", "Wet Level": "Nivel del efecto", "Dry Level": "Nivel directo",
    "High Frequency": "Frecuencia de agudos", "High Gain": "Ganancia de agudos", "Low Frequency": "Frecuencia de graves", "Low Gain": "Ganancia de graves", "Mid Frequency": "Frecuencia de medios", "Mid Gain": "Ganancia de medios",
    "Gain": "Ganancia", "Type": "Tipo", "Level": "Nivel", "Attack": "Ataque", "Release": "Liberación", "Depth": "Profundidad", "Rate": "Velocidad", "Ratio": "Relación", "Limit": "Límite",
    "Feedback": "Realimentación", "Feedback Type": "Tipo de realimentación", "Feedback Level": "Nivel de realimentación", "Reflection Level": "Nivel de reflexiones", "High Damp": "Amortiguación de agudos",
    "LFO Rate": "Velocidad del LFO", "LFO Depth": "Profundidad del LFO", "LFO Waveform": "Forma de onda del LFO", "Polarity": "Polaridad", "Positive": "Positiva", "Negative": "Negativa",
    "Overdrive Gain": "Ganancia de saturación", "Overdrive Level": "Nivel de saturación", "Dist Gain": "Ganancia de distorsión", "Dist Level": "Nivel de distorsión", "Dist High": "Agudos de distorsión", "Dist Low": "Graves de distorsión",
    "Wah Type": "Tipo de wah", "Wah Manual": "Posición manual del wah", "Wah Depth": "Profundidad del wah", "Drive Type": "Tipo de saturación", "Drive": "Saturación", "Routing": "Enrutamiento",
    "Delay Time": "Tiempo de retardo", "Delay Tempo Sync": "Sincronización del retardo", "Delay Ratio L": "Relación izquierda del retardo", "Delay Ratio R": "Relación derecha del retardo", "Delay Level L": "Nivel izquierdo del retardo", "Delay Level R": "Nivel derecho del retardo",
    "OSC Frequency": "Frecuencia del oscilador", "Pitch": "Transposición", "Fine": "Ajuste fino", "Speed": "Velocidad", "Slow": "Lenta", "Fast": "Rápida", "Stop": "Detener", "Rotate": "Girar", "Slow Rate": "Velocidad lenta", "Fast Rate": "Velocidad rápida", "Rise Accel": "Aceleración", "Fall Accel": "Desaceleración",
    "Lid Type": "Apertura de la tapa", "Closed": "Cerrada", "SemiOpen": "Semiabierta", "Semi Open": "Semiabierta", "FullOpen": "Abierta", "Full Open": "Abierta", "Removed": "Sin tapa",
    "Clean": "Limpio", "Crunch": "Crujiente", "Distortion ": "Distorsión ", "Variation": "Variación", "Stereo": "Estéreo", "Cross": "Cruzada", "Thin body": "Cuerpo delgado", "Mid body": "Cuerpo medio", "Thick body": "Cuerpo grueso", "Acc bass": "Bajo acústico", "Roundback": "Fondo redondeado",
    "DSP Bypass": "Anular el procesamiento del efecto", "Bypass": "Anular efecto",
    "Adjusts the time after a key is pressed from when the note starts to sound until it reaches maximum volume. A larger value specifies a slower attack.": "Tiempo entre pulsar la tecla y alcanzar el volumen máximo. Un valor mayor produce un ataque más lento.",
    "Adjusts how long notes linger after keyboard keys are released. A larger values specifies a longer release.": "Duración de la nota después de soltar la tecla. Un valor mayor prolonga el sonido.",
    "Adjusts timbre by attenuating the components of a note’s frequency characteristics that are higher than a certain frequency (cutoff frequency). A larger value specifies a brighter, harder sound, while a lower value specifies a mellower, softer sound.": "Atenúa las frecuencias superiores al corte. Un valor mayor da un sonido más brillante; uno menor, más suave.",
    "Adjusts the gain of harmonic tones in the vicinity of the cutoff frequency specified above. A larger value creates a more unusual sound.": "Realza los armónicos cercanos a la frecuencia de corte. Un valor mayor acentúa la resonancia.",
    "Selects the vibrato waveform.": "Selecciona la forma de onda del vibrato.", "VSpecifies the depth of vibrato.": "Intensidad de la variación de afinación del vibrato.", "Adjusts the speed of vibrato.": "Velocidad de la variación de afinación del vibrato.", "Adjusts the time until vibrato starts after a note is sounded.": "Tiempo que tarda en comenzar el vibrato después de tocar una nota.",
    "Shifts the pitch upwards or downwards in octave steps.": "Transporta la afinación en pasos de una octava.", "Specifies the volume level of a tone. A larger value sets a higher volume level.": "Nivel de volumen del tono. Un valor mayor aumenta el volumen.",
    "VSpecifies how much the tone and/or volume should be affected by keyboard touch (pressure). A larger positive value specifies more brightness and greater volume as keyboard touch becomes stronger. A larger negative value specifies more softness and less volume as keyboard touch becomes stronger. A value of 0 specifies no change in accordance with keyboard touch.": "Respuesta del timbre y volumen a la fuerza de pulsación. Los valores positivos aumentan brillo y volumen al tocar más fuerte; los negativos invierten la respuesta. Cero elimina esta variación.",
    "Specifies how much reverb is applied to a tone.": "Cantidad del tono enviada a reverberación.", "Specifies how much chorus is applied to a tone.": "Cantidad del tono enviada al chorus.", "Specifies how much delay is applied to a tone.": "Cantidad del tono enviada al retardo.",
    "Portamento lets the sound slide smoothly from one note to the next instead of jumping.": "Desliza la afinación suavemente entre notas.",
    "Portamento time controls how long it takes to slide from one note to another. A shorter time makes the slide quick, while a longer time creates a slow, smooth glide.": "Duración del deslizamiento de afinación entre notas. Un valor mayor produce una transición más lenta.",
    "Controls how velocity affects the filter cutoff (certain wavetables only).": "Cómo afecta la pulsación a la frecuencia de corte. Depende de la tabla de ondas.",
    "Volume of the note.": "Volumen de la capa.", "Volume of the note. Only notes played on the keyboard are affected by this (not MIDI IN or rhythms).": "Volumen de las notas tocadas en el teclado. No afecta a la entrada MIDI ni al acompañamiento.",
    "Adjusts the input level.": "Ajusta el nivel de entrada.", "Adjusts the level of the direct sound.": "Ajusta el nivel de la señal sin efecto.", "Adjusts the level of the effect sound.": "Ajusta el nivel de la señal procesada.", "Adjusts the feedback amount.": "Ajusta la cantidad de realimentación.",
    "Adjusts the total delay time in 1 ms units.": "Duración total del retardo, en milisegundos.", "Adjusts the repeat of the reflected sound.": "Cantidad de repeticiones del sonido retardado.", "Adjusts the pan (stereo position).": "Posición de la señal entre los canales izquierdo y derecho.",
}


_FRAGMENTS = re.compile("|".join(
    (r"(?<!\w)" if source[0].isalnum() else "") + re.escape(source) +
    (r"(?!\w)" if source[-1].isalnum() else "")
    for source in sorted(STRINGS, key=len, reverse=True) if len(source) >= 3))


@lru_cache(maxsize=8192)
def tr(text):
    if text is None:
        return ""
    text = str(text)
    if text in STRINGS:
        return STRINGS[text]
    stripped = text.strip()
    if stripped in STRINGS:
        return text.replace(stripped, STRINGS[stripped], 1)
    # Translate fragments around dynamic names, numbers and HTML without touching stored data.
    return _FRAGMENTS.sub(lambda match: STRINGS[match.group()], text)


def parameter_help(parameter):
    description = (parameter.description or "").strip()
    if description in STRINGS:
        return tr(description)
    return "Ajuste de {}. Consulte los valores disponibles en este control.".format(tr(parameter.name).lower())


def install_qt_spanish(app):
    from PySide6.QtCore import QTranslator, QLibraryInfo, QLocale
    from utils.utils import resource_path
    QLocale.setDefault(QLocale("es_PE"))
    translator = QTranslator(app)
    paths = [resource_path("translations/qtbase_es.qm"),
             QLibraryInfo.path(QLibraryInfo.TranslationsPath) + "/qtbase_es.qm"]
    for path in paths:
        if translator.load(path):
            app.installTranslator(translator)
            app.spanish_translator = translator
            return True
    return False


def module_help(module):
    descriptions = {
        "Compressor": "Reduce las variaciones de nivel de la señal de entrada.",
        "Limiter": "Limita la señal para que no supere un nivel determinado.",
        "Enhancer": "Realza la definición de graves y agudos.",
        "Reflection": "Simula las reflexiones iniciales de un espacio acústico.",
        "Tremolo": "Modula periódicamente el volumen mediante un oscilador de baja frecuencia.",
        "Auto Pan": "Desplaza periódicamente la señal entre izquierda y derecha.",
        "Phaser": "Mezcla la señal original con una copia cuya fase varía periódicamente.",
        "Flanger": "Combina la señal con un retardo variable para crear un efecto de barrido.",
        "Chorus": "Añade profundidad y amplitud al sonido.",
        "Delay": "Repite la señal de entrada mediante un retardo con realimentación.",
        "Pitch Shifter": "Modifica la afinación de la señal de entrada.",
        "Ring Modulator": "Combina la entrada con un oscilador para crear un timbre metálico.",
        "Rotary": "Simula un altavoz giratorio.",
        "Drive Rotary": "Simula un altavoz giratorio con saturación.",
        "LFO Wah": "Modula la frecuencia del filtro wah con un oscilador de baja frecuencia.",
        "Auto Wah": "Modifica el filtro wah en respuesta al nivel de entrada.",
        "Modeling Wah": "Simula diferentes pedales wah.",
        "Distortion": "Simula la saturación y distorsión de un amplificador.",
        "Distortion-Wah": "Combina distorsión, wah y simulación de amplificador.",
        "Amp Simulator": "Simula un amplificador y su caja acústica.",
    }
    if module.name in descriptions:
        return descriptions[module.name]
    if "EQ" in module.name or module.name == "Tone Control":
        return "Permite ajustar la frecuencia y ganancia de las bandas del ecualizador."
    if "(hidden)" in module.name:
        return "Efecto heredado experimental. Su comportamiento y sus rangos requieren investigación en el CT-X800."
    return "Procesamiento de audio: {}. Los controles permiten ajustar sus parámetros.".format(tr(module.name))
