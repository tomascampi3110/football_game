# Football Career — etapa de preparación para APK

## Incluido en esta versión

- Música de fondo original en `assets/music/football_career_theme.ogg`, con control de activar/desactivar desde menú, carrera y partido. La preferencia se guarda en `preferencias.json`.
- Pantalla inicial con identidad visual, retrato de portada, descripción y botones de nueva carrera/cargar partida/salir.
- Creación de carrera con selección visual de retrato y opciones para activar segunda división, Copa Libertadores y ligas adicionales.
- Tutorial de cuatro semanas sin partidos ni ofertas inmediatas para las carreras creadas desde la interfaz. Al cerrar la cuarta semana se genera la primera oferta.
- Ligas opcionales de Primera Nacional Argentina, Brasil Série A/B y una selección inicial de ligas europeas (Inglaterra, España, Italia, Alemania y Francia), además de sus divisiones secundarias disponibles en el catálogo.
- Opción de Copa Libertadores desde el comienzo, con fase de grupos.
- Vista de otras competiciones: tablas de ligas activas y estado/resultados de copas.
- Botón para simular la temporada completa de forma rápida.
- Calendario que identifica la competición de cada encuentro.
- Audio incluido en el paquete Android mediante `buildozer.spec`.

## Alcance de los datos

Los nombres de clubes y estadios se basan en entidades reales. El catálogo de competiciones y equipos es ampliable, pero no es todavía una base oficial exhaustiva de todos los clubes del mundo. Los jugadores de los equipos que se generan automáticamente son futbolistas ficticios con nombres plausibles y valoraciones calculadas; no deben confundirse con planteles reales actualizados. La exactitud de los entrenadores puede variar y necesita una pasada de actualización antes de publicar.

## Música

- Archivo recomendado: OGG Vorbis (`.ogg`), pequeño y apropiado para música en bucle.
- Botón `MÚSICA: ACTIVADA/DESACTIVADA` en el menú principal; también hay un control compacto en carrera y partido.
- El volumen de fondo está limitado al 20% para no tapar los avisos del juego.

## Pruebas

Ejecutar desde la carpeta `football_game_v2`:

```bash
python -m compileall -q .
python -m unittest discover -s tests -q
```

Kivy no se pudo ejecutar visualmente en este entorno; la validación visual final de los popups y el audio debe hacerse en Windows/Android.
