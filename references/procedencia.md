# Evidencia y alcance del paquete

La fuente es el proyecto local `negocios/contenido/proyectos-video/2026-09-16-dia1-guille-collado`.
Referencias estudiadas: Instagram DMI39yWo1NK (SEO), DcRT6LtoWsB (recursos/motion)
y captura aportada por Jan para subtítulos. No se dispone de proyectos editables
originales de Guille ni se afirma haber recuperado cada parámetro/SFX exacto.

Jan aprobó la v12 con una excepción explícita: recuperar el texto de SKILL como
antes. Se restituye el CTA v11 en v13; el resto de v12 se considera aprobado.
Después Jan aprobó el conjunto v13 salvo dos detalles: primera transición y
gallo en «Básicamente». La entrega v14 rehace el puente con los extremos reales
del montaje y usa otra interpretación de Jan para esa palabra. Conserva
duración, música y resto de montaje. Es la corrección solicitada, todavía sin
una aprobación posterior del usuario; `golden/approval.json` distingue ambas.
Esto sustituye la incertidumbre histórica de v7–v11 para este preset concreto.
La aprobación no convierte en ley universal cada coordenada ni número de cues.

| Regla actual | Evidencia/decisión |
|---|---|
| Sloop editorial y Toledo subtítulo | Archivos descargados y aportados por Jan; sustituciones rechazadas |
| Brillo amarillo visible | Peticiones repetidas y aprobación final del material v12 |
| Texto detrás salvo énfasis/CTA | Corrección explícita; máscara y final revisados |
| Tarjeta con chico fijo | Respuesta explícita a aclaración; no afecta cámara global |
| Continuidad musical | Jan: «La música está clavada»; después pide no parar en cambios de ritmo |
| Sin SFX al segundo0 | Identificado por Jan como el sonido que molestaba |
| Más pops y CLEAN más largo | Correcciones posteriores incorporadas a v12 |
| Inicio/Genial IA | Genial parte de la cuadrícula visible; inicio v14 parte del estado compuesto89 y llega al112, sin repetir la lente |
| Micropausas |46frames adicionales eliminados en v12; los intervalos ASR son orientativos y deben contrastarse escuchando |
| Final bucle | Salida completa de Jan y regreso a portada |
| SKILL persistente | Petición posterior a aprobación v12; CTA restituido de v11 |
| Gallo de «Básicamente» | Intento anterior del brutoD, palabra entera, eco tratado, ajuste de duración conservando pitch y revisión en contexto |

El paquete distingue:

- `preset.json`: ajustes operativos del resultado aprobado.
- `golden/`: ejemplo audiovisual y contacto; referencia de calidad, no promesa
  de que cualquier rodaje pueda ser idéntico.
- `recipe/`: código/datos Día1 para consultar su implementación, con reloj de
  proyecto. No ejecutar ciegamente scripts históricos ni números de frame.
- `runtime/` y `scripts/`: piezas parametrizadas para nuevo material.
- `manifest.json`: origen, tamaño y SHA256 de assets; sin claves API.

Uso del paquete local de Jan. Copiar una skill a otra máquina no instala Python,
FFmpeg, Remotion ni conecta Higgsfield/transcripción. `project.py doctor` informa
qué falta; no crear una barrera por servicios que el encargo no necesita.
Para compartir fuera, aplicar la política de distribución del workspace: las
fuentes con licencia y música no se convierten en recursos redistribuibles por
estar dentro del pack privado. La copia pública (github.com/janmo22/guille-collado,
8-oct-2026, a petición de Jan) sale de `scripts/package.py --publico DIR`, que deja
fuera Sloop, Toledo, la canción, los SFX y la entrega v14 (lleva la canción).

Las revisiones del analizador audiovisual son auxiliares. La revisión técnica
del vídeo aprobado:1080×1920/30,84,933333s,2548frames,−14,16LUFS-I y−1,09dBTP,
audio/vídeo de igual duración, sin intervalos negros detectados.
