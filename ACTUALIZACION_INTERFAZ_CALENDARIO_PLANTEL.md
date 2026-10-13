# Actualización: navegación, plantel, recursos y calendario

- Se unificó la navegación de Fútbol y Mi club en una única sección.
- Se agregó una franja persistente y más legible con dinero, XP y contrato.
- La alineación titular de cada equipo queda fijada durante el partido para evitar que los jugadores salten de titulares a suplentes al refrescar la pantalla.
- La cronología identifica el equipo de los jugadores amonestados y expulsados.
- Se restablecen el comentario del partido y el texto de situación al entrar a un nuevo encuentro, evitando que quede el gol/comentario anterior.
- El calendario muestra la competición de cada partido junto con su marcador y estado.
- Las mejoras de atributos usan tarjetas separadas, con nombre, nivel y costo claramente diferenciados.

Verificación realizada: `python -m compileall -q .` y `python -m unittest discover -s tests -q` (77 pruebas aprobadas).
