# Football Career — versión completa para VS Code

Esta carpeta contiene la versión integrada del proyecto, no el prototipo mínimo. Incluye la interfaz Kivy, los sistemas de carrera, módulos auxiliares, recursos gráficos, pruebas y configuración para Android.

## Recomendado en Windows

Usá **Python 3.12 de 64 bits** para este proyecto. Podés mantener Python 3.14 instalado; no hace falta desinstalarlo. Kivy 2.3.1 no está instalándose correctamente en tu Python 3.14 actual.

### 1. Abrir en VS Code

1. Extraé todo el ZIP.
2. En VS Code, elegí **Archivo → Abrir carpeta**.
3. Abrí la carpeta `football_game_v2` (la que contiene `main.py`, `carrera.py`, `temporada.py` y `assets`).

### 2. Verificar Python 3.12

Abrí **Terminal → Nueva terminal** y ejecutá:

```powershell
py -3.12 --version
```

Debería responder `Python 3.12.x`. Si dice que no encuentra esa versión, instalá Python 3.12 de 64 bits desde:
https://www.python.org/downloads/release/python-31210/

Durante la instalación, marcá `Add python.exe to PATH` si aparece.

### 3. Instalar Kivy

Desde la terminal, dentro de la carpeta del proyecto, ejecutá:

```powershell
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt
```

### 4. Ejecutar el juego

```powershell
py -3.12 main.py
```

La ventana del juego debería abrir el menú principal. Elegí **Nueva carrera**, ingresá el nombre y la posición del futbolista y empezá la carrera.

### 5. Probar la lógica sin abrir la interfaz

Las pruebas de los sistemas del juego no necesitan Kivy. Ejecutá:

```powershell
py -3.12 -m unittest discover -s tests -v
```

En esta versión, las 62 pruebas automatizadas de backend pasan en el entorno de preparación. La ventana Kivy debe probarse en el equipo local después de instalar `requirements.txt`.

## Controles básicos del juego

- **Nueva carrera:** crea un futbolista y una carrera.
- **Continuar carrera:** si tu equipo tiene un partido pendiente en la semana, abre primero la pantalla de partido interactivo. Si no jugás esa semana, procesa el resto de la semana.
- **Partido interactivo:** el reloj avanza en intervalos de 1, 5 o 10 minutos. Cada 10 minutos podés elegir pasar, encarar, rematar o presionar. Las decisiones se registran en el partido y pueden modificar tu rendimiento y el resultado. Al finalizar, se procesa el resto de los partidos y la economía semanal.
- **Perfil / Fútbol / Club / Relaciones / Economía / Inversiones / Patrocinadores:** permiten consultar y administrar los sistemas disponibles desde las pestañas.
- **Guardar:** guarda la carrera en `partida.career`.
- **Cargar partida:** intenta recuperar el guardado predeterminado.

Los nombres y opciones exactas que aparezcan dependen de la pantalla y del estado de la carrera.

## Si aparece un error

- `No module named kivy`: ejecutá la instalación con `py -3.12 -m pip install -r requirements.txt`.
- `No suitable window provider` u otro error gráfico: copiá el traceback completo de la terminal.
- Si VS Code ejecuta Python 3.14 al usar el botón de ejecución, preferí el comando `py -3.12 main.py` en la terminal o seleccioná el intérprete Python 3.12 desde **Python: Select Interpreter**.

## Android

Se conserva `buildozer.spec` y `.github/workflows/build-android.yml` para el flujo de compilación Android. Esta descarga es el código fuente del proyecto; no contiene un APK compilado.
