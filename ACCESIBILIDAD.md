# Tone Mutant 1.4 en español: uso con NVDA y CT-X800

Versión local del 19 de octubre de 2026, basada en Tone Mutant 1.3.3.

## Ejecutar

En esta máquina abra `Iniciar Tone Mutant.cmd`. El entorno local está preparado
con Python 3.12.14, PySide6/Qt 6.10.3 y python-rtmidi 1.5.8.

Para otra máquina Windows 10/11 de 64 bits, extraiga el ZIP
`dist/ToneMutant-ES-Windows-x64.zip` y abra `ToneMutant-ES.exe`.
Mantenga `_internal` junto al ejecutable. El proyecto está ahora en su carpeta propia `Proyectos/Tone-Mutant`.
El paquete incluye el entorno,
la traducción de Qt, los recursos, las capturas, las licencias y el código fuente.
No necesita instalar Python para ejecutar esa versión.

Conecte el teclado por USB, entre en Configuración con Ctrl+, y elija el modelo
CT-X700/800 y los puertos reales del Casio. Confirme con Aceptar y pulse F5.
Los ajustes se guardan en `config.cfg` junto al ejecutable portátil.

## Navegación con teclado y NVDA

| Tecla | Acción |
| --- | --- |
| Tab / Mayús+Tab | Control siguiente / anterior |
| Flechas | Cambiar selección, pestaña o valor |
| Escribir número y pulsar Intro | Confirmar un parámetro numérico |
| F6 / Mayús+F6 | Cambiar entre mezclador, edición y ayuda/registro |
| F8 | Enfocar y seleccionar el último mensaje de estado |
| Escape desde el estado | Volver al control anterior |
| Escape en formularios auxiliares | Cerrar el formulario |
| Ctrl+, | Abrir Configuración |
| F5 | Leer los parámetros del teclado |
| Ctrl+S | Guardar el tono en JSON |
| Ctrl+O | Abrir un tono JSON |
| Ctrl+Mayús+S | Exportar TON; en CT-X800 es experimental |
| Alt | Acceder a menús |
| F2 o Intro en la tabla de memoria | Renombrar el tono seleccionado, en modelos con memoria de usuario |

Los números tienen nombres, descripciones y rangos accesibles en español.
Tab se detiene en el campo numérico equivalente a cada dial, evitando duplicar
la parada. Los valores escritos se confirman con Intro o al abandonar el campo.
Los campos, listas, tablas, botones, áreas de lectura y pestañas utilizan controles
nativos de Qt. Los mensajes se consultan con F8 o en Registro; no se añade un
sintetizador de voz propio ni anuncios automáticos específicos de NVDA.

## Controles incorporados y organización

- Principales: los 14 parámetros de tono originales, traducidos y etiquetados.
- Avanzados: pulsación al soltar la tecla, afinación extendida y la nueva
  **Ruta de salida**, con opciones Directa y DSP, parámetro 44.
- DSP: efectos habituales y sus parámetros en español. Los tres efectos
  heredados marcados como ocultos se seleccionan desde Experimental.
- Mezclador: tono, volumen y panorámica de las cuatro capas. Se conservan los
  nombres originales de los sonidos del Casio para identificarlos en el instrumento.
- JSON: vista de datos de solo lectura. Los identificadores internos siguen en
  inglés para conservar la compatibilidad de archivos.

El CT-X700/800 utiliza los límites documentados de octava -2 a +2 y las tres
opciones documentadas de pulsación al soltar. Otros modelos conservan sus opciones
anteriores. Cambiar de modelo actualiza los controles y sus límites.

## Experimental

La pestaña Experimental reúne tres subsecciones:

1. **Lecturas e instantáneas.** Tabla de 126 direcciones incluidas en el lector de
   tonos original. Las lecturas iniciales corresponden a la sesión del 19/10/2026;
   cada fila indica su origen. Seleccione una dirección con las flechas y use
   Consultar seleccionado para leer su valor actual. Si no responde en 1,5 segundos,
   se conserva la lectura anterior y se indica el resultado. La tabla no permite
   escribir valores en direcciones sin identificar.
2. **Controles en investigación.** Diez parámetros avanzados heredados cuya
   función, escala o aplicación en tiempo real requiere comprobación. La edición
   comienza desactivada y se habilita con una casilla identificada. También permite
   seleccionar los tres efectos DSP heredados ocultos, tras habilitar la edición.
