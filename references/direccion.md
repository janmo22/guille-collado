# Dirección aprobada · lenguaje visual

## Tipografía y composición

Diseñar toda la frase antes de mostrar su primera palabra. HarfBuzz da kerning,
ligaduras y baseline; convertir glifos a paths y medir su tinta real permite
apoyar una línea sobre la siguiente. Las futuras palabras reservan su sitio:
no recentrar filas cuando entra otra palabra. Tildes y florituras cuentan.

Titular amarillo Anton, apoyo Anton blanco y enlaces breves en Sloop ScriptOne.
Toledo es exclusivamente el subtítulo. Great Vibes, Mr Dafoe, Georgia y DM Serif
no son alternativas válidas a esas dos cursivas en este preset. No aplicar
fake italic o fake bold a Toledo; usar el archivo BoldItalic suministrado.

El bloque tiene centro óptico común, blancos apretados y escala vinculada a la
cabeza. Pocas palabras como «Sí, entera» se acercan a ella; no dejarlas flotando
en el extremo superior. Los grandes énfasis pueden ocupar casi todo el ancho,
con la persona por delante cuando la lectura lo permite. La geometría del
guion nuevo se diseña, no se trasplantan coordenadas de un sujeto distinto.

La reproducción usa curvas suaves del bloque (arco 7–14 px y flare 0,018–0,055 a
1080p) antes del acabado de lente global. No escalar horizontalmente una script
hasta deformar la letra; el ajuste ordinario conserva sus proporciones.

## Material, brillo y sombra

Valores exactos de referencia en `assets/preset.json → typography.materials`:
amarillo #FBDD48; halo cercano σ4,8 / α0,92, exterior σ19 / α0,54;
sombra σ11 / α0,23 desplazada 5 px. Blanco #FFFFFC; halo σ3,8 / α0,90,
exterior σ9 / α0,48; sombra σ10 / α0,20 a 4 px.

La letra nítida va encima del halo; el amarillo conserva color y contraformas.
El glow sigue la silueta, no una caja ni una mancha rectangular. La script
blanca usa trazo adicional min(5,2 px, 0,04 × altura visible), aparte de su halo.
Los filtros SVG usan `colorInterpolationFilters='sRGB'` y margen exterior.
Renderizar a 1080p y comprobar también pequeño; escalar estos píxeles con canvas.

## Capas y oclusión

Orden: plano intacto → recursos que van detrás → titulares traseros → copia RGB
del mismo plano recortada por matte → excepciones frontales → subtítulos.
Todo comparte cámara/reencuadre. No basta poner `z-index` al texto para que
quede detrás de una persona integrada en el vídeo.

RGB y máscara son del **mismo frame** y reciben idéntica transformación. Las dos
imágenes del componente se posicionan `absolute; inset:0`: una imagen oculta
en el flujo normal desplazó la capa visible una altura entera en una revisión.
Validar pelo, hombros, dedos y bordes temporalmente. El modelo selfie puede
perder una palma muy cerca del objetivo: máscara específica de mano o retoque
temporal; no confiar solo en segmentación de persona. Las thresholds de piel
del ejemplo son para esa luz/piel, no universales.

Excepciones aprobadas:

- «SÍ O SÍ»: tres filas gigantes delante de Jan, sobre su plano real.
- CTA: «si comentas SKILL» permanece arriba, SKILL detrás del sujeto;
  «te la MANDO» y «y cómo INSTALARLA» aparecen abajo en primer plano. No
  sustituir toda la cabecera con cada apoyo. Copiar su persistencia, no su texto
  literal si la nueva llamada a la acción es otra. En Día 1 se restituye v11.
- Subtítulos delante para legibilidad. No convertirlos en titulares ocluidos.

## Subtítulos y zona segura

Toledo-Serial BoldItalic, 44 px a 1080×1920, #F8D850, line-height 1,08;
contorno negro 3,5 px pintado antes del relleno; sombra
`1px 5px 0 #100b06, 2px 7px 3px #000c, 0 2px 9px #0008`.
Frases breves por sintaxis, sin karaoke, solapes ni saltos verticales palabra
a palabra. En Día 1: centro Y1035 en persona, Y1440 en recursos, excepciones
Y1270 para reservar la demo sonora y Y1490 en un tramo. Márgenes X95.
Son puntos de partida: medir ancho, cara y UI real del destino. Si no cabe,
recomponer en dos líneas con intención; no desbordar `white-space:nowrap`.

## Angular y protagonismo

No es solo inclinar una captura: persona, escena, texto y UI comparten profundidad.
El final aprobado usa remapeo radial flotante, centro (0,5;0,49), fuerza 0,16,
zoom 1,025 en plano humano; fuerza 0,105 sin zoom extra en pantallas. Usar mapas
float y remuestreo cúbico: el displacement SVG de 8 bits escalonado se descartó.

Las pantallas suavizan laterales, preservando el 54 % central. La máscara lateral
crece con potencia1,65; blur σ7 px al asentarse y hasta13 px al entrar; α0,84–0,96.
No emborronar el contenido que debe leerse. Perspectiva suave, por ejemplo
2000 px / rotateY −5°→−1,5° / rotateX 2°, que llega y se asienta.

Push-in sostenido por unidad de cámara, típico1,012→1,067. Hook1,055→1,09;
CTA1→1,055. Mantener continuidad entre frases de la misma toma; no reiniciar
el zoom en cada palabra ni sumar varios efectos sin controlar la escala final.
Recalibrar con rodaje distinto; no ensanchar caras automáticamente.

## Recursos que se entienden

Vídeos y capturas sobre crema #eee9df, borde #faf6ec, radios38–55 px y sombra
suave. No mostrar etiqueta «Referencia Guille Collado». Usar material real
cuando se habla de sus vídeos y scroll real de su perfil cuando se explica
haberle enviado ejemplos. No inventar pruebas, posts ni interfaces con IA.

Los perfiles desconocidos aparecen detrás de Jan; uno revela el creador elegido,
crece y brilla, los otros pierden contraste. La carpeta sticker reúne música,
texto, estilo y volumen con trayectorias visibles y contacto sonorizado.
Mostrar el significado de la frase, no insertar decoraciones por palabra clave.
