# Base de datos de Football Career — prueba de octubre de 2026

## Incluido en esta versión

- Los 20 clubes de la Liga Profesional Argentina, con planteles ampliados de 18 o más jugadores marcados como reales en el motor.
- Planteles ampliados para Boca Juniors, River Plate, Racing Club, Rosario Central y otros clubes argentinos.
- Planteles reales iniciales para clubes internacionales seleccionados: Flamengo, Palmeiras, São Paulo, Corinthians, Botafogo, Manchester City, Arsenal, Liverpool, Real Madrid, Barcelona, Atlético de Madrid, Inter, AC Milan, Juventus, Bayern Múnich, Borussia Dortmund y Paris Saint-Germain.
- Las ligas adicionales conservan sus clubes, estadios y entrenadores cargados desde `catalogo_futbol.py`.
- Las valoraciones son valores de balance de juego aproximados, no ratings oficiales ni estadísticas reales.

## Límites importantes

Esta es una base local de prueba, no una base oficial exhaustiva de todos los jugadores del mundo. Los clubes que todavía no tienen un plantel específico completo se rellenan con futbolistas generados por el juego para mantener partidos jugables. Esos jugadores se identifican internamente con `es_jugador_real = False` y no deben presentarse como futbolistas reales.

Los planteles cambian con los mercados de pases; revisar y actualizar la base antes de una publicación pública. Las páginas oficiales consultadas para validar algunos nombres incluyen:

- River Plate, plantel profesional masculino: https://www.riverplate.com/futbol/futbol-profesional/masculino/plantel
- Boca Juniors, fútbol masculino: https://www.bocajuniors.com.ar/futbol-masculino

## Tabla de ligas

La pantalla «Tablas de otras ligas» muestra las mismas columnas que la tabla local (POS, EQUIPO, PJ, G, E, P, GF, GC, DG, PTS). El nombre de cada equipo es un botón: al tocarlo abre el detalle del club, con entrenador, estadio, jugadores, valoraciones y estadísticas disponibles.
