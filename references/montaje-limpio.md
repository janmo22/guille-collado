# Cuatro interpretaciones del mismo guion → una interpretación continua

> Para la referencia SEO DMI39yWo1NK prevalece la [dirección aprobada](direccion.md): Sloop ScriptOne cotejada; Mr Dafoe y Great Vibes descartadas para ese reel. El angular afecta también a la persona. Las identificaciones contradictorias del corpus inferior son históricas.

Contrato confirmado por Jan el 16-09-2026: cuatro vídeos del MISMO guion,
con errores de lectura y repeticiones dentro de cada toma. Pueden tener ángulos
distintos; no son cuatro cámaras sincronizadas. Guion escrito útil, no obligatorio:
si solo llegan vídeos, reconstruirlo contrastando las cuatro transcripciones.

## 1. Inventario antes de cortar

Conservar originales. Registrar por archivo duración, fps/PTS, resolución,
rotación, HDR/SDR, pista de audio, clipping, ruido, enfoque y espacio libre para
rótulos. Crear copias normalizadas CFR, SDR Rec.709 cuando proceda, mismo lienzo
y origen de tiempos; **transcribir esas mismas copias**. No usar timestamps de un
proxy con offsets diferentes. WAV de ASR a 16 kHz; audio de montaje a 48 kHz.
No convertir HDR a SDR solo cambiando etiquetas ni estirar caras para igualar formato.

Transcribir cada toma con palabras y timestamps. Guardar todos los intentos,
incluidos errores. Corregir nombres/cifras escuchando: el guion ayuda a detectar
errores de ASR, no permite hacer pasar una palabra mal dicha por correcta.

## 2. Selección por sentido e interpretación

Dividir el guion en unidades con `id`, texto y propósito. Para cada unidad,
buscar **todos los intentos** en las cuatro tomas, incluido el segundo o tercero
dentro del mismo archivo. `align.py` puede sugerir coincidencias, pero su toma
de referencia es la de más palabras, NO la más correcta. No decide la selección.

Guardar `selects.md`: unidad, candidatos con toma/rango, texto realmente dicho,
defectos y ganador. Decidir en este orden:

1. Frase completa y significado correcto: conservar negaciones, cifras, nombres,
   condiciones y CTA. Un «no» perdido no se arregla cambiando el subtítulo.
2. Naturalidad y fuerza de la interpretación: intención, énfasis, respiración,
   mirada, gesto y remate. Penalizar lectura titubeante y autocorrecciones.
3. Calidad técnica: voz inteligible, sin clipping, foco y exposición utilizables.
4. Continuidad con las frases vecinas: energía, tono, postura y dirección de mirada.
5. Variedad de ángulo, solo después de lo anterior.

Ejemplo: A dice «te cuesta cincuenta... perdón, quince», B dice «te cuesta
quince euros» con seguridad. Elegir B completa; no conservar A por tener el
ángulo más vistoso. Tampoco elegir siempre la última repetición: comparar.

Preferir frases o cláusulas completas de una misma interpretación. Unir palabras
sueltas entre tomas es último recurso y exige escuchar el empalme. Si ninguna
toma contiene una frase correcta, registrar el hueco exacto; buscar una paráfrasis
completa que conserve el sentido. Si no existe, pedir solo esa regrabación y
continuar con lo demás. No sintetizar la voz ni inventar palabras.

## 3. Primero un montaje de diálogo

Construir `edl.json` con solo las selecciones. Cada clip utiliza **vídeo y audio
de la misma toma y rango**. No poner voz de A con labios de B porque el texto sea
parecido. Un b-roll puede cubrir una costura, pero no corrige una frase defectuosa.
Cambiar ángulo en una frontera de frase o gesto útil; mantener un tramo bueno
es preferible a rotar A/B/C/D por calendario.

Cortar fallos, falsos comienzos, comentarios de grabación y repeticiones no
intencionales ANTES de comprimir pausas. En los bordes, consultar onda y escuchar
con contexto. Los timestamps ASR no identifican el final exacto de consonantes.
Conservar respiraciones funcionales, ataques y colas; ajustar el hueco según
entonación, sin cortar todas las pausas a 80 ms. Los huecos medidos en las
referencias rondan 170–260 ms de mediana y varían con el beat.

