# Producción reproducible y comprobación

## Contrato del nuevo proyecto

`scripts/project.py init` crea inventario de archivos, carpetas, copia del preset,
runtime y acceso a assets del pack. No copia tomas pesadas: las registra por ruta
resuelta y hash. No pisa un proyecto existente. Un único vídeo ya editado requiere
decidir qué partes conservar; no tratar sus subtítulos quemados como capas editables.

Carpetas: 01-tomas,02-transcripciones,03-guion,04-direccion,05-assets,06-audio,
07-montaje,08-final,09-qa. `production.json` guarda fps, canvas, inputs, estado y
presupuesto. La invocación simple inicia trabajo autónomo; no significa un render
instantáneo ni garantiza calidad sin revisar las tomas.

1. Ingesta: ffprobe, orientación, HDR, fps, duración, audio, pistas. Normalizar
   a SDR/CFR30 y lienzo común sin aplastar la imagen; conservar originales.
2. Transcribir por toma y seleccionar unidades por continuidad semántica.
   `scripts/guille_conform.py` conforma una EDL elegida; no elige el mejor take.
   Su contrato se conserva en `references/montaje-limpio.md`.
3. Limpiar voz, medir y compensar cualquier latencia. Guardar A/B y stem real.
4. Cerrar cortes; alinear palabras al diálogo final. Elaborar un mapa de eventos
   con: frase, frame, plano, foco, texto, orden de capas, recurso, transición,
   acción/resultado, cue y tiempo de lectura. Cada evento sonoro referencia un
   evento gráfico o narrativo, no una estimación independiente del segundo.
5. Diseñar layout completo. `scripts/shape_text.py layout.json plan.json` da
   paths de glifos con kerning de frase y onsets por palabra. El diseño de
   posiciones sigue siendo una decisión editorial, no un algoritmo de gusto.
6. Generar únicamente recursos necesarios y autorizados. Registrar proveedor,
   modelo, prompt, keyframes, coste estimado/real, job_id y selección/descarte.
   No reenviar una generación tras timeout sin resolver el estado del job.
7. Componer con `assets/runtime/GuilleKit.tsx`, reutilizando escenas del ejemplo
   cuando encajen. Las recetas Día1 contienen clocks propios y no son un starter
   para ejecutar sin adaptar. Mantener un entrypoint aislado del proyecto.
8. Renderizar una muestra que incluya máscara, apilado, transición y sonido;
   corregir internamente y continuar. Exportar completo, aplicar
   `scripts/finish_lens.py flat.mp4 final.mp4 --edit edit.json --plan plan.json`.
9. Mezclar con `scripts/mix.py --voice VOZ_LIMPIA --song CANCION --events EVENTOS --asset-root ASSETS --outdir AUDIO --frames N --welcome SEG_PROMESA --source-beat SEG_ATAQUE`. Guarda stems y máster; medir el AAC final y revisar el MP4 completo.

## Qué se puede reutilizar directamente

- Fuentes, paleta/materiales y familia sonora identificadas por hash.
- Primitivas de capas, marcos, subtítulos, cámara y paths de texto.
- Shaping, conformado, acabado angular y verificación con argumentos explícitos.
- Recetas de interacción y timing **relativo a eventos**.

Qué se recalcula: selección de tomas, guion, onsets, duración, máscara de cada
frame, encaje a la cabeza, transiciones entre los nuevos planos, tempo narrativo,
offset/acento musical y mezcla de la voz. Nunca copiar la máscara de Jan ni los
frames2608/2630 de Día1 sobre un vídeo nuevo.

## Rendimiento sin cambiar el resultado

Cachear estados tipográficos idénticos; no recalcular filtros SVG costosos en
cada frame. Precomponer plano+texto×(1−matte), conservando escenas con animación
nativa. Día1 usó89 estados y1044 frames precompuestos; son cifras del caso.
La caché se invalida al cambiar texto, tiempo, posición, material o máscara.

No sobrescribir hardlinks de una versión anterior: unlink antes de reemplazar.
Assets compartidos solo de lectura. Bundles con `publicDir:null` y enlace al
public específico evitan duplicar gigabytes. Revisar espacio libre antes del
render; no borrar carpetas temporales globales de Remotion ni parar procesos
de otros proyectos. Usar temp y nombres de salida propios.

Lente final: mapas float precomputados, cv2 con1thread y cola ordenada de3workers
es el ejemplo aprobado. La paralelización no debe reordenar fotogramas. Comprobar
equivalencia visual después de optimizar (Día1: MAE0,198/255 en precomposición).

## Revisión que decide la entrega

Técnica: `python3 scripts/verify.py VIDEO --output 09-qa/archivo.json` decodifica,
mide loudness/true peak, duración AV y negro accidental. No certifica montaje.
El informe debe distinguir errores de archivo y observaciones para el editor.

Visual: frame0, entrada de cada frase, máxima oclusión, SÍ O SÍ frontal, CTA
completo, mano cerca de lente, llegada/salida de cada recurso, último frame.
Texto legible en móvil, sin reflujo ni cortes de acentos, glow sin quemar letra.
Pantallas legibles y seguras; el ejemplo de waveform no queda bajo la UI de IG.

Movimiento: velocidad normal y ralentizada de transiciones; revisar frames
adyacentes a la generación. Una hoja de contacto no prueba que un vuelo sea
fluido. Un analizador de baja frecuencia puede saltarse16frames y describirlos
como un zoom; contrastar el vídeo y la tira, no hacerle caso automáticamente.

Sonido: escuchar voz sola, empalmes y mezcla completa. Música desde inicio,
acento en promesa, sin reinicio ni mute accidental; pops/audios de acciones
alineados por ataque; BOOM y CLEAN con sus colas; ninguna palabra amputada.
La métrica de ruido o un resumen asistido no certifican que ya no se oye eco.

Entregar versión nueva sin pisar la aprobada. Registrar qué cambió, qué se
probó y cualquier limitación real. No generar una cadena de propuestas cuando
la tarea autoriza producir el vídeo completo.
