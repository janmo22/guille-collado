# Interpretación, ritmo y sonido

## Montaje oral

Inventariar/transcribir cada bruto de forma independiente. Son interpretaciones
con fallos y duraciones distintas; no sincronizar cuatro vídeos copiando la voz
de uno. Reconstruir el guion por sentido, escoger frases completas y conservar
voz y labios de la misma performance. Comparar negaciones, reinicios y últimas
consonantes: Whisper puede normalizar un fallo y ocultarlo.

Cerrar primero la edición de voz. Eliminar esperas visibles de Jan y microsilencios
que cortan una misma frase. Mantener respiración/énfasis que ayuden a entenderla.
No cortar cada hueco a80 ms ni perseguir un número de cortes/minuto. Si hace falta
tiempo de lectura, sostener una acción/recurso, no a Jan esperando el siguiente take.

EDL, palabras, gráficos y SFX usan un reloj explícito. Hay reloj de bruto,
conformado y entrega; registrar conversiones. Intervalos [from,to), a30fps si se
usa el preset. Tras recortar, trasladar **todos** los eventos y comprobar que
las pausas eliminadas no intersectan palabras. No silenciar `/s/` finales por
confiar ciegamente en el word-end del alineador. Fades3 ms solo en bordes de voz
de baja energía; no time-stretch de la locución para encajar un efecto.

## Eco, ruido y continuidad

Jan rechaza reverberación evidente. Escuchar cada toma sola y los empalmes antes
de música. La versión aprobada usó MelBand Roformer De-Reverb-Echo V2 sobre voz
real, con comprobación de desfase por correlación y compensación de muestras.
Los tramos «he entrenado la IA» y «simplemente colgándole mis cuatro brutos»
necesitaron atención extra; son ejemplos, no timestamps para el siguiente vídeo.

No confundir denoise, puerta o EQ con desreverberación. Un WPE demasiado seco
degradó timbre. Hacer A/B del fragmento real: inteligibilidad, sibilancia, cola
de sala y voz metálica. Conservar versión anterior; no encadenar pasadas neuronales
sin detectar una mejora. Nunca regenerar la voz de Jan para ocultar un mal empalme.

Ante un gallo o una palabra defectuosa, buscar primero otra interpretación real
en los brutos, incluso un intento descartado justo antes. Escuchar la palabra
completa y sus dos enlaces: los timestamps ASR pueden fusionar repeticiones.
En Día1 se sustituyó «Básicamente» por el intento anterior de Jan, se limpió
su eco y se ajustó duración sin cambiar pitch; la frase y la sincronía labial
se revisaron en contexto. No copiar esa duración a otras palabras ni recortar
una consonante para obedecer el alineador. Una reparación local debe conservar
la música aprobada y el reloj del montaje, con comparación de stems y máster.

Cadena posterior del ejemplo: highpass85 Hz, puerta suave (ratio1,6,
attack4ms/release95ms), compresión2:1 (attack12ms/release140ms), voz≈−16LUFS.
Son valores iniciales para su grabación, no normalización obligatoria de toda voz.

## Música aprobada

Para «como Día 1», reutilizar **Without Me instrumental** del asset local
identificado por hash. No volver a P.I.M.P., lo-fi genérico ni otra canción por
la descripción histórica del corpus. Si se pide otra canción/referencia,
adaptarla. La autorización de uso de este preset no implica publicar la música.

Arranque con energía; el golpe principal pertenece a la canción y cae en la
bienvenida/promesa. En Día 1: bienvenida6,3667 s, ataque fuente9,297625 s,
offset2,9309583 s. **Para otro guion recalcular el offset con su frase**, sin
pegar6,3667 en todos los vídeos. La música continúa debajo de la voz, sin corte
extraño en ~11 s y sin bajar a cero al decir «cambios de ritmo».

El original tenía ediciones musicales, pero Jan aprobó aquí una cama continua;
su aprobación manda sobre la antigua receta de mutes. El stems v10 contenía
una atenuación0,12 que v12 revierte: no reutilizar ese stem como si estuviera
limpio sin esa corrección. Para nueva pieza partir del instrumental sin mutes.

Ejemplo de ganancia antes del máster: RMS base−24dBFS; ×1,16 al inicio,
×1,88 en el acento de bienvenida, retorno a×0,94 después de0,75s. Entrada10ms
para evitar clic, cola80ms si el bucle lo permite. Ajustar escuchando voz/música.
No inferir percepción desde `volume=0.25` ni igualar RMS y LUFS.

## Ingeniería de SFX

La aprobación incluye entradas editoriales más presentes. Usar un ataque corto
por llegada audible de palabra/bloque, también en script, agrupando simultáneos.
Evitar una metralleta de pops superpuestos: eventos a<40ms comparten ataque.
El sonido debe sentirse unido al texto/gesto; no es una cuota de120 cues por vídeo.

| Acción | Archivo de referencia | Pico de partida / cola tras ataque |
|---|---|---|
| Keyword amarilla | pop-B.wav | −14,5dBFS /95ms |
| Apoyo/cursiva | click-soft-tap.mp3 | −17,5 /70ms |
| Agarrar/enviar | mouse-click.mp3 | −21 a−19 /70–140ms |
| Soltar/resultado | pop-clean.mp3 | −23 a−19 /90–180ms |
| Cámara | whoosh-soft.mp3 | −24 /160ms |
| Scroll/arrastre | whoosh-soft.mp3 | −29 /110–140ms |
| Tarjeta/sticker | card-flip.mp3 | −24 a−20 /120–220ms |
| BOOM | boom-deep + pop-clean | −11 +−18 /700ms +100ms |
| SUPER CLEAN | whoosh-soft + shimmer-glow | −21 +−19 /420ms +900ms |

Recortar el sonido alrededor de su **ataque perceptivo**, no alrededor del primer
sample del fichero. El ejemplo encuentra energía máxima en ventana4 ms y alinea
ese punto al evento. Ataque hasta8ms y fade de cola15ms, según archivo.
Whooshes limpios: highpass160 Hz, lowpass5200 Hz; los graves se reservan al BOOM.
Brillo CLEAN más largo **sin ralentizar ni bajar el pitch**. Ningún golpe/chime
aislado al segundo0: se eliminó expresamente; ahí manda la música.

Mostrar también la acción cuando se explica: la demo sonora se ve en zona
segura, cambios de ritmo tienen un acento visual sin cortar música, la mano
tapa TRANSICIONES. Un waveform decorativo no se presenta como medición del audio.

Guardar stems voz/música/SFX y cue sheet con evento, archivo, frame, ataque,
nivel y duración. Medir el AAC entregado: objetivo≈−14LUFS-I, TP≤−1dBTP;
dejar margen (limitador−1,5 antes de codificar). No perseguir un LRA fijo.
Comparar móviles/auriculares si están disponibles; revisión asistida complementa
la escucha, no certifica que cada efecto sea el original de Guille.
