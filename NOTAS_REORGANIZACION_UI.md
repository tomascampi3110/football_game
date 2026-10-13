# Reorganización de interfaz — Football Career

## Cambios
- Inicio reconstruido como una vista desplazable con jerarquía visual: retrato y datos principales, indicadores compactos, próximo partido y accesos directos.
- Se elimina la repetición de información que antes aparecía en varios bloques de texto.
- Se agrega selector de cuatro tratamientos visuales del retrato del perfil. Son variantes de color del retrato genérico del proyecto, no fotografías de jugadores reales ni camisetas ligadas a un club.
- Los duelos ya no reutilizan la misma fotografía para representar al jugador y al rival. Se presentan como tarjetas de datos diferenciadas con valoración y atributo relevante.
- Se aplica una base visual consistente a los botones que antes conservaban el estilo gris predeterminado de Kivy.
- Se compactan alturas y espacios principales de la pantalla de partido.

## Verificación
- `python -m compileall -q .`
- `python -m unittest discover -s tests -q`

Las pruebas automáticas cubren la lógica, no sustituyen una comprobación visual ejecutando Kivy en Windows o Android. El retrato elegido se guarda en `jugador.apariencia['retrato']` y se usa en la pantalla de carrera; no se añade una fotografía por futbolista de la plantilla, para no aumentar innecesariamente el tamaño de la aplicación.
