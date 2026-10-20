# Resultados del CT-X800: lecturas y pruebas automatizadas

Fecha: 19 de octubre de 2026. Instrumento identificado por el usuario como CT-X800.
Puertos detectados: CASIO USB-MIDI 0 (entrada) y CASIO USB-MIDI 1 (salida).
Los mensajes de prueba usaron IPR (acción 00), categoría 3, memoria 3 y conjunto 0.
No se enviaron escrituras IPS, cambios de programa ni notas durante estas capturas.

## Evidencia del instrumento

- 166 consultas transmitidas y 163 respuestas coincidentes.
- Primera captura: 40 consultas contestadas, con parámetros de la interfaz, Line Select y datos DSP.
- Exploración posterior: respondieron 123 direcciones, de 0 a 122, bloque 0. No respondieron 200, 201 ni 202 dentro de 0,3 segundos por consulta.
- Las direcciones exploradas proceden del lector TON original. No son descubrimientos nuevos del protocolo.
- Line Select (44) devolvió 1. Está documentado por Casio; tras esta captura se incorporó como Ruta de salida en Avanzados.
- Los parámetros 100, 101 y 106 devolvieron cinco bytes de datos. Su significado y rango no se han confirmado.
- DSP 1 devolvió ID 1; DSP 2, 3 y 4 devolvieron 7F 7F. Consultar esas ranuras no demuestra cuatro efectos utilizables simultáneamente.

Una respuesta acredita lectura de esa dirección con esta configuración. No prueba que admita escritura, que su función sea audible ni cuáles son sus extremos válidos. La ausencia de respuesta tampoco prueba inexistencia del parámetro.

## Correcciones verificadas en software

1. Ataque/liberación: el decodificador podía devolver -1 o volver a 0 para datos fuera de su tabla. Ahora limita el resultado a los extremos 0 y 127.
2. MIDI entrante: mensajes vacíos o truncados provocaban IndexError; ecos de solicitudes y otros modelos podían interpretarse como valores. Ahora se comprueban cabecera, acción, tamaño y categoría antes de actualizar controles.
3. Archivos TON: se leían en orden incorrecto los campos de cabecera y no se verificaba el CRC. Ahora se verifican tamaño y checksum antes de aceptar el archivo.
4. Empaquetado de datos vacíos: generaba un byte extra. Corregido y contrastado con un codificador independiente.
5. Mensajes MIDI de tiempo real intercalados: invalidaban una trama SysEx parcial en el lector TON. Ahora se conservan los datos de esa trama.
6. Delay: concatenar texto perdía ceros, por ejemplo 100 se convertía en 10. Se comprobó ida y vuelta de 1 a 1099 contra el formato existente, sin escribir esos valores en el instrumento.
7. Índice y longitud de arrays: el constructor TON usaba pares de 8 bits; a partir de 128 generaba bytes incompatibles con el formato de 7 bits. Corregido.
8. Límites de modelo: Octave Shift usa -2 a +2 y Note-off Velocity tres opciones en CT-X700/800, conservando los valores MIDI centrales correctos. Otros modelos conservan sus opciones anteriores.

