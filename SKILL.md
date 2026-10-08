---
name: guille-collado
description: >-
  Edita brutos con el acabado Guille Collado que Jan aprobó en Día 1: montaje
  oral, Anton/Sloop/Toledo, texto con brillo detrás del sujeto, pantallas crema
  angulares, transiciones de cámara y diseño sonoro. Usar con «estilo Guille»,
  «como el Día 1», «esta calidad en un toque» o al continuar ese formato.
  Adapta el lenguaje al nuevo guion y entrega MP4 revisado y fuentes editables.
---

# Guille Collado · preset aprobado de Jan

Jan aprobó el 21-09-2026 la **v12 del Día 1 salvo el CTA SKILL**, que prefiere
como en v11. La v13 restituye ese bloque. Después pidió afinar la primera
transición y sustituir el gallo de «Básicamente»: la v14 incorpora ambas
correcciones. Es la entrega más reciente; no implica una nueva aprobación del
usuario. No reinferir fuentes, música o reglas desde versiones rechazadas.
Es una reproducción aprobada para Jan, no el proyecto original de Guille.

## Una petición, producción completa

«Hazlo como el Día 1» + los archivos basta para empezar. Localiza el material,
reconstruye el guion si falta y continúa hasta render, revisión y corrección.
No pedir de nuevo fuentes, canción, formato ni aprobación de cada fase cuando
este preset resuelve esas decisiones. Una toma también sirve; no exigir cuatro.
Si el usuario pide solo análisis, limitarse a eso. El preset no autoriza publicar
ni gastar sin el presupuesto/autorización aplicables al nuevo encargo.

1. Leer [dirección aprobada](references/direccion.md) y [montaje y sonido](references/montaje-sonido.md).
2. Inventariar con `python3 scripts/project.py init --workspace RAIZ --name SLUG --input VIDEO`;
   repetir `--input` para más tomas. Este comando crea el proyecto y copia el kit;
   **no elige la interpretación ni genera automáticamente una película terminada**.
3. Transcribir cada toma, elegir performances por sentido, conformar audio/vídeo,
   limpiar eco y cerrar el reloj editorial. Ver [producción](references/produccion.md).
4. Dirigir cada frase con texto, acción, transición y sonido vinculados al mismo
   evento. Reutilizar [motion y transiciones](references/motion.md), `assets/preset.json`
   y `assets/runtime/GuilleKit.tsx`. Adaptar onsets y geometría al nuevo rodaje.
5. Renderizar una muestra difícil, corregirla y completar el vídeo. Aplicar lente
   final, mezclar y pasar `scripts/verify.py`. Revisar audiovisual completo,
   máscaras y lectura móvil; el verificador técnico no aprueba la estética.
6. Entregar MP4, SRT, composición, EDL, eventos, assets, costes y QA. Si pide
   abrirlo, abrir el archivo ya verificado. No declarar «idéntico» o «perfecto».

## Invariantes que evitaron regresiones

- **Anton** para titulares; **Sloop ScriptOne** para cursiva editorial;
  **Toledo-Serial BoldItalic** para subtítulos. Archivos locales exactos.
- Apilado por tinta visible y frase completa, con posiciones reservadas y
  onsets individuales. Glow amarillo visible; no sustituirlo por sombra sola.
- Titulares detrás de Jan con RGB/matte alineados. **SÍ O SÍ delante** si es el
  énfasis gigante equivalente. El **CTA mantiene su keyword** mientras aparecen
  apoyos inferiores en primer plano: es la excepción aprobada de SKILL.
- Música fuerte desde el inicio, acento musical en la bienvenida/promesa,
  continuidad sin reinicios extraños ni mute al mencionar «cambios de ritmo».
- Sonorizar entradas editoriales y acciones, con ataques suaves y jerarquía.
  Ningún golpe aislado en el segundo cero. BOOM grave y CLEAN con cola audible.
- Transiciones importantes parten del **último estado compuesto visible** y
  terminan en el siguiente plano. Voz entrante antes del final de la transición.
- Push-in suave sostenido sin sumar zooms redundantes. «Chico parado» en Día 1
  solo afecta al contenido de la tarjeta puente; no congela a Jan en otros planos.
- Quitar esperas visibles y microsilencios sin amputar respiración, consonantes,
  negaciones ni remates. Pausa narrativa sobre recurso activo cuando hace falta.

## Recursos y precedencia

`assets/preset.json` contiene valores de reproducción medidos del código aprobado,
no parámetros recuperados de Guille. `assets/manifest.json` identifica archivos,
hashes y procedencia. `assets/golden/` conserva la entrega y ejemplos aprobados;
`assets/recipe/` guarda el código específico Día 1 para estudiar mecanismos,
**no para ejecutar sus timestamps sobre nuevos brutos**.

Este perfil prevalece sobre `editor-jan/formats/guille-collado-v1.md`, v2 y los
tokens históricos cuando se pide el acabado aprobado de Jan. Otros formatos de
editor-jan, la marca Flow y otras referencias no heredan automáticamente estas
preferencias. Las instrucciones nuevas del usuario siempre mandan.

La copia pública no trae Sloop, Toledo, la canción ni los SFX (tienen licencia).
Si `project.py doctor` los marca, pedir al usuario sus archivos: fuentes en
`assets/fonts/`, su canción y sus SFX. No sustituir fuentes en silencio.

Actualizar esta carpeta viva antes de volver a generar el ZIP. El paquete es
una copia de ella, sin secretos ni dependencias de `/Users/janmoliner` en los
scripts operativos. Véase [procedencia y alcance](references/procedencia.md).