3. **Preguntas pendientes.** Interpretación de datos de cinco bytes, escalas de
   ataque/liberación, funcionamiento de las ranuras DSP, tablas de ondas y las
   direcciones 200 a 202 sin respuesta inicial.

Guardar instantánea exporta las observaciones en un formato separado de los
archivos de tono. Comparar con instantánea muestra los parámetros cuyos datos
cambiaron. Un flujo útil consiste en consultar un parámetro, guardar la instantánea,
cambiar un único ajuste manualmente en el teclado, consultar de nuevo y comparar.
No se atribuye una función nueva a una dirección únicamente porque responda.

El menú Experimental también agrupa los tonos de calibración heredados y,
para el CT-X800, la exportación TON aún por validar. Los tonos de calibración
no se seleccionan automáticamente.

## Verificación

La suite actual pasa **52 pruebas automatizadas**: accesibilidad de controles,
traducción, identificadores estables de pestañas/JSON, límites por modelo,
protocolo MIDI, conversiones, integridad de archivos TON, consultas experimentales,
instantáneas y separación de la edición experimental. La captura real se reproduce
con Core, MidiService y una ventana Qt sin transmitir cambios de parámetros.

La etapa de diagnóstico realizó 166 consultas de lectura al CT-X800 y obtuvo
163 respuestas coincidentes. Se conservan los paquetes originales en `captures/`.
El [informe del diagnóstico](docs/RESULTADOS_CTX800.md) detalla los hallazgos.
Leer un valor no confirma sus límites, su escritura ni su efecto audible.

La interfaz se revisó visualmente con el motor nativo de Windows. El ejecutable
se comprueba mediante `--self-test archivo.json`, con dispositivos simulados,
recursos empaquetados y traducción de Qt cargada. La prueba de arranque no utiliza
el teclado. Falta comprobar auditivamente todos los flujos con NVDA y verificar
los cambios de sonido de los controles experimentales. La versión portátil no se
ha probado físicamente en un segundo equipo.

Para repetir las pruebas en esta copia:

```powershell
.\.runtime\python312\Scripts\python.exe -m unittest discover -s tests -v
.\.runtime\python312\Scripts\python.exe main.py --self-test .runtime/arranque.json
```

## Estabilidad al cambiar tonos

La versión 1.4 entrega los mensajes de RtMidi al hilo principal mediante señales
Qt antes de modificar la ventana. Un temporizador agrupa los cambios rápidos y
solicita una resincronización tras 350 ms sin un nuevo cambio. Los puertos activos
se conservan durante esa lectura. Al cerrar se detienen el temporizador y el
callback MIDI antes de liberar los dispositivos.

También se corrigió la selección vacía: un tono no encontrado en el catálogo
podía provocar reenvíos al teclado y resincronizaciones repetidas. Ahora se
actualiza la lista sin activar acciones de selección del usuario.

Una prueba simula 1.000 cambios desde otro hilo, comprueba que la actualización
ocurre en el hilo de la interfaz, que no se envían selecciones al teclado y que
solo se solicita una resincronización. No aparecen excepciones de los slots.
La prueba física del cierre reportado queda pendiente: el teclado estaba guardado
al finalizar esta versión. El programa deja registros en `registros/` para analizar
cualquier excepción o fallo nativo que vuelva a ocurrir.

## Código y compilación

`requirements-desktop.txt` conserva las dependencias del entorno comprobado.
`requirements-build.txt` añade PyInstaller. En un entorno Python 3.12 de Windows
con esas dependencias, `python tools/build_portable.py` construye el ejecutable,
copia fuentes y licencias, genera el ZIP y calcula su SHA-256. No necesita Git
para reconstruir desde la carpeta de fuentes incluida.

El catálogo `docs/control-catalog.json` incluye identificadores originales y
nombres/descripciones en español como referencia para una futura interfaz Java.
Android aún no se ha implementado. El núcleo actual depende de Qt y necesitará
separar el protocolo de la interfaz antes de adaptarlo.

[Repositorio original](https://github.com/Barsik-Barbosik/Tone-Mutant).
Licencia y atribuciones conservadas en LICENSE.md y en el paquete portátil.