Microfades de 3–8 ms pueden evitar clicks en una unión limpia, no reparar una
sílaba mutilada. Igualar timbre/ruido/nivel entre tomas con suavidad, sin puerta
que bombee ni reducción de ruido metálica. Mantener tono de sala si lo necesita.
J/L cuts solo con intención y sin mostrar labios desincronizados.

## 4. EDL y conformado reproducible

`scripts/guille_conform.py` valida estructura y genera timeline, palabras
remapeadas y, con `--render`, un montaje AV base más diálogo WAV. **No selecciona
la mejor actuación ni valida el contenido semántico**: esa labor es §2–3.
Las rutas son relativas al JSON. Intervalos de frames `[in_frame,out_frame)`.
`word_indices` son los índices cero-based del transcript de ESA toma.
Unidades largas pueden repartirse en clips consecutivos con el mismo `unit_id`.

```json
{
  "fps": 30,
  "takes": {
    "A": {"media": "../01-tomas/toma-A.mp4", "words": "../02-transcripciones/toma-A.words.json"},
    "B": {"media": "../01-tomas/toma-B.mp4", "words": "../02-transcripciones/toma-B.words.json"}
  },
  "script_units": [{"id": "u01", "text": "Claude edita este vídeo."}],
  "clips": [{
    "take": "B", "in_frame": 90, "out_frame": 150,
    "unit_ids": ["u01"], "word_indices": [12, 13, 14, 15],
    "reason": "Segundo intento completo, mirada a lente y remate limpio"
  }]
}
```

Ejemplo de forma, no rangos para reutilizar. Añadir las cuatro tomas reales y
las unidades reales del proyecto. No copiar estos tiempos.

```bash
python3 scripts/guille_conform.py \
  proyecto/03-beats/edl.json --outdir proyecto/03-beats/conform --render
```

El helper rechaza archivos ausentes, fps/lienzos incompatibles, falta de audio,
rangos fuera del vídeo, palabras cortadas o no declaradas, reutilización de
fotogramas y unidades omitidas/desordenadas. Incluye palabras que realmente
intersectan cada clip: no permite esconder un «perdón» en el JSON mientras sigue
sonando en el vídeo. Comparar además `master.words.json` con las unidades: cubrir
un ID no demuestra que se hayan dicho sus palabras correctamente.

Salidas: `timeline.json`, `master.words.json`, `montaje-base.mp4`, `dialogo.wav`.
El vídeo base ya tiene la imagen y la voz seleccionadas sincronizadas. Puede
usarse como base continua en Remotion, o utilizar los clips del timeline con sus
trims exactos. Nunca volver a aplicar el tiempo global del master a cada bruto.

`t_final = from_frame/fps + t_fuente - in_frame/fps`.
Después de CUALQUIER recorte, regenerar el mapa y los eventos dependientes.
No usar `silence_cut.py` con una única tabla para cuatro performances distintas.
`build_skeleton.py` y `assemble_segments.py` son rutas heredadas de audio común;
no son el ensamblador de estas cuatro interpretaciones.

## 5. Revisión del diálogo antes del diseño

Ver/escuchar completo el montaje base, sin música, para comprobar que se sostiene
como una explicación natural. Revisar cada empalme con al menos 0,5 s de contexto
a cada lado. Retranscribir el WAV final y comparar cobertura/orden, usando la
escucha para resolver discrepancias. El ASR puede reconstruir una palabra cortada:
coincidencia textual no demuestra una costura limpia.

Registrar en `qa-dialogo.md`: unidad ganadora, errores retirados, ausencia de
omisiones/cambios de sentido, costuras corregidas y cualquier frase pendiente.
Solo entonces fijar duración y pasar a gráficos, b-roll y sonido. Este gate es
revisión interna del editor, no una nueva aprobación de Jan.

## 6. Condiciones que mejoran los futuros brutos

No exigir rodaje perfecto. Para aumentar el margen: lente limpia, exposición y
balance de blancos estables, micrófono a distancia similar, algo de aire sobre
la cabeza, encuadres realmente distintos. Tras equivocarse: parar un instante,
respirar y repetir la frase completa. Mirar a lente al arrancar/rematar. Mantener
dos segundos útiles antes/después y, si encaja, un gesto de cierre. Son ayudas
de captura, no requisitos para aceptar el material.
