# Prototipo de rediseño visual

Esta versión introduce una primera pasada visual para el centro de partido:
- Fondo azul noche y paneles oscuros con acento verde.
- Marcador más jerárquico y disciplina separada.
- Secciones de alineaciones y cronología.
- Eventos de duelo con ambos jugadores, valoración y porcentaje estimado de éxito.
- Acciones breves: regatear, pasar, rematar, quitar, interceptar y contener.

El partido sigue siendo de situaciones y decisiones al estilo Football Superstar 2. No es un simulador 3D.

## Prueba
Ejecutar `python main.py`. El test automatizado de lógica se ejecuta con `python -m unittest discover -s tests -v`.

Nota: el entorno de construcción no dispone de Kivy, así que se validó sintaxis y lógica con las pruebas, pero no se hizo una prueba visual real en Android/Windows. Este es un primer prototipo de la interfaz; la sustitución del avatar geométrico por retratos ilustrados y el rediseño completo de todas las secciones quedan como siguientes pasos.
