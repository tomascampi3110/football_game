# Actualización: decisiones contextuales, apariencia y apuestas

- Se quitó el indicador de energía de la pantalla de carrera; no se simula energía porque no forma parte de la lógica actual.
- La pantalla de creación permite elegir entre cuatro retratos existentes, corte de pelo, color de pelo y tono de piel. El perfil abre la personalización al tocar el retrato.
- El avatar vectorial de vista previa sí cambia con las opciones de pelo/piel/ojos; los retratos fotográficos siguen siendo imágenes independientes. Para que el retrato fotográfico cambie píxel por píxel con todas las combinaciones hace falta una biblioteca de variantes fotográficas coherentes, que no se incluye todavía en esta versión.
- Las ocasiones ofensivas se separan en gambeta, pase o remate. La gambeta ofrece dirección; el pase, tipo de entrega; el remate, zona del arco. Se muestran comentarios contextuales y existe una pequeña posibilidad de caño.
- Penales y tiros libres usan una cuadrícula dibujada como arco, con zonas seleccionables; córneres conservan la elección de zona de centro.
- La apuesta deportiva tiene mínimo de $1.000, queda pendiente y se liquida según el resultado real del encuentro al procesar la semana. Los demás juegos del casino mantienen su mínimo general de $100.
- Los nombres NPC nuevos se generan con nombres y apellidos, no con etiquetas tipo «Jugador 16-10».

## Verificación

`python -m compileall -q .` y `python -m unittest discover -s tests -q` completados correctamente (71 pruebas). No se ejecutó la interfaz Kivy en una sesión gráfica, por lo que la composición visual debe comprobarse en el equipo del usuario.