Las dos últimas restricciones de modelo se contrastaron con las tablas de parámetros del [manual MIDI oficial de Casio, páginas 27–28](https://www.casio.com/content/dam/casio/global/support/manuals/electronic-musical-instruments/pdf/008-en/c/CT-X800-midi-imple_EN.pdf). No se ensayaron los límites mediante escrituras al teclado.

## Pruebas reproducibles

La etapa de diagnóstico pasó 35 pruebas, incluidas las 19 iniciales de accesibilidad. La ampliación posterior en español y con Experimental se documenta en ACCESIBILIDAD.md.
La suite comprueba 24335 valores de los descriptores, todos los 16384 enteros representables en dos bytes de 7 bits, otros 16384 valores de entrada del decodificador de ataque/liberación, 1099 valores de delay y más de 4000 mensajes incompletos o aleatorios. Estos son casos de software, no un barrido de valores escrito en el hardware.
También se reproducen las capturas mediante MidiService y Core, con una ventana Qt real y dispositivos sustituidos. Los valores de los controles quedan dentro de sus opciones/rangos y esa reproducción no genera escrituras de parámetros.

```powershell
.\.runtime\python310\python.exe -m unittest discover -s tests -v
```

Las capturas originales están en `captures/ctx800-readonly-20261019.json` y `captures/ctx800-survey-20261019.json`. Contienen paquetes transmitidos, recibidos y resultados por consulta. Este informe se regenera con `tools/analyze_ctx800_capture.py` sin conectar el teclado.

## Pendientes para investigar funciones y rangos

- Asociar direcciones sin control visible con cambios manuales de un único ajuste del teclado y comparar capturas antes/después.
- Confirmar el significado de Line Select en el sonido actual antes de exponerlo como un control nuevo.
- Contrastar la tabla especial de ataque/liberación con ajustes manuales conocidos: la ida/vuelta de su código no demuestra que la escala coincida con la del CT-X800.
- Probar cambios de un parámetro documentado y restaurar su valor inicial; guardar ambas lecturas y la observación auditiva.
- Comprobar NVDA con la aplicación real. Los tests de propiedades Qt no sustituyen escuchar el lector de pantalla.

## Inventario bruto de la exploración

Los nombres solo identifican controles ya existentes. No se atribuyen funciones a los valores restantes.

| ID decimal | Control existente, si coincide en bloque 0 | Bytes | Datos hexadecimales |
| --- | --- | --- | --- |
| 0 | Tone name | 16 | 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 |
| 1 | Sound A Timbre Type | 1 | 04 |
| 2 | Sound A Wavetable | 2 | 00 00 |
| 3 | Sin control identificado | 1 | 7F |
| 4 | Velocity to Cutoff | 1 | 7F |
| 5 | Velocity Sense | 1 | 7F |
| 6 | Sin control identificado | 2 | 00 01 |
| 7 | Sin control identificado | 2 | 00 04 |
| 8 | Sin control identificado | 2 | 18 01 |
| 9 | Sin control identificado | 2 | 66 00 |
| 10 | Sin control identificado | 2 | 1A 01 |
| 11 | Sin control identificado | 2 | 00 04 |
| 12 | Sin control identificado | 2 | 00 01 |
| 13 | Sin control identificado | 2 | 00 04 |
| 14 | Cutoff Frequency | 2 | 00 01 |
| 15 | Resonance | 2 | 00 01 |
| 16 | Sin control identificado | 1 | 7F |
| 17 | Sin control identificado | 2 | 00 01 |
| 18 | Sin control identificado | 2 | 00 04 |
| 19 | Sin control identificado | 2 | 68 00 |
| 20 | Sin control identificado | 2 | 00 04 |
| 21 | Sound B Timbre Type | 1 | 04 |
| 22 | Sound B Wavetable | 2 | 00 00 |
| 23 | Sin control identificado | 1 | 7F |
| 24 | Sin control identificado | 1 | 7F |
| 25 | Sin control identificado | 1 | 7F |
| 26 | Sin control identificado | 2 | 00 01 |
| 27 | Sin control identificado | 2 | 00 04 |
| 28 | Sin control identificado | 2 | 00 01 |
| 29 | Sin control identificado | 2 | 00 01 |
| 30 | Sin control identificado | 2 | 00 01 |
| 31 | Sin control identificado | 2 | 00 04 |
| 32 | Sin control identificado | 2 | 00 01 |
| 33 | Sin control identificado | 2 | 00 04 |
| 34 | Sin control identificado | 2 | 00 01 |
| 35 | Sin control identificado | 2 | 00 01 |
| 36 | Sin control identificado | 1 | 7F |
| 37 | Sin control identificado | 2 | 00 01 |
| 38 | Sin control identificado | 2 | 00 04 |
| 39 | Sin control identificado | 2 | 00 01 |
| 40 | Sin control identificado | 2 | 00 04 |
| 41 | Sound B for Note-off | 1 | 00 |
| 42 | Note-off velocity | 1 | 00 |
| 43 | Octave Shift | 1 | 04 |
| 44 | Output Route | 1 | 01 |
| 45 | Volume | 1 | 5A |
| 46 | Sin control identificado | 1 | 7F |
| 47 | Sin control identificado | 1 | 02 |
| 48 | Sin control identificado | 1 | 02 |
| 49 | Sin control identificado | 1 | 69 |
| 50 | Sin control identificado | 1 | 24 |
| 51 | Sin control identificado | 1 | 02 |
| 52 | Sin control identificado | 1 | 7F |
| 53 | Sin control identificado | 1 | 02 |
| 54 | Sin control identificado | 1 | 7F |
| 55 | Sin control identificado | 1 | 01 |
| 56 | Chorus Send | 1 | 00 |
| 57 | Reverb Send | 1 | 1E |
| 58 | Delay Send | 1 | 00 |
| 59 | Vibrato Type | 1 | 0F |
| 60 | Vibrato Rate | 1 | 40 |
| 61 | Vibrato Delay | 1 | 40 |
| 62 | Sin control identificado | 1 | 40 |
| 63 | Vibrato Depth | 1 | 40 |
| 64 | Sin control identificado | 1 | 48 |
| 65 | Sin control identificado | 1 | 48 |
| 66 | Sin control identificado | 1 | 0F |
| 67 | Sin control identificado | 1 | 40 |
| 68 | Sin control identificado | 1 | 40 |
| 69 | Sin control identificado | 1 | 40 |
| 70 | Sin control identificado | 1 | 40 |
| 71 | Sin control identificado | 1 | 40 |
| 72 | Sin control identificado | 1 | 40 |
| 73 | Sin control identificado | 1 | 40 |
| 74 | Sin control identificado | 1 | 40 |
| 75 | Sin control identificado | 1 | 40 |
| 76 | Sin control identificado | 1 | 40 |
| 77 | Sin control identificado | 1 | 40 |
| 78 | Sin control identificado | 1 | 00 |
| 79 | Sin control identificado | 1 | 00 |
| 80 | Stretch Tuning | 1 | 01 |
| 81 | Sin control identificado | 1 | 00 |
| 82 | Sin control identificado | 1 | 01 |
| 83 | Sin control identificado | 1 | 01 |
| 84 | Sin control identificado | 16 | 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 |
| 85 | DSP module | 2 | 01 00 |
| 86 | DSP bypass | 1 | 00 |
| 87 | DSP data | 14 | 02 3E 10 40 13 43 7F 7F 00 00 00 00 00 00 |
| 88 | Sin control identificado | 1 | 01 |
| 89 | Sin control identificado | 1 | 01 |
| 90 | Sin control identificado | 1 | 00 |
| 91 | Sin control identificado | 1 | 00 |
| 92 | Sin control identificado | 1 | 03 |
| 93 | Sin control identificado | 1 | 64 |
| 94 | Sin control identificado | 1 | 02 |
| 95 | Sin control identificado | 1 | 01 |
| 96 | Sin control identificado | 1 | 00 |
| 97 | Sin control identificado | 1 | 64 |
| 98 | Sin control identificado | 1 | 7F |
| 99 | Sin control identificado | 1 | 01 |
| 100 | Sin control identificado | 5 | 00 00 00 00 00 |
| 101 | Sin control identificado | 5 | 00 00 00 00 00 |
| 102 | Sin control identificado | 2 | 00 00 |
| 103 | Sin control identificado | 1 | 01 |
| 104 | Sin control identificado | 1 | 00 |
| 105 | Sin control identificado | 1 | 00 |
| 106 | Sin control identificado | 5 | 00 00 00 00 00 |
| 107 | Portamento Time | 1 | 00 |
| 108 | Sin control identificado | 1 | 04 |
| 109 | Sin control identificado | 2 | 00 00 |
| 110 | Sin control identificado | 1 | 00 |
| 111 | Sin control identificado | 1 | 00 |
| 112 | Sin control identificado | 1 | 00 |
| 113 | Sin control identificado | 1 | 01 |
| 114 | Monophonic Mode | 1 | 00 |
| 115 | Sound B for Double-stop | 1 | 00 |
| 116 | Portamento | 1 | 00 |
| 117 | Sin control identificado | 1 | 06 |
| 118 | Sin control identificado | 1 | 00 |
| 119 | Sin control identificado | 1 | 0E |
| 120 | Sin control identificado | 1 | 00 |
| 121 | Sin control identificado | 1 | 01 |
| 122 | Sin control identificado | 1 | 00 |
| 200 | Sin control identificado | — | Sin respuesta en el plazo |
| 201 | Sin control identificado | — | Sin respuesta en el plazo |
| 202 | Sin control identificado | — | Sin respuesta en el plazo |
