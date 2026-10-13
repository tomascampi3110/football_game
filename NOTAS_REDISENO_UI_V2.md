# Reorganización visual v2

Cambios aplicados en el código de interfaz:

- Navegación persistente lateral en la pantalla de carrera, con acceso a Inicio, Fútbol, Mi club, Relaciones y Economía.
- Eliminación de la barra inferior anterior en la pantalla de carrera para evitar dos sistemas de navegación compitiendo.
- Inicio con una zona de identidad del jugador más ancha y una jerarquía más clara para valoración, temporada, recursos, forma, energía y próximo partido.
- Partido organizado en tres zonas persistentes: alineaciones, evento/duelo y cronología; marcador y disciplina quedan arriba, controles debajo.
- Texto del duelo simplificado para no repetir nombre y valoración en tres lugares a la vez.
- Se mantienen las clases y funciones de simulación existentes; el cambio es de composición de interfaz.

## Verificación

- `python -m compileall -q .`: correcto.
- `python -m unittest discover -s tests -v`: 67 pruebas aprobadas.
- No se pudo ejecutar la ventana Kivy visualmente en este entorno. Hay que probar la distribución en el PC donde se usa el proyecto.
