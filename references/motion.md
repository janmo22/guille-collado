# Acciones, cámara y transiciones

## Último frame → primero siguiente

En transiciones protagonistas, extraer los dos estados que el espectador verá,
**incluida composición de tarjetas y reencuadre**. En «Genial» el último plano
era una cuadrícula: partir de un bruto individual provocaba un salto antes de
la transición. La corrección aprobada atravesó la tarjeta frontal y recorrió
la mesa hasta el siguiente plano de Jan.

Definir origen, destino, recorrido, dirección, duración y tramo de cobertura.
Una cámara que pasa por mesa/mano/objeto da continuidad espacial; un zoom+blur
2D arbitrario había resultado artificial. Comprobar identidad, manos, ropa,
luz, geometría del espacio y último frame. No insertar un asset solo porque
la generación haya terminado o porque haya consumido créditos.

Generación del caso: Seedance2.0Mini, start/end image,4s/720p/9:16/sin audio,
4créditos estimados por candidato. **Verificar catálogo/coste vivo antes de cada
nuevo encargo**, no fijar el proveedor como única opción. Usar el presupuesto
autorizado de la sesión; el límite200 y acumulado conservador73 eran del Día1, no una
autorización permanente. Registrar también intentos fallidos y descartados.

Prompt base adaptable:

> One continuous camera transition. Start exactly on the supplied final visible
> composition; travel [physical route with parallax] into the supplied next shot.
> Preserve subject identity, clothing, anatomy, room and light. Start moving
> immediately, crisp endpoints, natural motion blur only during travel. No new
> text, crossfade, morphing between people, particles or explosions.

Retimar la generación a la ventana real. El inicio v14 ocupa22frames a30fps,
fase0/.18/.72/1→0/.10/.86/1 con interpolación monótona. Corrige la antigua
ventana16frames del inicio v12/v13; no reutilizar esa receta como resultado
vigente. Son puntos del caso, no fórmula universal.
Conservar extremos reales y revisar continuidad con los frames adyacentes.
Si la transición sustituye `[a,b)`, extraer el estado final de `a−1` y el estado
de reentrada de `b` del montaje final. El primer frame del bruto entrante puede
ser anterior al que realmente se verá después del puente: esa diferencia causó
un salto de manos/postura en el inicio del Día1. Tampoco aplicar de nuevo lente
o zoom a una generación condicionada con frames que ya llevan esos efectos.
Un fundido entre extremos desplazados produce doble texto; comprobar también
los primeros y últimos dos frames, no solo que los extremos coincidan.
Si se reexportan frames RGB con FFmpeg, convertir explícitamente a la matriz
YUV del máster (en Día1, BT.709 limitado) y etiquetarla. Copiar solo los tags
después de una conversión BT.601 por defecto deja un salto de color al empalmar.
En v14 los dos extremos se insertan además desde el YUV decodificado del máster,
sin ida y vuelta por RGB; así se evita acumular redondeos de color en el empalme.
No ralentizar toda la voz ni extender el montaje para enseñar una transición.
La voz entrante empieza antes de que termine el movimiento (**J-cut**).

Combinar transiciones protagonistas con cortes limpios y movimientos breves
que acompañen gestos. El número depende de las frases. «Genial… ¿y ahora qué?»
funciona como bisagra; no convertir cada corte en un vuelo de cámara.

## Mano y plano puente

TRANSICIONES se revela al pronunciarlo y la mano lo oculta. En una revisión
el titular caducaba antes de su onset: validar intervalo y voz, no solo el texto.
El RGB de mano y su máscara vienen del mismo vídeo, mismos frames y velocidad.
Una palma que llena la pantalla requiere máscara de mano; el modelo selfie puede
devolver cero. Ocultar el cambio de set durante cobertura real, sin flash negro.

En el plano puente, tres tarjetas explican origen/puente/destino. **El chico en
la tarjeta destino está fijo** como pidió Jan; la tarjeta sí puede ampliarse.
Su imagen final coincide con el primer frame de la toma que llena pantalla.
En el último tramo, perspectiva/radio/marco/lente convergen hacia el plano real.
No exportar ese permiso local como «congelar todos los recursos».

## Cuatro archivos → Claude → resultado

Usar miniaturas de los cuatro brutos realmente recibidos. Secuencia completa:
archivos visibles → mano Mac abierta → agarra → arrastra conjunto → suelta →
adjuntos → cursor al botón → click enviar → estado enviado → respuesta
**«Aquí lo tienes.»** → tarjeta con muestra real del resultado.
El tramo de ~18s no debe quedarse parado esperando audio.

La cámara sigue la intención y se asienta: acerca al agarrar, acompaña el
trayecto, llega a la zona de envío. El angular y blur lateral afectan también
a Claude. No generar texto/UI dentro de Seedance: componerlo nativamente.
Conservar identidad de archivos y miniaturas al pasar entre estados.
El clip que Claude devuelve contiene edición real, no un vídeo bruto ni mock
genérico. Renderizar primero ese fragmento evita dependencia circular.

## Recetas semánticas del caso

| Frase/función | Representación reutilizable |
|---|---|
| «Como el creador que yo quiera» | Avatares incógnitos detrás de Jan; uno revela al elegido y brilla |
| «Cuatro posiciones» | Cuadrícula de los cuatro ángulos reales con etiquetas claras |
| «Efectos de sonido» | Demo visual del sonido + acento audible en zona segura |
| «Cambios de ritmo» | Acento visual y sonoro sin parar la canción |
| «Super clean» | Titular grande detrás, barrido de luz y destello con cola larga |
| «Le mandé todos sus vídeos» | Scroll de captura real en marco crema curvado |
| «Paquetizar» | Stickers música/texto/estilo/volumen entran en carpeta y se cierra |
| «Boom» | Palabra grande tras cabeza + golpe grave con ataque limpio |
| CTA y bucle | Keyword persistente, apoyos legibles; salida real completa de Jan y portada final |

Son analogías para representar el guion nuevo. No reutilizar Guille, Claude,
cuatro archivos o SKILL si el nuevo contenido habla de otra cosa.
