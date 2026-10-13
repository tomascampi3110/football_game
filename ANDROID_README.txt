FOOTBALL CAREER - GENERAR APK DE PRUEBA

La APK todavía no está compilada dentro de este ZIP. El proyecto incluye un flujo de GitHub Actions para compilarla en Linux.

PASOS
1. En GitHub, creá o abrí el repositorio donde vas a guardar el proyecto.
2. Subí el CONTENIDO de esta carpeta football_game_v2 a la raíz del repositorio (incluida la carpeta oculta .github). No subas la carpeta football_game_v2 como una subcarpeta, porque GitHub no detectaría el workflow si queda anidado.
3. Entrá a la pestaña Actions y elegí “Generar APK Android”.
4. Tocá “Run workflow” y confirmá. También se ejecutará automáticamente cuando hagas push de cambios relevantes.
5. Esperá a que el proceso termine en verde. Si falla, abrí el trabajo “Compilar Football Career” y copiá el primer error real del log.
6. En la ejecución completada, descargá el artefacto “football-career-debug-apk”. Dentro está la APK debug para instalar en tu teléfono.
7. Pasá la APK al teléfono Android y autorizá la instalación desde esa fuente si el sistema lo pide.

NOTAS
- Esta es una APK de prueba (debug), no una publicación de Play Store.
- La primera compilación puede tardar bastante porque debe descargar Android SDK/NDK y dependencias.
- La compilación requiere acceso a Internet en GitHub Actions.
- Si ya tenés un repositorio con el proyecto, actualizá sus archivos con esta versión y ejecutá el workflow.
