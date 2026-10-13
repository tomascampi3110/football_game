# Actualización de recursos visuales

- Se reemplazaron emojis de la pantalla de partido por iconos PNG locales dibujados para el proyecto.
- Se agregó `assets/ui/arco_zonas.png`, una ilustración de arco con red, arquero y nueve zonas; los botones transparentes se superponen sobre esa imagen durante penales y tiros libres.
- La cronología y la alineación usan etiquetas de texto (`[GOL]`, `[AS]`, `[TA]`, `[TR]`) para evitar glifos emoji ausentes en Android/Windows.
- Se eliminó `AvatarWidget` de la pantalla de personalización. Ahora se elige entre los retratos fotográficos del proyecto y la vista previa es la propia foto, no una cara geométrica.
- La creación de carrera ya no muestra selectores de pelo/piel que no alteraban el retrato fotográfico.

Nota: el cambio de peinado o tono de piel de una fotografía requiere retratos alternativos preparados para esas combinaciones. Esta versión no simula ese cambio con controles que no afectan a la imagen.
