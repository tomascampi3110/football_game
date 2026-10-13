__version__ = "0.1.0"

from kivy.app import App
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button as KivyButton
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.core.audio import SoundLoader
import json
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.clock import Clock
import random
import os

from carrera import Carrera
from temporada import Temporada
from guardado import GestorGuardado
from tienda import TiendaEquipamiento
from mejoras import MejoraCarrera
from economia import Inversion
from personalizacion import OPCIONES_APARIENCIA
from zonas_tabla import zona_tabla
from competiciones import Liga, CopaNacional, CopaClubes, Internacional

RUTA_GUARDADO = "partida.career"


class Button(KivyButton):
  """Botón global con estilo consistente para evitar los controles grises por defecto."""
  def __init__(self, **kwargs):
    kwargs.setdefault("background_normal", "")
    kwargs.setdefault("background_down", "")
    kwargs.setdefault("background_color", (0.105, 0.145, 0.19, 1))
    kwargs.setdefault("color", (0.93, 0.95, 0.98, 1))
    kwargs.setdefault("font_size", 13)
    super().__init__(**kwargs)
    self.bind(on_press=self._reproducir_click)

  def _reproducir_click(self, *_):
    try:
      app = App.get_running_app()
      if app is not None:
        app.reproducir_efecto("click")
    except Exception:
      # Los controles también se construyen durante el arranque.
      pass


class FondoLabel(Label):
  """Label con fondo coloreado para distinguir filas de la tabla."""
  def __init__(self, fondo=(0.12, 0.14, 0.18, 1), color_texto=(0.92, 0.94, 0.97, 1), **kwargs):
    super().__init__(color=color_texto, **kwargs)
    with self.canvas.before:
      self._color_fondo = Color(*fondo)
      self._rect_fondo = Rectangle(pos=self.pos, size=self.size)
    self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

  def _actualizar_fondo(self, *_):
    self._rect_fondo.pos = self.pos
    self._rect_fondo.size = self.size


class TarjetaPremium(BoxLayout):
  """Panel oscuro reutilizable para la nueva identidad visual."""
  def __init__(self, fondo=(0.075, 0.11, 0.16, 1), **kwargs):
    super().__init__(**kwargs)
    with self.canvas.before:
      Color(*fondo)
      self._panel = RoundedRectangle(pos=self.pos, size=self.size, radius=[14])
    self.bind(pos=self._actualizar_panel, size=self._actualizar_panel)

  def _actualizar_panel(self, *_):
    self._panel.pos = self.pos
    self._panel.size = self.size


class BotonPremium(Button):
  def __init__(self, **kwargs):
    kwargs.setdefault("background_normal", "")
    kwargs.setdefault("background_down", "")
    kwargs.setdefault("background_color", (0.20, 0.88, 0.43, 1))
    kwargs.setdefault("color", (0.035, 0.07, 0.09, 1))
    kwargs.setdefault("bold", True)
    kwargs.setdefault("font_size", 13)
    super().__init__(**kwargs)


class MenuPrincipal(Screen):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(orientation="vertical", padding=(42, 24), spacing=12)
    with layout.canvas.before:
      Color(0.025, 0.045, 0.075, 1)
      self._bg = Rectangle(pos=layout.pos, size=layout.size)
    layout.bind(pos=lambda w, v: setattr(self._bg, "pos", v), size=lambda w, v: setattr(self._bg, "size", v))
    layout.add_widget(Label(text="[b][color=ffc34d]FOOTBALL[/color] [color=ffffff]CAREER[/color][/b]", markup=True, font_size=34, size_hint_y=None, height=65))
    layout.add_widget(Label(text="TU HISTORIA. TU CLUB. TU LEGADO.", font_size=14, color=(0.48, 0.91, 0.70, 1), size_hint_y=None, height=28))
    layout.add_widget(Image(source="assets/jugador_portada.jpg", fit_mode="contain", size_hint_y=1))
    layout.add_widget(Label(text="Creá tu futbolista, ganate un lugar y construí tu carrera desde cero.", font_size=15, color=(0.80, 0.86, 0.93, 1), size_hint_y=None, height=44))
    for texto, accion in [("NUEVA CARRERA", self.nueva_carrera), ("CARGAR PARTIDA", self.cargar_partida)]:
      boton = BotonPremium(text=texto, size_hint_y=None, height=52, font_size=16)
      boton.bind(on_press=accion)
      layout.add_widget(boton)
    fila = BoxLayout(size_hint_y=None, height=46, spacing=8)
    self.boton_musica = Button(text="MÚSICA: ACTIVADA", font_size=11)
    self.boton_musica.bind(on_press=lambda *_: App.get_running_app().alternar_musica())
    fila.add_widget(self.boton_musica)
    self.boton_efectos = Button(text="EFECTOS: ACTIVADOS", font_size=11)
    self.boton_efectos.bind(on_press=lambda *_: App.get_running_app().alternar_efectos())
    fila.add_widget(self.boton_efectos)
    salir = Button(text="SALIR", font_size=11, size_hint_x=0.65)
    salir.bind(on_press=self.salir)
    fila.add_widget(salir)
    layout.add_widget(fila)
    audio = Button(text="CONFIGURAR VOLUMEN", size_hint_y=None, height=38, font_size=11)
    audio.bind(on_press=lambda *_: App.get_running_app().abrir_configuracion_audio())
    layout.add_widget(audio)
    self.add_widget(layout)

  def on_pre_enter(self, *_):
    app = App.get_running_app()
    self.boton_musica.text = "MÚSICA: ACTIVADA" if getattr(app, "musica_activa", True) else "MÚSICA: DESACTIVADA"
    self.boton_efectos.text = "EFECTOS: ACTIVADOS" if getattr(app, "efectos_activos", True) else "EFECTOS: DESACTIVADOS"

  def nueva_carrera(self, *_):
    App.get_running_app().mostrar_pantalla("crear")

  def cargar_partida(self, *_):
    app = App.get_running_app()
    try:
      estado = GestorGuardado.cargar(RUTA_GUARDADO)
      app.carrera = estado["carrera"]
      app.mostrar_carrera()
    except FileNotFoundError:
      app.mostrar_mensaje("No hay una partida guardada en la ruta predeterminada.")
    except Exception as error:
      app.mostrar_mensaje(f"No se pudo cargar la partida: {error}")

  def salir(self, *_):
    App.get_running_app().stop()


class CrearJugador(Screen):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(orientation="vertical", padding=30, spacing=12)
    layout.add_widget(Label(text="Crear futbolista", font_size=26))

    self.nombre = TextInput(hint_text="Nombre del jugador", multiline=False)
    self.posicion = Spinner(
      text="Delantero",
      values=("Arquero", "Defensor", "Mediocampista", "Delantero")
    )
    layout.add_widget(Label(text="Elegí el retrato inicial", size_hint_y=None, height=26))
    self.retrato_seleccionado = "Modelo 1"
    self.rutas_retrato = {
      "Modelo 1": "assets/players/retrato_1.png",
      "Modelo 2": "assets/players/retrato_2.png",
      "Modelo 3": "assets/players/retrato_3.png",
      "Modelo 4": "assets/players/retrato_4.png"
    }
    layout.add_widget(self.nombre)
    layout.add_widget(Label(
      text="Edad inicial: 18 años. Mejorá tus atributos usando puntos de mejora.",
      size_hint_y=None,
      height=48
    ))
    layout.add_widget(self.posicion)
    layout.add_widget(Label(text="COMPETICIONES DE ESTA CARRERA", size_hint_y=None, height=28, font_size=14, bold=True, color=(0.98, 0.77, 0.32, 1)))
    self.opciones_competicion = {"segunda_division": True, "copas_grandes": False, "ligas_extras": False}
    for clave, texto in [
      ("segunda_division", "Incluir segunda división argentina"),
      ("copas_grandes", "Jugar copas grandes desde el inicio (Libertadores)"),
      ("ligas_extras", "Activar Brasil y ligas europeas (más partidos a simular)"),
    ]:
      boton_opcion = Button(
        text=("[ON]  " if self.opciones_competicion[clave] else "[OFF]  ") + texto,
        markup=False, size_hint_y=None, height=42, halign="left",
        background_color=(0.12, 0.38, 0.27, 1) if self.opciones_competicion[clave] else (0.10, 0.14, 0.19, 1)
      )
      boton_opcion.bind(on_press=lambda _btn, k=clave, b=boton_opcion, t=texto: self.alternar_opcion_competicion(k, b, t))
      layout.add_widget(boton_opcion)
    layout.add_widget(Label(text="ELEGÍ TU RETRATO", size_hint_y=None, height=26, font_size=14, bold=True))
    fila_retratos = GridLayout(cols=4, spacing=8, size_hint_y=None, height=190)
    self.botones_retrato = {}
    for etiqueta, ruta in self.rutas_retrato.items():
      boton_modelo = Button(
        text=etiqueta.upper(), size_hint_y=None, height=178, color=(1, 1, 1, 1), bold=True,
        background_normal=ruta, background_down=ruta,
        background_color=(0.25, 0.75, 0.45, 1) if etiqueta == self.retrato_seleccionado else (1, 1, 1, 1),
        border=(5, 5, 5, 5)
      )
      boton_modelo.bind(on_press=lambda _btn, nombre=etiqueta: self.seleccionar_retrato(nombre))
      self.botones_retrato[etiqueta] = boton_modelo
      fila_retratos.add_widget(boton_modelo)
    layout.add_widget(fila_retratos)
    layout.add_widget(Label(text="Podés cambiar el retrato más adelante tocando la imagen de tu futbolista.", size_hint_y=None, height=32))

    boton_crear = Button(text="EMPEZAR CARRERA")
    boton_crear.bind(on_press=self.crear)
    layout.add_widget(boton_crear)

    boton_volver = Button(text="VOLVER")
    boton_volver.bind(on_press=lambda *_: App.get_running_app().mostrar_pantalla("menu"))
    layout.add_widget(boton_volver)
    self.add_widget(layout)

  def crear(self, *_):
    app = App.get_running_app()
    nombre = self.nombre.text.strip()

    if not nombre:
      app.mostrar_mensaje("Ingresá un nombre para el jugador.")
      return

    app.carrera = Carrera.nueva(nombre, 18, self.posicion.text.lower(), opciones=getattr(self, "opciones_competicion", {}))
    jugador = app.carrera.jugador
    rutas = {
      "Modelo 1": "assets/players/retrato_1.png",
      "Modelo 2": "assets/players/retrato_2.png",
      "Modelo 3": "assets/players/retrato_3.png",
      "Modelo 4": "assets/players/retrato_4.png"
    }
    jugador.apariencia["retrato"] = self.rutas_retrato[self.retrato_seleccionado]
    app.mostrar_carrera()
    pantalla = app.pantallas.get_screen("carrera")
    Clock.schedule_once(lambda _dt: pantalla.iniciar_tutorial(), 0.35)

  def alternar_opcion_competicion(self, clave, boton, texto):
    valor = not self.opciones_competicion.get(clave, False)
    self.opciones_competicion[clave] = valor
    boton.text = ("[ON]  " if valor else "[OFF]  ") + texto
    boton.background_color = (0.12, 0.38, 0.27, 1) if valor else (0.10, 0.14, 0.19, 1)

  def seleccionar_retrato(self, nombre):
    self.retrato_seleccionado = nombre
    for etiqueta, boton in self.botones_retrato.items():
      boton.background_color = (0.25, 0.75, 0.45, 1) if etiqueta == nombre else (1, 1, 1, 1)


class GloboTexto(BoxLayout):
  """Globo visual para mensajes breves entre partidos."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    with self.canvas.before:
      Color(0.09, 0.16, 0.25, 1)
      self._fondo_globo = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
    self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

  def _actualizar_fondo(self, *_):
    self._fondo_globo.pos = self.pos
    self._fondo_globo.size = self.size


class PantallaCarrera(Screen):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    # Navegación lateral persistente: una sola estructura para todas las secciones.
    raiz = BoxLayout(orientation="horizontal", padding=7, spacing=7)
    self.botones_nav = {}
    barra_lateral = BoxLayout(orientation="vertical", size_hint_x=None, width=142, padding=(5, 10), spacing=5)
    with barra_lateral.canvas.before:
      Color(0.035, 0.055, 0.08, 1)
      barra_fondo = RoundedRectangle(pos=barra_lateral.pos, size=barra_lateral.size, radius=[12])
    barra_lateral.bind(pos=lambda w, v: setattr(barra_fondo, "pos", v), size=lambda w, v: setattr(barra_fondo, "size", v))
    marca = Label(text="[b]FOOTBALL[/b]\n[color=ffc34d]CAREER[/color]", markup=True, size_hint_y=None, height=72, font_size=19, halign="left")
    barra_lateral.add_widget(marca)
    barra_lateral.add_widget(Label(text="TU CARRERA", size_hint_y=None, height=22, font_size=10, color=(0.53, 0.65, 0.76, 1)))
    for clave, etiqueta in [
      ("inicio", "INICIO"),
      ("futbol", "FÚTBOL"),
      ("relaciones", "RELACIONES"),
      ("economia", "$   Economía"),
    ]:
      boton = Button(text=etiqueta, size_hint_y=None, height=48, font_size=12, halign="left", background_normal="", background_down="", background_color=(0.08, 0.12, 0.17, 1))
      boton.bind(on_press=lambda _, k=clave: self.mostrar_seccion(k))
      self.botones_nav[clave] = boton
      barra_lateral.add_widget(boton)
    barra_lateral.add_widget(Label(text="TEMPORADA\nEN CURSO", font_size=10, color=(0.43, 0.92, 0.65, 1)))
    barra_lateral.add_widget(Widget())
    raiz.add_widget(barra_lateral)

    columna = BoxLayout(orientation="vertical", padding=(2, 0, 0, 0), spacing=5)
    cabecera = BoxLayout(size_hint_y=None, height=42, spacing=6)
    cabecera.add_widget(Label(text="MI CARRERA", bold=True, font_size=18, halign="left"))
    guardar = Button(text="GUARDAR", size_hint_x=None, width=105)
    guardar.bind(on_press=self.guardar)
    cabecera.add_widget(guardar)
    menu = Button(text="MENÚ", size_hint_x=None, width=80)
    menu.bind(on_press=self.volver)
    cabecera.add_widget(menu)
    musica = Button(text="MÚSICA", size_hint_x=None, width=72, font_size=10)
    musica.bind(on_press=lambda *_: App.get_running_app().alternar_musica())
    cabecera.add_widget(musica)
    efectos = Button(text="EFECTOS", size_hint_x=None, width=72, font_size=10)
    efectos.bind(on_press=lambda *_: App.get_running_app().alternar_efectos())
    cabecera.add_widget(efectos)
    volumen = Button(text="VOL.", size_hint_x=None, width=54, font_size=11)
    volumen.bind(on_press=lambda *_: App.get_running_app().abrir_configuracion_audio())
    cabecera.add_widget(volumen)
    columna.add_widget(cabecera)
    self.resumen_recursos = TarjetaPremium(orientation="horizontal", size_hint_y=None, height=42, padding=(10, 3), spacing=12, fondo=(0.075, 0.13, 0.19, 1))
    self.resumen_dinero = Label(text="$0", font_size=17, bold=True, color=(0.42, 0.96, 0.68, 1))
    self.resumen_xp = Label(text="0 XP", font_size=17, bold=True, color=(1, 0.79, 0.30, 1))
    self.resumen_contrato = Label(text="Contrato: —", font_size=14, color=(0.85, 0.90, 0.96, 1))
    self.resumen_recursos.add_widget(self.resumen_dinero)
    self.resumen_recursos.add_widget(self.resumen_xp)
    self.resumen_recursos.add_widget(self.resumen_contrato)
    columna.add_widget(self.resumen_recursos)
    self.contenido_principal = BoxLayout(orientation="vertical", spacing=6)
    columna.add_widget(self.contenido_principal)
    self.cola_globos = []
    self.popup_globo = None
    self.mensaje = Label(text="Tu carrera está pausada.", size_hint_y=None, height=25, font_size=12, color=(0.66, 0.77, 0.86, 1))
    columna.add_widget(self.mensaje)
    raiz.add_widget(columna)
    self.add_widget(raiz)
    self.seccion_actual = "inicio"

  def mostrar_seccion(self, seccion):
    if seccion == "club":
      seccion = "futbol"
    self.seccion_actual = seccion
    self.contenido_principal.clear_widgets()
    app = App.get_running_app()
    if app.carrera is not None:
      j = app.carrera.jugador
      self.resumen_dinero.text = f"DINERO  ${j.dinero:,.0f}"
      self.resumen_xp.text = f"XP  {j.puntos_mejora}"
      self.resumen_contrato.text = f"CONTRATO  {getattr(j, 'contrato', 0)} sem."
    for clave, boton in self.botones_nav.items():
      boton.background_color = (0.16, 0.19, 0.25, 1) if clave != seccion else (0.16, 0.42, 0.31, 1)

    if seccion == "inicio":
      self._mostrar_inicio()
      return

    acciones = {
      "futbol": [
        ("PRÓXIMO PARTIDO · CONTINUAR CARRERA", self.continuar_carrera),
        ("Tabla de posiciones", self.ver_tabla_posiciones),
        ("Tablas de otras ligas", self.ver_tablas_competiciones),
        ("Copas y torneos", self.ver_copas_competiciones),
        ("Calendario y resultados", self.ver_calendario),
        ("Mi plantel y entrenador", self.ver_plantel),
        ("Situación contractual", self.ver_contrato),
        ("Mercado de pases", self.ver_mercado),
        ("Tienda de equipamiento", self.ver_tienda),
        ("Mejoras de atributos y carrera", self.ver_mejoras),
      ],
      "relaciones": [
        ("Charlar con el presidente", self.charlar_presidente),
        ("Mis vínculos", self.ver_vinculos),
        ("Logros", self.ver_logros),
        ("Eventos y notificaciones", self.ver_evento_social),
      ],
      "economia": [
        ("Ver patrocinadores y ofertas", self.abrir_sponsors),
        ("Administrar inversiones", self.ver_inversiones),
        ("Mejoras permanentes", self.ver_mejoras),
        ("Casino", self.ver_casino),
      ],
    }
    if seccion == "club":
      seccion = "futbol"
      self.seccion_actual = "futbol"
    titulo = {"futbol":"FÚTBOL Y MI CLUB", "relaciones":"RELACIONES", "economia":"ECONOMÍA"}[seccion]
    contenido = GridLayout(cols=1, spacing=8, padding=8, size_hint_y=None)
    contenido.bind(minimum_height=contenido.setter("height"))
    contenido.add_widget(Label(text=titulo, size_hint_y=None, height=38, bold=True, font_size=20))
    if seccion == "economia":
      contenido.add_widget(Label(text="Ingresos, contratos comerciales e inversiones", size_hint_y=None, height=30))
    for texto, accion in acciones[seccion]:
      boton = Button(text=texto, size_hint_y=None, height=52)
      boton.bind(on_press=accion)
      contenido.add_widget(boton)
    scroll = ScrollView()
    scroll.add_widget(contenido)
    self.contenido_principal.add_widget(scroll)

  def _mostrar_inicio(self):
    """Inicio rediseñado: jerarquía compacta, tarjetas y contenido desplazable."""
    self.contenido_principal.clear_widgets()
    app = App.get_running_app()
    carrera = app.carrera
    if carrera is None:
      self.contenido_principal.add_widget(Label(text="No hay una carrera cargada."))
      return

    datos = carrera.estado_resumido()
    scroll = ScrollView(do_scroll_x=False, bar_width=5)
    contenido = BoxLayout(orientation="vertical", spacing=10, padding=(4, 4), size_hint_y=None)
    contenido.bind(minimum_height=contenido.setter("height"))

    equipo = carrera.jugador.equipo
    nombre_equipo = equipo.nombre if equipo else "Agente libre"
    ruta_retrato = carrera.jugador.apariencia.get("retrato", "assets/players/retrato_1.png")
    if not os.path.exists(ruta_retrato):
      ruta_retrato = "assets/players/retrato_1.png"

    # Hero asimétrico: retrato y datos en un solo bloque, sin duplicar información.
    hero = TarjetaPremium(orientation="horizontal", padding=8, spacing=14,
      size_hint_y=None, height=285, fondo=(0.035, 0.055, 0.085, 1))
    retrato_box = BoxLayout(orientation="vertical", size_hint_x=None, width=250, spacing=5)
    retrato = Button(text="", size_hint_y=1, background_normal=ruta_retrato,
      background_down=ruta_retrato, border=(0, 0, 0, 0))
    retrato.bind(on_press=self.ver_personalizacion)
    retrato_box.add_widget(retrato)
    hero.add_widget(retrato_box)

    info = BoxLayout(orientation="vertical", spacing=5, padding=(8, 6))
    info.add_widget(Label(text="MI CARRERA", size_hint_y=None, height=20, halign="left",
      color=(0.96, 0.76, 0.30, 1), bold=True, font_size=12))
    info.add_widget(Label(text=datos["nombre"], size_hint_y=None, height=35, halign="left",
      color=(1, 1, 1, 1), bold=True, font_size=19))
    info.add_widget(Label(text=f"{datos['edad']} AÑOS  ·  {datos['posicion'].upper()}",
      size_hint_y=None, height=23, halign="left", color=(0.70, 0.77, 0.85, 1), font_size=11))
    rating = TarjetaPremium(orientation="horizontal", padding=(8, 4), spacing=7,
      size_hint_y=None, height=47, fondo=(0.12, 0.15, 0.20, 1))
    rating.add_widget(Label(text=str(datos["valoracion"]), font_size=25, bold=True,
      color=(0.98, 0.78, 0.32, 1), size_hint_x=0.35))
    rating.add_widget(Label(text=f"VALORACIÓN\n{nombre_equipo}", font_size=11,
      color=(0.95, 0.96, 0.98, 1), halign="left"))
    info.add_widget(rating)
    semanas_tutorial = getattr(carrera, "semanas_tutorial", 0)
    if datos["semana"] <= semanas_tutorial:
      texto_temporada = f"TEMPORADA {datos['temporada']} · PRETEMPORADA {datos['semana']}/{semanas_tutorial}"
    else:
      texto_temporada = f"TEMPORADA {datos['temporada']} · JORNADA {datos['semana'] - semanas_tutorial}"
    info.add_widget(Label(text=texto_temporada,
      size_hint_y=None, height=22, halign="left", color=(0.68, 0.78, 0.88, 1), font_size=10))
    info.add_widget(Label(text=f"${datos['dinero']:,.0f}  ·  {carrera.jugador.puntos_mejora} XP  ·  CONTRATO {datos['semanas_contrato']} sem.",
      size_hint_y=None, height=28, halign="left", color=(0.37, 0.92, 0.62, 1), font_size=15, bold=True))
    hero.add_widget(info)
    contenido.add_widget(hero)

    # Indicadores en tarjetas pequeñas, no en bloques de texto separados.
    indicadores = GridLayout(cols=2, spacing=8, size_hint_y=None, height=78)
    for titulo, valor, color in [
      ("FORMA", f"{datos['forma']}%", (0.32, 0.91, 0.61, 1)),
      ("MORAL", str(getattr(carrera.jugador, 'felicidad', 'Bien')), (0.42, 0.78, 1, 1)),
    ]:
      tarjeta = TarjetaPremium(orientation="vertical", padding=6, spacing=1,
        fondo=(0.075, 0.10, 0.15, 1))
      tarjeta.add_widget(Label(text=titulo, font_size=10, color=(0.64, 0.72, 0.81, 1)))
      tarjeta.add_widget(Label(text=valor, font_size=16, bold=True, color=color))
      indicadores.add_widget(tarjeta)
    contenido.add_widget(indicadores)

    proximo = self._obtener_proximo_partido()
    tarjeta_partido = TarjetaPremium(orientation="vertical", padding=12, spacing=7,
      size_hint_y=None, height=174, fondo=(0.055, 0.12, 0.12, 1))
    tarjeta_partido.add_widget(Label(text="PRÓXIMO PARTIDO", size_hint_y=None, height=20,
      color=(0.98, 0.77, 0.32, 1), bold=True, font_size=12, halign="left"))
    if proximo and equipo:
      rival, condicion, jornada = proximo
      tarjeta_partido.add_widget(Label(text=f"{equipo.nombre.upper()}     VS     {rival.upper()}",
        size_hint_y=None, height=34, font_size=17, bold=True, color=(1, 1, 1, 1)))
      tarjeta_partido.add_widget(Label(text=f"JORNADA {jornada}  ·  {condicion}",
        size_hint_y=None, height=22, font_size=11, color=(0.70, 0.81, 0.87, 1)))
      jugar_texto = "VER PARTIDO / CONTINUAR"
    else:
      tarjeta_partido.add_widget(Label(text="Todavía no tenés un partido asignado", size_hint_y=None, height=34,
        font_size=14, color=(0.94, 0.95, 0.98, 1)))
      tarjeta_partido.add_widget(Label(text="Avanzá la carrera para recibir oportunidades y calendario.",
        size_hint_y=None, height=22, font_size=11, color=(0.70, 0.81, 0.87, 1)))
      jugar_texto = "AVANZAR CARRERA"
    jugar = BotonPremium(text=jugar_texto, size_hint_y=None, height=38, font_size=12,
      background_color=(0.95, 0.70, 0.24, 1), color=(0.08, 0.08, 0.09, 1))
    jugar.bind(on_press=self.continuar_carrera)
    tarjeta_partido.add_widget(jugar)
    contenido.add_widget(tarjeta_partido)

    atajos = GridLayout(cols=2, spacing=7, size_hint_y=None, height=138)
    atajos_data = [
      ("MEJORAR ATRIBUTOS", self.ver_mejoras_atributos),
      ("PERSONALIZAR", self.ver_personalizacion),
      ("CONTRATO Y OFERTAS", self.ver_contrato),
      ("PATROCINADORES", self.abrir_sponsors),
      ("SIMULAR HASTA FIN DE TEMPORADA", self.confirmar_simulacion_temporada),
    ]
    for texto, accion in atajos_data:
      boton = Button(text=texto, font_size=11, bold=True, background_normal="",
        background_color=(0.12, 0.17, 0.23, 1), color=(0.93, 0.95, 0.98, 1))
      boton.bind(on_press=accion)
      atajos.add_widget(boton)
    contenido.add_widget(atajos)

    semana = carrera.temporada.semana
    if semana == 1:
      nota = "SEMANA DE BIENVENIDA · Explorá el perfil y preparate para empezar."
    elif equipo is None:
      nota = "AGENTE LIBRE · Revisá las ofertas de clubes en la sección Club."
    else:
      nota = f"EN ACTIVIDAD · {equipo.nombre} · Tu carrera está en marcha."
    contenido.add_widget(Label(text=nota, size_hint_y=None, height=35, font_size=11,
      color=(0.66, 0.77, 0.86, 1), halign="center"))
    scroll.add_widget(contenido)
    self.contenido_principal.add_widget(scroll)

  def confirmar_simulacion_temporada(self, *_):
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(text="Se simularán automáticamente las semanas restantes, incluyendo partidos, economía y competiciones. Esta acción avanza la carrera hasta el cierre de temporada.", halign="center", valign="middle"))
    botones = BoxLayout(size_hint_y=None, height=46, spacing=8)
    popup = Popup(title="Simulación rápida de temporada", content=contenido, size_hint=(0.82, 0.45))
    aceptar = BotonPremium(text="SIMULAR TEMPORADA")
    aceptar.bind(on_press=lambda *_: self._simular_temporada_rapido(popup))
    cancelar = Button(text="CANCELAR")
    cancelar.bind(on_press=popup.dismiss)
    botones.add_widget(aceptar)
    botones.add_widget(cancelar)
    contenido.add_widget(botones)
    popup.open()

  def _simular_temporada_rapido(self, popup):
    popup.dismiss()
    carrera = App.get_running_app().carrera
    resultado = carrera.simular_hasta_fin_temporada()
    self.actualizar()
    App.get_running_app().mostrar_mensaje(resultado.get("mensaje", "Simulación finalizada."))

  def elegir_retrato(self, *_):
    """Permite elegir un retrato genérico; no se fuerza una camiseta de club."""
    app = App.get_running_app()
    jugador = app.carrera.jugador
    opciones = [
      ("Modelo 1", "assets/players/retrato_1.png"),
      ("Modelo 2", "assets/players/retrato_2.png"),
      ("Modelo 3", "assets/players/retrato_3.png"),
      ("Modelo 4", "assets/players/retrato_4.png"),
    ]
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=8)
    contenido.add_widget(Label(text="Elegí el rostro inicial del futbolista", size_hint_y=None, height=32, font_size=16))
    fila = GridLayout(cols=2, spacing=8)
    popup = Popup(title="Elegir futbolista", content=contenido, size_hint=(0.88, 0.84))
    for etiqueta, ruta in opciones:
      tarjeta = BoxLayout(orientation="vertical", spacing=6, padding=6)
      tarjeta.add_widget(Image(source=ruta, allow_stretch=True, keep_ratio=True))
      boton = Button(text=etiqueta, size_hint_y=None, height=42, font_size=12)
      def seleccionar(_btn, path=ruta):
        jugador.apariencia["retrato"] = path
        jugador.apariencia.setdefault("peinado", "clasico")
        jugador.apariencia.setdefault("color_pelo", "castanio")
        jugador.apariencia.setdefault("piel", "media")
        popup.dismiss()
        self.actualizar()
      boton.bind(on_press=seleccionar)
      tarjeta.add_widget(boton)
      fila.add_widget(tarjeta)
    contenido.add_widget(fila)
    nota = Label(text="La elección se guarda en tu perfil. Los ajustes de pelo y piel están en Personalizar.", size_hint_y=None, height=40, font_size=11, color=(0.72, 0.79, 0.87, 1))
    contenido.add_widget(nota)
    cerrar = Button(text="CERRAR", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def _obtener_proximo_partido(self):
    carrera = App.get_running_app().carrera
    if carrera is None:
      return None
    equipo = carrera.jugador.equipo
    temporada = carrera.temporada
    desplazamiento_tutorial = getattr(carrera, "semanas_tutorial", 0)
    ultima_semana_interna = len(carrera.liga.jornadas) + desplazamiento_tutorial
    for semana_interna in range(temporada.semana, ultima_semana_interna + 1):
      for partido in temporada.obtener_partidos_semana(semana_interna):
        if equipo in (partido.local, partido.visitante) and partido.estado == "pendiente":
          rival = partido.visitante if partido.local == equipo else partido.local
          condicion = "LOCAL" if partido.local == equipo else "VISITANTE"
          return rival.nombre, condicion, max(1, semana_interna - desplazamiento_tutorial)
    return None

  def abrir_sponsors(self, *_):
    carrera = App.get_running_app().carrera
    if carrera is None:
      return
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    desplazamiento = ScrollView()
    self.contenido_sponsors = GridLayout(cols=1, spacing=8, padding=8, size_hint_y=None)
    self.contenido_sponsors.bind(minimum_height=self.contenido_sponsors.setter("height"))
    desplazamiento.add_widget(self.contenido_sponsors)
    contenido.add_widget(desplazamiento)
    cerrar = Button(text="CERRAR", size_hint_y=None, height=44)
    contenido.add_widget(cerrar)
    popup = Popup(title="Patrocinadores", content=contenido, size_hint=(0.88, 0.84))
    cerrar.bind(on_press=popup.dismiss)
    self.refrescar_sponsors()
    popup.open()

  def actualizar(self):
    carrera = App.get_running_app().carrera
    if carrera is None:
      self.estado.text = "No hay carrera cargada."
      return

    if self.seccion_actual == "inicio":
      self.mostrar_seccion("inicio")
    self.refrescar_sponsors()

  def iniciar_tutorial(self):
    """Tutorial guiado por ventanas emergentes que resalta cada pestaña."""
    self._pasos_tutorial = [
      ("INICIO", "Esta es tu pantalla principal: resumen del futbolista, próximo partido, dinero y puntos de mejora.", "inicio"),
      ("FÚTBOL Y MI CLUB", "Acá están el plantel, contrato, mercado, calendario y tablas. Las copas tienen su propio botón.", "futbol"),
      ("RELACIONES", "Desde acá podés interactuar con el presidente, revisar vínculos, logros y notificaciones.", "relaciones"),
      ("ECONOMÍA", "Administrá patrocinadores, inversiones y otros recursos.", "economia"),
      ("PRETEMPORADA", "El tutorial no cuenta como campeonato. Durante cuatro semanas no se juegan partidos; al terminar, la liga empieza en JORNADA 1.", None),
    ]
    self._indice_tutorial = 0
    self._mostrar_paso_tutorial()

  def _mostrar_paso_tutorial(self):
    pasos = getattr(self, "_pasos_tutorial", [])
    indice = getattr(self, "_indice_tutorial", 0)
    if indice >= len(pasos):
      self.popup_globo = None
      for boton in self.botones_nav.values():
        boton.background_color = (0.08, 0.12, 0.17, 1)
        boton.color = (0.93, 0.95, 0.98, 1)
      self.mostrar_seccion("inicio")
      self.mensaje.text = "Tutorial terminado. El campeonato todavía no comenzó; avanzá cuando estés listo."
      return
    titulo, descripcion, seccion = pasos[indice]
    if seccion:
      self.mostrar_seccion(seccion)
      for clave, boton in self.botones_nav.items():
        seleccionado = clave == seccion
        boton.background_color = (0.95, 0.68, 0.20, 1) if seleccionado else (0.08, 0.12, 0.17, 1)
        boton.color = (0.06, 0.07, 0.09, 1) if seleccionado else (0.93, 0.95, 0.98, 1)
    contenido = BoxLayout(orientation="vertical", padding=16, spacing=12)
    contenido.add_widget(Label(text=descripcion, halign="left", valign="middle", font_size=16))
    pie = BoxLayout(size_hint_y=None, height=44, spacing=8)
    omitir = Button(text="OMITIR", size_hint_x=0.34)
    siguiente = Button(text="SIGUIENTE" if indice < len(pasos)-1 else "TERMINAR TUTORIAL", background_color=(0.16, 0.48, 0.31, 1))
    popup = Popup(title=f"Tutorial · {indice+1}/{len(pasos)} · {titulo}", content=contenido, size_hint=(0.82, 0.48), auto_dismiss=False)
    def avanzar(*_):
      popup.dismiss()
      self.popup_globo = None
      self._indice_tutorial += 1
      self._mostrar_paso_tutorial()
    def omitir_todo(*_):
      popup.dismiss()
      self.popup_globo = None
      self._indice_tutorial = len(self._pasos_tutorial)
      self._mostrar_paso_tutorial()
    siguiente.bind(on_press=avanzar)
    omitir.bind(on_press=omitir_todo)
    pie.add_widget(omitir)
    pie.add_widget(siguiente)
    contenido.add_widget(pie)
    self.popup_globo = popup
    popup.open()

  def continuar_carrera(self, *_):
    """Abre el partido del usuario antes de procesar automáticamente la semana."""
    app = App.get_running_app()
    carrera = app.carrera
    if carrera is None:
      self.mensaje.text = "No hay una carrera cargada."
      return
    if self.popup_globo is not None:
      return
    if carrera.temporada.estado != "en juego":
      self.mensaje.text = "La temporada terminó. Podés revisar la tabla y los resultados."
      self.actualizar()
      return

    pendientes_sociales = [item for item in carrera.temporada.eventos_sociales_pendientes if not item["evento"].resuelto]
    if pendientes_sociales:
      self.mostrar_evento(pendientes_sociales[0]["evento"])
      return

    # Las primeras cuatro semanas son pretemporada/tutorial: no se juegan
    # partidos ni se cuentan como jornadas del campeonato.
    if carrera.temporada.semana <= getattr(carrera, "semanas_tutorial", 0):
      self.mensaje.text = (
        f"PRETEMPORADA · SEMANA {carrera.temporada.semana}/"
        f"{carrera.semanas_tutorial}. El campeonato todavía no comenzó."
      )
      self._procesar_semana_sin_partido_usuario()
      return

    equipo = carrera.jugador.equipo
    if equipo is not None:
      partidos_semana = carrera.temporada.obtener_partidos_semana(carrera.temporada.semana)
      partido_usuario = next((p for p in partidos_semana if equipo in (p.local, p.visitante) and p.estado == "pendiente"), None)
      if partido_usuario is not None:
        partido_usuario.jugador_controlado = carrera.jugador
        app.partido_actual = partido_usuario
        app.mostrar_pantalla("partido")
        return

    self._procesar_semana_sin_partido_usuario()

  def _procesar_semana_sin_partido_usuario(self):
    app = App.get_running_app()
    carrera = app.carrera
    semana_jugada = carrera.temporada.semana
    resultado = carrera.jugar_siguiente_semana()
    if resultado.get("requiere_evento"):
      self.mostrar_evento(resultado["evento"])
      return
    if not resultado.get("ok"):
      self.mensaje.text = resultado.get("mensaje", "No se pudo continuar la carrera.")
      return
    self.actualizar()
    mensajes = [f"SEMANA {semana_jugada} COMPLETADA", f"Dinero disponible: ${carrera.jugador.dinero:,.0f}."]
    if resultado.get("ofertas_nuevas", 0):
      mensajes.append("NUEVA OPORTUNIDAD: recibiste una oferta contractual. Revisá Club → Situación contractual.")
    if resultado.get("ventana_mercado"):
      mensajes.append("VENTANA DE MERCADO ABIERTA: esta semana se activan movimientos y ofertas de transferencias. Revisá Club → Mercado de pases.")
    for liquidacion in resultado.get("apuestas_liquidadas", []):
      mensajes.append(f"APUESTA DEPORTIVA: {liquidacion['mensaje']}")
    if resultado.get("nota"):
      mensajes.append(f"TU RENDIMIENTO: {resultado['nota']}")
    if carrera.temporada.estado != "en juego":
      mensajes.append("FIN DE TEMPORADA. Revisá la tabla final y tus estadísticas.")
    self.mostrar_resumen_unico("\n\n────────────────────\n\n".join(mensajes))

  def mostrar_resumen_unico(self, texto):
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    desplazamiento = ScrollView(do_scroll_x=False)
    etiqueta = Label(
      text=texto,
      size_hint_y=None,
      halign="left",
      valign="top",
      font_size=17,
      color=(0.96, 0.97, 1, 1)
    )
    etiqueta.bind(width=lambda widget, ancho: setattr(widget, "text_size", (ancho, None)))
    etiqueta.bind(texture_size=lambda widget, tam: setattr(widget, "height", tam[1] + 24))
    desplazamiento.add_widget(etiqueta)
    contenido.add_widget(desplazamiento)
    # Los avisos relevantes incluyen accesos directos; no obligamos a recordar el menú.
    accesos = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=8)
    if "oferta contractual" in texto.lower() or "situación contractual" in texto.lower():
      boton_ofertas = Button(text="IR A OFERTAS / CONTRATO", size_hint_x=0.65)
      boton_ofertas.bind(on_press=lambda *_: self._abrir_destino_resumen(popup, "contrato"))
      accesos.add_widget(boton_ofertas)
    if "mercado" in texto.lower():
      boton_mercado = Button(text="ABRIR MERCADO", size_hint_x=0.55)
      boton_mercado.bind(on_press=lambda *_: self._abrir_destino_resumen(popup, "mercado"))
      accesos.add_widget(boton_mercado)
    if len(accesos.children):
      contenido.add_widget(accesos)
    boton = Button(text="CERRAR NOVEDADES", size_hint_y=None, height=46)
    contenido.add_widget(boton)
    popup = Popup(
      title="Resumen de la semana",
      content=contenido,
      size_hint=(0.88, 0.78),
      auto_dismiss=False
    )
    boton.bind(on_press=lambda *_: self.cerrar_resumen(popup))
    self.popup_globo = popup
    popup.open()

  def _abrir_destino_resumen(self, popup, destino):
    popup.dismiss()
    self.popup_globo = None
    self.mostrar_seccion("club")
    if destino == "contrato":
      self.ver_contrato()
    elif destino == "mercado":
      self.ver_mercado()

  def cerrar_resumen(self, popup):
    popup.dismiss()
    self.popup_globo = None
    carrera = App.get_running_app().carrera
    pendientes = [
      item for item in carrera.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    if carrera.temporada.estado != "en juego":
      self.mensaje.text = "Temporada finalizada. Podés revisar la tabla y las estadísticas."
    elif pendientes:
      self.mensaje.text = "Resumen visto. Tenés un evento pendiente en Relaciones; podés resolverlo cuando quieras."
    else:
      self.mensaje.text = "Resumen visto. La carrera quedó pausada: revisá lo que quieras y tocá CONTINUAR CARRERA cuando estés listo."

  def ver_tablas_competiciones(self, *_):
    """Muestra tablas completas de todas las ligas y permite abrir cada plantel."""
    carrera = App.get_running_app().carrera
    if carrera is None:
      App.get_running_app().mostrar_mensaje("Primero iniciá o cargá una carrera.")
      return
    comps = [c for c in getattr(carrera.temporada, "competiciones", []) if isinstance(c, Liga)]
    if not comps:
      App.get_running_app().mostrar_mensaje("No hay ligas cargadas en esta carrera.")
      return

    raiz = BoxLayout(orientation="vertical", padding=8, spacing=6)
    selector = Spinner(
      text=comps[0].nombre,
      values=tuple(c.nombre for c in comps),
      size_hint_y=None,
      height=42
    )
    raiz.add_widget(selector)
    desplazamiento = ScrollView(do_scroll_x=True)
    tabla = GridLayout(
      cols=10,
      spacing=1,
      size_hint=(None, None),
      row_default_height=34,
      row_force_default=True,
      width=900
    )
    tabla.bind(minimum_height=tabla.setter("height"))
    anchos = [42, 250, 48, 42, 42, 42, 48, 48, 48, 58]
    tabla.width = sum(anchos)
    desplazamiento.add_widget(tabla)
    raiz.add_widget(desplazamiento)

    def cargar(*_):
      tabla.clear_widgets()
      comp = next((c for c in comps if c.nombre == selector.text), comps[0])
      cabecera = ["POS", "EQUIPO ↗", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]
      for indice, encabezado in enumerate(cabecera):
        tabla.add_widget(FondoLabel(
          text=f"[b]{encabezado}[/b]", markup=True,
          fondo=(0.07, 0.09, 0.12, 1),
          size_hint_x=None, width=anchos[indice],
          size_hint_y=None, height=34, font_size=12,
          halign="center", valign="middle"
        ))
      ordenados = comp.tabla()
      for posicion, equipo in enumerate(ordenados, 1):
        dg = equipo.gf - equipo.gc
        valores = [str(posicion), equipo.nombre, str(equipo.pj), str(equipo.g),
                   str(equipo.e), str(equipo.p), str(equipo.gf), str(equipo.gc),
                   f"{dg:+d}", str(equipo.pts)]
        zona = zona_tabla(posicion, len(ordenados))
        fondos = {
          "copa_principal": (0.10, 0.25, 0.17, 1),
          "copa_secundaria": (0.10, 0.19, 0.30, 1),
          "descenso": (0.30, 0.12, 0.14, 1),
          "normal": (0.12, 0.14, 0.18, 1)
        }
        fondo = fondos.get(zona, fondos["normal"])
        for indice, valor in enumerate(valores):
          if indice == 1:
            celda = Button(
              text=valor, background_normal="", background_down="",
              background_color=fondo, color=(0.96, 0.96, 0.98, 1),
              size_hint_x=None, width=anchos[indice],
              size_hint_y=None, height=34, font_size=12,
              halign="left", valign="middle"
            )
            celda.bind(on_press=lambda _btn, elegido=equipo: self.ver_plantel_equipo(elegido))
          else:
            celda = FondoLabel(
              text=f"[b]{valor}[/b]" if indice in (0, 9) else valor,
              markup=True, fondo=fondo, size_hint_x=None,
              width=anchos[indice], size_hint_y=None, height=34,
              font_size=12, halign="center", valign="middle",
              text_size=(anchos[indice], 34)
            )
          tabla.add_widget(celda)

    selector.bind(text=cargar)
    cargar()
    cerrar = Button(text="CERRAR", size_hint_y=None, height=42)
    popup = Popup(title="Tablas de otras ligas · Tocá un equipo para ver su plantel", content=raiz, size_hint=(0.97, 0.90))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def ver_copas_competiciones(self, *_):
    """Consulta copas por separado de las tablas de liga."""
    carrera = App.get_running_app().carrera
    if carrera is None:
      App.get_running_app().mostrar_mensaje("Primero iniciá o cargá una carrera.")
      return
    copas = [c for c in carrera.temporada.competiciones if not isinstance(c, Liga)]
    if not copas:
      App.get_running_app().mostrar_mensaje("No hay copas activadas en esta carrera. Podés elegirlas al crear una partida nueva.")
      return
    raiz = BoxLayout(orientation="vertical", padding=10, spacing=8)
    nombres = [c.nombre for c in copas]
    selector = Spinner(text=nombres[0], values=tuple(nombres), size_hint_y=None, height=42)
    raiz.add_widget(selector)
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=4, size_hint_y=None, padding=4)
    lista.bind(minimum_height=lista.setter("height"))
    scroll.add_widget(lista)
    raiz.add_widget(scroll)
    def cargar(*_):
      lista.clear_widgets()
      comp = next((c for c in copas if c.nombre == selector.text), copas[0])
      lista.add_widget(Label(text=f"{comp.nombre} · {getattr(comp, 'fase', comp.estado)} · {len(comp.equipos)} equipos", size_hint_y=None, height=38))
      partidos = getattr(comp, "partidos", [])
      if not partidos:
        lista.add_widget(Label(text="Todavía no hay partidos generados.", size_hint_y=None, height=36))
      for partido in partidos:
        if getattr(partido, "estado", "pendiente") == "terminado":
          marcador = f"{partido.resultado[0]} - {partido.resultado[1]}"
        else:
          marcador = "vs. · pendiente"
        lista.add_widget(FondoLabel(text=f"{partido.local.nombre}  {marcador}  {partido.visitante.nombre}", fondo=(0.09, 0.16, 0.22, 1), size_hint_y=None, height=34, font_size=12, halign="left"))
    selector.bind(text=cargar)
    cargar()
    cerrar = Button(text="CERRAR", size_hint_y=None, height=42)
    popup = Popup(title="Copas y torneos", content=raiz, size_hint=(0.92, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def ver_tabla_posiciones(self, *_):
    carrera = App.get_running_app().carrera
    liga = carrera.liga
    if carrera.jugador.equipo is None:
      app = App.get_running_app()
      app.mostrar_mensaje("Todavía no tenés club. Podés revisar las ofertas en Club → Situación contractual; cuando firmes, la tabla de tu liga aparecerá acá.")
      return
    equipos_ordenados = liga.tabla()

    raiz = BoxLayout(orientation="vertical", padding=8, spacing=6)
    raiz.add_widget(Label(
      text=f"{liga.nombre} · Temporada {carrera.temporada.anio}",
      size_hint_y=None,
      height=32,
      font_size=18
    ))

    leyenda = GridLayout(cols=2, size_hint_y=None, height=52, spacing=4)
    leyenda.add_widget(FondoLabel(
      text="  1–4 · Copa principal", fondo=(0.10, 0.38, 0.22, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    leyenda.add_widget(FondoLabel(
      text="  5–9 · Copa secundaria", fondo=(0.10, 0.27, 0.48, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    leyenda.add_widget(FondoLabel(
      text="  Últimos 2 · Descenso", fondo=(0.48, 0.13, 0.16, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    leyenda.add_widget(FondoLabel(
      text="  Tu equipo", fondo=(0.65, 0.45, 0.08, 1),
      size_hint_y=None, height=24, font_size=11, halign="left"
    ))
    raiz.add_widget(leyenda)

    desplazamiento = ScrollView(do_scroll_x=True)
    tabla = GridLayout(
      cols=10,
      spacing=1,
      size_hint=(None, None),
      row_default_height=32,
      row_force_default=True,
      width=900
    )
    tabla.bind(minimum_height=tabla.setter("height"))
    anchos = [42, 250, 48, 42, 42, 42, 48, 48, 48, 58]
    tabla.width = sum(anchos)

    encabezados = ["POS", "EQUIPO", "PJ", "G", "E", "P", "GF", "GC", "DG", "PTS"]
    for indice, encabezado in enumerate(encabezados):
      tabla.add_widget(FondoLabel(
        text=f"[b]{encabezado}[/b]",
        markup=True,
        fondo=(0.08, 0.09, 0.12, 1),
        size_hint_x=None,
        width=anchos[indice],
        size_hint_y=None,
        height=32,
        font_size=12
      ))

    colores_zona = {
      "copa_principal": (0.10, 0.25, 0.17, 1),
      "copa_secundaria": (0.10, 0.19, 0.30, 1),
      "descenso": (0.30, 0.12, 0.14, 1),
      "normal": (0.12, 0.14, 0.18, 1)
    }
    color_usuario = (0.42, 0.29, 0.06, 1)
    for posicion, equipo in enumerate(equipos_ordenados, start=1):
      diferencia = equipo.gf - equipo.gc
      valores = [
        str(posicion), equipo.nombre, str(equipo.pj), str(equipo.g),
        str(equipo.e), str(equipo.p), str(equipo.gf), str(equipo.gc),
        f"{diferencia:+d}", str(equipo.pts)
      ]
      zona = zona_tabla(posicion, len(equipos_ordenados))
      es_equipo_usuario = equipo is carrera.jugador.equipo
      for indice, valor in enumerate(valores):
        fondo = color_usuario if es_equipo_usuario else colores_zona[zona]
        # La celda de posición conserva el color de clasificación incluso en la fila del usuario.
        if indice == 0:
          fondo = colores_zona[zona]
        texto = f"[b]{valor}[/b]" if es_equipo_usuario or indice in (0, 9) else valor
        if indice == 1:
          boton_equipo = Button(
            text=texto,
            markup=True,
            background_normal="",
            background_color=fondo,
            color=(0.96, 0.96, 0.98, 1),
            size_hint_x=None,
            width=anchos[indice],
            size_hint_y=None,
            height=32,
            font_size=12,
            halign="left",
            valign="middle"
          )
          boton_equipo.bind(on_press=lambda _boton, equipo_seleccionado=equipo: self.ver_plantel_equipo(equipo_seleccionado))
          tabla.add_widget(boton_equipo)
        else:
          tabla.add_widget(FondoLabel(
            text=texto,
            markup=True,
            fondo=fondo,
            size_hint_x=None,
            width=anchos[indice],
            size_hint_y=None,
            height=32,
            font_size=12,
            halign="center",
            valign="middle",
            text_size=(anchos[indice], 32)
          ))

    desplazamiento.add_widget(tabla)
    raiz.add_widget(desplazamiento)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    popup = Popup(title="Tabla de posiciones", content=raiz, size_hint=(0.96, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def ver_plantel(self, *_):
    """Abre el plantel del club actual sin fallar cuando el jugador está libre."""
    app = App.get_running_app()
    carrera = getattr(app, "carrera", None)
    jugador = getattr(carrera, "jugador", None) if carrera else None
    equipo = getattr(jugador, "equipo", None) if jugador else None
    if equipo is None:
      contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
      contenido.add_widget(Label(
        text="Todavía no tenés club. Revisá las ofertas contractuales o avanzá semanas para recibir nuevas oportunidades.",
        halign="center", valign="middle"
      ))
      ofertas = Button(text="VER OFERTAS CONTRACTUALES", size_hint_y=None, height=44)
      contenido.add_widget(ofertas)
      cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
      contenido.add_widget(cerrar)
      popup = Popup(title="Mi plantel", content=contenido, size_hint=(0.8, 0.42))
      ofertas.bind(on_press=lambda *_: (popup.dismiss(), self.ver_contrato()))
      cerrar.bind(on_press=popup.dismiss)
      popup.open()
      return
    self.ver_plantel_equipo(equipo)

  def ver_plantel_equipo(self, equipo):
    """Muestra el plantel, minutos/participaciones y estadísticas reales por competición."""
    raiz = BoxLayout(orientation="vertical", padding=10, spacing=8)
    cabecera_plantel = BoxLayout(orientation="horizontal", size_hint_y=None, height=82, spacing=10)
    ruta_escudo = getattr(equipo, "ruta_escudo", "")
    if ruta_escudo:
      cabecera_plantel.add_widget(Image(source=ruta_escudo, size_hint_x=None, width=72, fit_mode="contain"))
    cabecera_plantel.add_widget(Label(
      text=f"[b]{equipo.nombre}[/b]\nDT: {equipo.dt} · Estadio: {equipo.estadio}",
      markup=True, halign="left", valign="middle"
    ))
    raiz.add_widget(cabecera_plantel)
    selector = Spinner(
      text="Estadísticas generales",
      values=("Estadísticas generales", "Temporada actual", "Liga", "Copas"),
      size_hint_y=None, height=42
    )
    raiz.add_widget(selector)
    desplazamiento_plantel = ScrollView()
    lista = GridLayout(cols=1, spacing=4, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    desplazamiento_plantel.add_widget(lista)
    raiz.add_widget(desplazamiento_plantel)

    def cargar_lista(*_):
      lista.clear_widgets()
      jugadores = sorted(equipo.jugadores, key=lambda j: getattr(j, "valoracion", 0), reverse=True)
      if not jugadores:
        lista.add_widget(Label(text="Este equipo todavía no tiene jugadores cargados.", size_hint_y=None, height=42))
        return
      for jugador in jugadores:
        valoracion = getattr(jugador, "valoracion", 0)
        edad = getattr(jugador, "edad", "—")
        posicion = getattr(jugador, "posicion", "Sin posición")
        reales = getattr(jugador, "estadisticas_reales", {})
        if selector.text == "Temporada actual":
          datos = reales.get("temporada", {})
        elif selector.text == "Liga":
          datos = reales.get("liga", {})
        elif selector.text == "Copas":
          datos = reales.get("copas", {})
        else:
          datos = reales.get("general", {})
        partidos = datos.get("partidos", getattr(jugador, "partidos_jugados", 0))
        goles = datos.get("goles", getattr(jugador, "goles", 0))
        asistencias = datos.get("asistencias", getattr(jugador, "asistencias", 0))
        titularidades = datos.get("titularidades", 0)
        suplencias = datos.get("suplencias", max(0, partidos - titularidades))
        vallas = datos.get("vallas_invictas", 0)
        atajadas = datos.get("atajadas", 0)
        tarjetas_amarillas = datos.get("amarillas", 0)
        tarjetas_rojas = datos.get("rojas", 0)
        etiqueta_real = " · JUGADOR REAL" if getattr(jugador, "es_jugador_real", False) else ""
        texto = (
          f"[b]{jugador.nombre}[/b]{etiqueta_real} · {posicion} · {edad} años · VAL {valoracion}\n"
          f"PJ {partidos} · Titular {titularidades} · Suplente {suplencias} · "
          f"Goles {goles} · Asistencias {asistencias}\n"
          f"Vallas invictas {vallas} · Atajadas {atajadas} · "
          f"Amarillas {tarjetas_amarillas} · Rojas {tarjetas_rojas}"
        )
        lista.add_widget(FondoLabel(
          text=texto, markup=True, fondo=(0.12, 0.15, 0.20, 1),
          size_hint_y=None, height=76, font_size=12, halign="left", valign="middle",
          text_size=(680, 76)
        ))
    selector.bind(text=cargar_lista)
    cargar_lista()
    cerrar = Button(text="Volver", size_hint_y=None, height=42)
    popup = Popup(title=f"Plantel · {equipo.nombre}", content=raiz, size_hint=(0.92, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def ver_calendario(self, *_):
    carrera = App.get_running_app().carrera
    temporada = carrera.temporada
    semanas = sorted({semana for semana in temporada.calendario})
    if not semanas:
      App.get_running_app().mostrar_mensaje("Todavía no hay partidos programados.")
      return

    raiz = BoxLayout(orientation="vertical", padding=10, spacing=8)
    controles = BoxLayout(size_hint_y=None, height=42, spacing=8)
    controles.add_widget(Label(text="Jornada:", size_hint_x=None, width=85))
    selector = Spinner(
      text=str(min(temporada.semana, max(semanas))),
      values=tuple(str(semana) for semana in semanas),
      size_hint_x=None,
      width=100
    )
    controles.add_widget(selector)
    controles.add_widget(Label(
      text="Elegí una jornada para consultar sus partidos.",
      halign="left"
    ))
    raiz.add_widget(controles)

    lista_scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=5, padding=4, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    lista_scroll.add_widget(lista)
    raiz.add_widget(lista_scroll)

    def actualizar_jornada(texto):
      lista.clear_widgets()
      semana = int(texto)
      partidos = temporada.obtener_partidos_semana(semana)
      partidos.sort(key=lambda partido: (
        partido.local.nombre.lower(), partido.visitante.nombre.lower()
      ))
      lista.add_widget(Label(
        text=(f"PRETEMPORADA · SEMANA {semana}/{getattr(App.get_running_app().carrera, 'semanas_tutorial', 0)}"
              if semana <= getattr(App.get_running_app().carrera, 'semanas_tutorial', 0)
              else f"JORNADA {semana - getattr(App.get_running_app().carrera, 'semanas_tutorial', 0)} · {len(partidos)} PARTIDOS · TODAS LAS COMPETICIONES"),
        size_hint_y=None,
        height=32,
        font_size=16
      ))
      if not partidos:
        lista.add_widget(Label(
          text="No hay partidos programados para esta jornada.",
          size_hint_y=None,
          height=40
        ))
        return

      for partido in partidos:
        if partido.estado == "terminado":
          marcador = f"{partido.resultado[0]} - {partido.resultado[1]}"
          estado = "FINAL"
        elif partido.estado == "en juego":
          marcador = f"{partido.resultado[0]} - {partido.resultado[1]}"
          estado = f"EN JUEGO · {partido.minuto}'"
        else:
          marcador = "vs"
          estado = "PENDIENTE"
        fila = BoxLayout(size_hint_y=None, height=46, spacing=6)
        fila.add_widget(Label(
          text=partido.local.nombre,
          halign="right",
          text_size=(None, None)
        ))
        fila.add_widget(Label(
          text=marcador,
          size_hint_x=None,
          width=100,
          bold=True
        ))
        fila.add_widget(Label(text=partido.visitante.nombre))
        tipo_competicion = getattr(partido, "competicion_nombre", None) or getattr(partido, "tipo", "liga")
        tipo_competicion = str(tipo_competicion).replace("_", " ").upper()
        fila.add_widget(Label(text=tipo_competicion, size_hint_x=None, width=125, font_size=10, color=(0.98, 0.78, 0.32, 1)))
        fila.add_widget(Label(
          text=estado,
          size_hint_x=None,
          width=115,
          font_size=11
        ))
        lista.add_widget(fila)

    selector.bind(text=lambda _, texto: actualizar_jornada(texto))
    actualizar_jornada(selector.text)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    popup = Popup(title="Calendario y resultados", content=raiz, size_hint=(0.94, 0.88))
    cerrar.bind(on_press=popup.dismiss)
    raiz.add_widget(cerrar)
    popup.open()

  def guardar(self, *_):
    app = App.get_running_app()
    try:
      ruta = GestorGuardado.guardar({"carrera": app.carrera}, RUTA_GUARDADO)
      app.mostrar_mensaje(f"Partida guardada en {ruta}.")
    except Exception as error:
      app.mostrar_mensaje(f"No se pudo guardar: {error}")

  def ver_sponsors(self, *_):
    self.refrescar_sponsors()

  def refrescar_sponsors(self):
    if not hasattr(self, "contenido_sponsors"):
      return
    app = App.get_running_app()
    carrera = app.carrera
    if carrera is None:
      return

    lista = self.contenido_sponsors
    lista.clear_widgets()
    jugador = carrera.jugador
    lista.add_widget(Label(
      text=f"PATROCINADORES · {len(jugador.sponsors)}/{jugador.espacios_sponsor} espacios ocupados\nDinero: ${jugador.dinero:,.0f}",
      size_hint_y=None, height=56, font_size=17
    ))

    lista.add_widget(Label(text="CONTRATOS ACTIVOS", size_hint_y=None, height=32, bold=True))
    if jugador.sponsors:
      for sponsor in jugador.sponsors.values():
        lista.add_widget(Label(
          text=f"{sponsor.nombre} · ${sponsor.pago_semanal:,.0f}/semana · {sponsor.semanas_restantes} semanas",
          size_hint_y=None, height=48
        ))
    else:
      lista.add_widget(Label(text="Todavía no tenés patrocinadores contratados.", size_hint_y=None, height=42))

    bolsa = carrera.temporada.bolsa_sponsors
    if not bolsa.ofertas:
      bolsa.actualizar(carrera.temporada.semana)
    lista.add_widget(Label(text="OFERTAS DISPONIBLES · Tocá una para contratar", size_hint_y=None, height=42, bold=True))
    ofertas_disponibles = [
      (indice, oferta) for indice, oferta in enumerate(bolsa.ofertas)
      if oferta.estado == "disponible"
    ]
    if not ofertas_disponibles:
      lista.add_widget(Label(text="No hay ofertas disponibles en este momento.", size_hint_y=None, height=42))
    for indice, oferta in ofertas_disponibles:
      sponsor = oferta.sponsor
      texto = (
        f"{sponsor.nombre} · {sponsor.categoria_comercial}\n"
        f"${sponsor.pago_semanal:,.0f}/semana · {sponsor.duracion_semanas} semanas"
      )
      if oferta.bono_firma:
        texto += f" · Bono de firma ${oferta.bono_firma:,.0f}"
      if oferta.requisito_reputacion:
        texto += f" · Reputación requerida: {oferta.requisito_reputacion}"
      boton = Button(text=texto, size_hint_y=None, height=68)
      boton.bind(on_press=lambda _, i=indice: self.aceptar_sponsor(i))
      lista.add_widget(boton)

  def aceptar_sponsor(self, indice, popup=None):
    app = App.get_running_app()
    ok = app.carrera.aceptar_sponsor(indice)
    if ok:
      app.carrera.temporada.sistema_logros.actualizar(app.carrera.jugador)
      if popup is not None:
        popup.dismiss()
    app.mostrar_mensaje("Sponsor contratado." if ok else "No cumplís los requisitos, no hay espacio o ya tenés un sponsor de esa categoría.")
    self.actualizar()
    self.refrescar_sponsors()

  def ver_tienda(self, *_):
    app = App.get_running_app()
    carrera = app.carrera
    bolsa = carrera.temporada.bolsa_equipamiento
    if not bolsa.ofertas:
      bolsa.actualizar(carrera.temporada.semana)

    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    popup = Popup(title="Oportunidades de equipamiento", content=contenido, size_hint=(0.85, 0.8))
    for indice, item in enumerate(bolsa.ofertas):
      texto = (
        f"{item['nombre']} · ${item['precio']}"
        f" (antes ${item['precio_original']})\n"
        f"-{item['descuento']}% · dura aprox. una temporada ({item['durabilidad']} partidos) · stock {item['stock']}"
      )
      boton = Button(text=texto, size_hint_y=None, height=65)
      boton.bind(on_press=lambda _, i=indice: self.comprar_oferta_equipo(i, popup))
      contenido.add_widget(boton)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def comprar_oferta_equipo(self, indice, popup):
    app = App.get_running_app()
    resultado = app.carrera.comprar_oferta_equipamiento(indice)
    if resultado["ok"]:
      popup.dismiss()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def comprar_equipo(self, identificador):
    app = App.get_running_app()
    resultado = app.carrera.comprar_equipamiento(identificador)
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def ver_inversiones(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=6, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    contenido.add_widget(Label(
      text=f"Dinero disponible: ${jugador.dinero}\nIngresos semanales actuales: ${sum(inv.ingreso_semanal for inv in jugador.inversiones):.0f}",
      size_hint_y=None,
      height=55
    ))

    for identificador, oferta in Inversion.CATALOGO.items():
      req_val = oferta.get("valoracion_minima", 0)
      req_pat = oferta.get("patrimonio_minimo", 0)
      desbloqueada = jugador.valoracion >= req_val and jugador.dinero + sum(getattr(inv, "dinero_invertido", 0) for inv in jugador.inversiones) >= req_pat
      texto = (
        f"{oferta['nombre']} · ${oferta['costo']}\n"
        f"Ingreso semanal: ${oferta['ingreso_semanal']}\n{oferta['descripcion']}\n"
        f"Requisitos: valoración {req_val} · patrimonio ${req_pat:,} · {'DISPONIBLE' if desbloqueada else 'BLOQUEADA'}"
      )
      boton = Button(text=texto, size_hint_y=None, height=105, disabled=not desbloqueada)
      boton.bind(on_press=lambda _, ident=identificador: self.comprar_inversion(ident, popup))
      lista.add_widget(boton)

    if jugador.inversiones:
      lista.add_widget(Label(text="Tus inversiones", size_hint_y=None, height=35))
      for inversion in jugador.inversiones:
        lista.add_widget(Label(
          text=f"{inversion.nombre} · Nivel {inversion.nivel} · ${inversion.ingreso_semanal:.0f}/semana",
          size_hint_y=None,
          height=35
        ))
        mejorar = Button(
          text=f"Mejorar inversión · ${max(1000, inversion.costo // 2)}",
          size_hint_y=None,
          height=45
        )
        mejorar.bind(on_press=lambda _, inv=inversion: self.mejorar_inversion(inv, popup))
        lista.add_widget(mejorar)

    scroll.add_widget(lista)
    contenido.add_widget(scroll)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    popup = Popup(title="Inversiones", content=contenido, size_hint=(0.88, 0.85))
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def comprar_inversion(self, identificador, popup=None):
    app = App.get_running_app()
    resultado = app.carrera.comprar_inversion(identificador)
    app.mostrar_mensaje(resultado["mensaje"])
    if popup is not None:
      popup.dismiss()
    self.actualizar()
    self.ver_inversiones()

  def mejorar_inversion(self, inversion, popup=None):
    app = App.get_running_app()
    costo = max(1000, inversion.costo // 2)
    if inversion.mejorar(app.carrera.jugador, costo):
      app.mostrar_mensaje(f"Mejoraste {inversion.nombre}; ahora genera ${inversion.ingreso_semanal:.0f} por semana.")
    else:
      app.mostrar_mensaje("No tenés dinero suficiente para mejorar esta inversión.")
    if popup is not None:
      popup.dismiss()
    self.actualizar()
    self.ver_inversiones()

  def ver_mejoras_atributos(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=7)
    cabecera_xp = TarjetaPremium(orientation="vertical", padding=10, spacing=3, size_hint_y=None, height=82, fondo=(0.08, 0.15, 0.20, 1))
    cabecera_xp.add_widget(Label(text=f"PUNTOS DE MEJORA DISPONIBLES: {jugador.puntos_mejora} XP", size_hint_y=None, height=30, font_size=18, bold=True, color=(1, 0.79, 0.30, 1)))
    cabecera_xp.add_widget(Label(text="Cada atributo tiene su propia tarjeta y muestra el costo de la próxima mejora.", size_hint_y=None, height=26, font_size=12))
    contenido.add_widget(cabecera_xp)
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=7, padding=3, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    for atributo, valor in jugador.estadisticas.items():
      fila = TarjetaPremium(orientation="horizontal", size_hint_y=None, height=64, spacing=8, padding=(10, 5), fondo=(0.075, 0.105, 0.15, 1))
      costo = jugador.costo_mejora_estadistica(atributo)
      if costo is None:
        costo_texto = "Máximo"
        boton_texto = "Máximo"
      else:
        costo_texto = f"{costo} XP"
        boton_texto = f"Mejorar ({costo})"
      datos_atributo = BoxLayout(orientation="vertical", spacing=1)
      datos_atributo.add_widget(Label(text=atributo.replace("_", " ").title(), font_size=15, bold=True, halign="left", color=(0.96, 0.97, 1, 1)))
      datos_atributo.add_widget(Label(text=f"Nivel {valor}/100  ·  Próxima mejora: {costo_texto}", font_size=12, halign="left", color=(0.68, 0.80, 0.90, 1)))
      fila.add_widget(datos_atributo)
      mas = Button(text=boton_texto, size_hint_x=None, width=125, disabled=costo is None or jugador.puntos_mejora < costo)
      mas.bind(on_press=lambda _, a=atributo: self.aplicar_mejora_atributo(a, 1))
      fila.add_widget(mas)
      lista.add_widget(fila)
    scroll.add_widget(lista)
    contenido.add_widget(scroll)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    popup = Popup(title="Atributos y puntos de mejora", content=contenido, size_hint=(0.9, 0.9))
    self.popup_atributos = popup
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def aplicar_mejora_atributo(self, atributo, cantidad):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    if cantidad > 0:
      anterior = jugador.valoracion
      costo = jugador.costo_mejora_estadistica(atributo)
      if costo is None or jugador.puntos_mejora < costo:
        app.mostrar_mensaje(f"Necesitás {costo if costo is not None else 'más'} XP para mejorar {atributo}. Te quedan {jugador.puntos_mejora}.")
      else:
        jugador.mejorar_estadistica(atributo, 1)
        app.mostrar_mensaje(f"{atributo.title()} mejoró. Valoración: {anterior} → {jugador.valoracion}. XP restantes: {jugador.puntos_mejora}.")
    if getattr(self, "popup_atributos", None) is not None:
      self.popup_atributos.dismiss()
    self.actualizar()
    self.ver_mejoras_atributos()

  def ver_mejoras(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    scroll = ScrollView()
    lista = GridLayout(cols=1, spacing=6, size_hint_y=None)
    lista.bind(minimum_height=lista.setter("height"))
    scroll.add_widget(lista)
    contenido.add_widget(scroll)
    popup = Popup(title="Mejoras permanentes", content=contenido, size_hint=(0.88, 0.85))

    for identificador, mejora in MejoraCarrera.CATALOGO.items():
      nivel = MejoraCarrera.nivel(jugador, identificador)
      max_nivel = mejora["max_nivel"]
      precio = MejoraCarrera.costo_siguiente_nivel(jugador, identificador) if nivel < max_nivel else None
      if identificador == "espacio_sponsor":
        progreso = "Comprada" if nivel else "No adquirida"
      else:
        progreso = f"Nivel {nivel}/{max_nivel} · bonificación actual: +{round((jugador.bonificadores.get(mejora['bonificador'], 1.0) - 1) * 100)}%"
      texto_precio = f"${precio}" if precio is not None else "NIVEL MÁXIMO"
      boton = Button(
        text=f"{mejora['nombre']} · {texto_precio}\n{progreso}\n{mejora['descripcion']}" + (f" Cada nivel suma {int(mejora['incremento'] * 100)}%." if mejora["incremento"] else ""),
        size_hint_y=None,
        height=100,
        disabled=nivel >= max_nivel
      )
      boton.bind(on_press=lambda _, ident=identificador, pop=popup: self.comprar_mejora(ident, pop))
      lista.add_widget(boton)

    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def comprar_mejora(self, identificador, popup=None):
    app = App.get_running_app()
    ok = app.carrera.comprar_mejora(identificador)
    app.mostrar_mensaje("Mejora comprada: bonificación aumentada un 5%." if ok else "No tenés dinero suficiente o esa mejora llegó al nivel máximo.")
    if popup is not None:
      popup.dismiss()
    self.actualizar()
    self.ver_mejoras()

  def ver_evento_social(self, *_):
    app = App.get_running_app()
    pendientes = [
      item for item in app.carrera.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    if not pendientes:
      self.mensaje.text = "No hay notificaciones sociales pendientes. Avanzá al próximo partido para recibir nuevas oportunidades."
      return
    self.mostrar_evento(pendientes[0]["evento"])

  def mostrar_evento(self, evento):
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=6)
    contenido.add_widget(Label(
      text=f"{evento.titulo}\n{evento.descripcion}\n\nElegí una opción para cerrar esta notificación y continuar la carrera."
    ))
    popup = Popup(title="Notificación de la carrera", content=contenido, size_hint=(0.85, 0.75), auto_dismiss=False)
    for indice, opcion in enumerate(evento.opciones):
      boton = Button(
        text=f"{opcion.texto} · ${opcion.coste}",
        size_hint_y=None,
        height=58
      )
      boton.bind(on_press=lambda _, i=indice: self.elegir_evento(evento, i, popup))
      contenido.add_widget(boton)

    dejar = Button(text="Dejar pendiente", size_hint_y=None, height=40)
    dejar.bind(on_press=popup.dismiss)
    contenido.add_widget(dejar)
    popup.open()

  def elegir_evento(self, evento, indice, popup=None):
    app = App.get_running_app()
    resultado = app.carrera.resolver_evento_social(evento, indice)
    if resultado["ok"] and popup is not None:
      popup.dismiss()
      self.mensaje.text = (
        f"Notificación resuelta: {evento.titulo}. La carrera quedó pausada; "
        "podés revisar otras pestañas y continuar cuando quieras."
      )
      self.actualizar()
      return
    else:
      self.mensaje.text = resultado["mensaje"]
    self.actualizar()

  def ver_contrato(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contrato = jugador.contrato

    contenido = BoxLayout(orientation="vertical", padding=10, spacing=8)
    if contrato is None or not contrato.esta_vigente():
      contenido.add_widget(Label(text="Estás libre. Podés esperar ofertas o elegir una de las disponibles."))
      for oferta in app.carrera.ofertas_contractuales:
        if oferta["estado"] != "pendiente":
          continue
        bloque_oferta = BoxLayout(orientation="vertical", size_hint_y=None, height=94, spacing=3)
        fila_oferta = BoxLayout(size_hint_y=None, height=48, spacing=5)
        fila_oferta.add_widget(Label(text=f"{oferta['equipo'].nombre} · ${oferta['salario']}/sem."))
        ver_plantel = Button(text="Ver plantel", size_hint_x=None, width=105)
        ver_plantel.bind(on_press=lambda _, equipo=oferta["equipo"]: self.ver_plantel_equipo(equipo))
        aceptar = Button(text="Firmar", size_hint_x=None, width=82)
        aceptar.bind(on_press=lambda _, o=oferta: self.responder_oferta(o, True, popup))
        rechazar = Button(text="Rechazar", size_hint_x=None, width=90)
        rechazar.bind(on_press=lambda _, o=oferta: self.responder_oferta(o, False, popup))
        fila_oferta.add_widget(ver_plantel)
        fila_oferta.add_widget(aceptar)
        fila_oferta.add_widget(rechazar)
        bloque_oferta.add_widget(fila_oferta)
        resumen_plantel = Label(
          text=f"Plantel: {len(oferta['equipo'].jugadores)} jugadores · " +
          f"Arqueros: {sum(1 for j in oferta['equipo'].jugadores if j.posicion.lower() in ('arquero', 'portero'))}",
          size_hint_y=None, height=34, halign="left"
        )
        bloque_oferta.add_widget(resumen_plantel)
        contenido.add_widget(bloque_oferta)
    else:
      contenido.add_widget(Label(
        text=(
          f"Club: {contrato.club.nombre}\n"
          f"Salario: ${contrato.salario_semanal}/semana\n"
          f"Semanas restantes: {contrato.semanas_restantes}"
        )
      ))

    popup = Popup(title="Situación contractual", content=contenido, size_hint=(0.85, 0.8))

    boton_renovar = Button(text="Solicitar renovación", size_hint_y=None, height=48)
    boton_renovar.bind(on_press=lambda *_: self.accion_renovacion(popup))
    contenido.add_widget(boton_renovar)

    if (contrato is None or not contrato.esta_vigente()) and jugador.equipo is not None:
      boton_negociar = Button(text="Negociar contrato", size_hint_y=None, height=48)
      boton_negociar.bind(on_press=lambda *_: self.abrir_negociacion(popup))
      contenido.add_widget(boton_negociar)
    elif jugador.equipo is None:
      contenido.add_widget(Label(
        text="Sin club no se negocia directamente: firmá una oferta disponible.",
        size_hint_y=None, height=36
      ))

    boton_transferible = Button(text="Pedir estar en lista de transferibles", size_hint_y=None, height=48)
    boton_transferible.bind(on_press=lambda *_: self.pedir_transferible(popup))
    contenido.add_widget(boton_transferible)

    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def responder_oferta(self, oferta, aceptar, popup):
    app = App.get_running_app()
    resultado = app.carrera.responder_oferta_contractual(oferta, aceptar)
    popup.dismiss()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()
    self.ver_contrato()

  def accion_renovacion(self, popup_anterior):
    app = App.get_running_app()
    popup_anterior.dismiss()
    resultado, negociacion = app.carrera.solicitar_renovacion()
    if not resultado["ok"]:
      app.mostrar_mensaje(resultado["mensaje"])
      return
    self.mostrar_minijuego_negociacion(negociacion)

  def abrir_negociacion(self, popup_anterior):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    popup_anterior.dismiss()

    if jugador.contrato is not None and jugador.contrato.esta_vigente():
      resultado, negociacion = app.carrera.solicitar_renovacion()
      if not resultado["ok"]:
        app.mostrar_mensaje(resultado["mensaje"])
        return
      self.mostrar_minijuego_negociacion(negociacion)
      return

    if jugador.equipo is None:
      app.mostrar_mensaje(
        "Estás sin equipo: no podés negociar un contrato directamente. "
        "Elegí una oferta pendiente o avanzá semanas para recibir nuevas oportunidades."
      )
      self.ver_contrato()
      return

    negociacion = app.carrera.negociar_contrato()
    if negociacion is None:
      app.mostrar_mensaje("Necesitás pertenecer a un club para negociar directamente.")
      return
    self.mostrar_minijuego_negociacion(negociacion)

  def mostrar_minijuego_negociacion(self, negociacion):
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(
      text=(
        f"El club ofrece ${negociacion.salario_ofrecido} por semana.\n"
        "Mové la mano hasta el punto que consideres adecuado y probá cerrar el acuerdo."
      ),
      size_hint_y=None,
      height=75
    ))
    slider = Slider(min=0, max=100, value=50, step=1)
    # La posición exacta queda oculta. Solo se revela una pista aproximada y ruidosa,
    # para que negociar requiera intuición y no sea seguir un marcador fijo.
    senal = max(0, min(100, negociacion.objetivo + random.randint(-18, 18)))
    if senal < 34:
      pista = "La señal del club apunta hacia el lado izquierdo."
    elif senal > 66:
      pista = "La señal del club apunta hacia el lado derecho."
    else:
      pista = "La señal del club apunta hacia la zona central."
    contenido.add_widget(Label(
      text="SEÑAL DE NEGOCIACIÓN\n" + pista + "\nLa señal no es exacta: estimá dónde cerrar el acuerdo.",
      size_hint_y=None, height=76, halign="center", valign="middle"
    ))
    contenido.add_widget(Label(text="Mové el control para elegir tu posición. Cuanto más cerca estés del punto del club, más probable será firmar."))
    contenido.add_widget(slider)
    popup = Popup(title="Negociación de contrato", content=contenido, size_hint=(0.85, 0.55))

    boton = Button(text="ESTRECHAR LAS MANOS", size_hint_y=None, height=48)
    boton.bind(on_press=lambda *_: self.resolver_negociacion(negociacion, slider.value, popup))
    contenido.add_widget(boton)
    cancelar = Button(text="Cancelar", size_hint_y=None, height=38)
    cancelar.bind(on_press=popup.dismiss)
    contenido.add_widget(cancelar)
    popup.open()

  def resolver_negociacion(self, negociacion, posicion, popup):
    app = App.get_running_app()
    resultado = negociacion.intentar_acuerdo(posicion)
    popup.dismiss()
    if resultado["ok"]:
      app.mostrar_mensaje(
        f"{resultado['mensaje']}\nSalario acordado: ${resultado['salario_semanal']}/semana."
      )
    else:
      app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def pedir_transferible(self, popup):
    app = App.get_running_app()
    resultado = app.carrera.solicitar_lista_transferibles()
    popup.dismiss()
    app.mostrar_mensaje(resultado["mensaje"])

  def ver_casino(self, *_):
    app = App.get_running_app()
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=7)
    contenido.add_widget(Label(text=f"CASINO · Dinero disponible: ${app.carrera.jugador.dinero:,}\nApuesta mínima general $100 · deportiva $1.000 · máxima $10.000", size_hint_y=None, height=55))
    apuesta = TextInput(text="1000", hint_text="Apuesta", multiline=False, input_filter="int", size_hint_y=None, height=42)
    contenido.add_widget(apuesta)
    juego = Spinner(text="Ruleta", values=("Ruleta", "Tragamonedas", "Carrera de caballos", "Apuestas deportivas"), size_hint_y=None, height=42)
    contenido.add_widget(juego)
    partidos_disponibles = [p for p in app.carrera.temporada.obtener_partidos_semana(app.carrera.temporada.semana) if p.estado == "pendiente"]
    if not partidos_disponibles:
      partidos_disponibles = [p for p in app.carrera.temporada.obtener_partidos_semana(app.carrera.temporada.semana + 1) if p.estado == "pendiente"]
    mapa_partidos = {f"{p.local.nombre} vs {p.visitante.nombre}": p for p in partidos_disponibles}
    partido_spinner = Spinner(text=next(iter(mapa_partidos), "Sin partidos disponibles"), values=tuple(mapa_partidos) or ("Sin partidos disponibles",), size_hint_y=None, height=42)
    contenido.add_widget(partido_spinner)
    eleccion = Spinner(text="rojo", values=("rojo", "negro", "par", "impar", "0", "7", "14", "21", "28", "Relámpago", "Tormenta", "Centella", "Sombra", "local", "empate", "visitante"), size_hint_y=None, height=42)
    contenido.add_widget(eleccion)
    resultado_label = Label(text="Elegí el juego, la apuesta y la opción.", size_hint_y=None, height=65)
    contenido.add_widget(resultado_label)
    popup = Popup(title="Casino · dinero virtual", content=contenido, size_hint=(0.88, 0.78))

    def actualizar_opciones(spinner, valor):
      if valor == "Ruleta":
        eleccion.values = ("rojo", "negro", "par", "impar", "0", "7", "14", "21", "28")
        eleccion.text = "rojo"
      elif valor == "Tragamonedas":
        eleccion.values = ("Girar",)
        eleccion.text = "Girar"
      elif valor == "Carrera de caballos":
        eleccion.values = ("Relámpago", "Tormenta", "Centella", "Sombra")
        eleccion.text = "Relámpago"
      else:
        eleccion.values = ("local", "empate", "visitante")
        eleccion.text = "local"

    juego.bind(text=actualizar_opciones)

    def apostar(_):
      try:
        monto = int(apuesta.text)
      except ValueError:
        resultado_label.text = "Ingresá un monto válido."
        return
      casino = app.carrera.casino
      if juego.text == "Ruleta":
        resultado = casino.jugar_ruleta(app.carrera.jugador, monto, eleccion.text)
      elif juego.text == "Tragamonedas":
        resultado = casino.jugar_tragamonedas(app.carrera.jugador, monto)
      elif juego.text == "Carrera de caballos":
        resultado = casino.jugar_carrera_caballos(app.carrera.jugador, monto, eleccion.text)
      else:
        partido = mapa_partidos.get(partido_spinner.text)
        if partido is None:
          resultado = {"ok": False, "mensaje": "No hay un partido disponible para apostar."}
        else:
          valor_local = max(1, getattr(partido.local, "valoracion", 50))
          valor_visitante = max(1, getattr(partido.visitante, "valoracion", 50))
          total = valor_local + valor_visitante
          if eleccion.text == "local":
            prob = 0.88 * valor_local / total
          elif eleccion.text == "visitante":
            prob = 0.88 * valor_visitante / total
          else:
            prob = 0.12
          resultado = casino.apostar_partido(app.carrera.jugador, monto, eleccion.text, prob, partido=partido)
      resultado_label.text = resultado["mensaje"] + (f"\nResultado neto: ${resultado['neto']:+,}\nSaldo: ${resultado['dinero']:,}" if resultado["ok"] else "")
      self.actualizar()

    boton = Button(text="APOSTAR", size_hint_y=None, height=46)
    boton.bind(on_press=apostar)
    contenido.add_widget(boton)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def ver_personalizacion(self, *_):
    """Selector de retratos reales: no muestra un avatar geométrico que no coincide con la foto."""
    app = App.get_running_app()
    jugador = app.carrera.jugador
    opciones = [
      ("Modelo 1", "assets/players/retrato_1.png"),
      ("Modelo 2", "assets/players/retrato_2.png"),
      ("Modelo 3", "assets/players/retrato_3.png"),
      ("Modelo 4", "assets/players/retrato_4.png"),
    ]
    contenido = BoxLayout(orientation="vertical", padding=10, spacing=8)
    ruta_actual = jugador.apariencia.get("retrato", opciones[0][1])
    if not os.path.exists(ruta_actual):
      ruta_actual = opciones[0][1]
    contenido.add_widget(Label(text="RETRATO DEL FUTBOLISTA", size_hint_y=None, height=28, font_size=16, bold=True))
    imagen_actual = Image(source=ruta_actual, size_hint_y=None, height=230, fit_mode="contain")
    contenido.add_widget(imagen_actual)
    contenido.add_widget(Label(text="Elegí un modelo distinto. La foto cambia de verdad; no usamos una cara dibujada encima.", size_hint_y=None, height=42, font_size=12))
    fila = GridLayout(cols=4, spacing=7, size_hint_y=None, height=150)
    popup = Popup(title="Cambiar retrato", content=contenido, size_hint=(0.92, 0.88))
    for etiqueta, ruta in opciones:
      tarjeta = BoxLayout(orientation="vertical", spacing=4, padding=4)
      tarjeta.add_widget(Image(source=ruta, fit_mode="contain"))
      boton = Button(text=etiqueta, size_hint_y=None, height=36, font_size=11)
      def seleccionar(_btn, path=ruta):
        jugador.apariencia["retrato"] = path
        imagen_actual.source = path
        imagen_actual.reload()
        self.actualizar()
      boton.bind(on_press=seleccionar)
      tarjeta.add_widget(boton)
      fila.add_widget(tarjeta)
    contenido.add_widget(fila)
    cerrar = Button(text="LISTO", size_hint_y=None, height=42)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def guardar_apariencia(self, spinners, popup):
    app = App.get_running_app()
    for atributo, spinner in spinners.items():
      app.carrera.personalizar(atributo, spinner.text)
    popup.dismiss()
    self.actualizar()
    app.mostrar_mensaje("Apariencia guardada.")

  def comprar_tatuaje(self, popup):
    app = App.get_running_app()
    ok = app.carrera.comprar_tatuaje("Tatuaje genérico", 25000)
    popup.dismiss()
    self.actualizar()
    app.mostrar_mensaje("Tatuaje desbloqueado." if ok else "No tenés dinero suficiente o ya tenés ese tatuaje.")

  def ver_retiro(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(
      text=(
        f"Edad actual: {jugador.edad}\n"
        f"Edad prevista de retiro: {jugador.edad_retiro}\n"
        "Cuando alcances la edad de retiro, podés pagar para extender la carrera."
      )
    ))
    popup = Popup(title="Retiro profesional", content=contenido, size_hint=(0.8, 0.5))
    extender = Button(text="Extender una temporada", size_hint_y=None, height=46)
    extender.bind(on_press=lambda *_: self.confirmar_extension(popup))
    contenido.add_widget(extender)
    retirarse = Button(text="Retirarme", size_hint_y=None, height=46)
    retirarse.bind(on_press=lambda *_: self.confirmar_retiro(popup))
    contenido.add_widget(retirarse)
    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def confirmar_extension(self, popup):
    app = App.get_running_app()
    popup.dismiss()
    resultado = app.carrera.extender_carrera()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def confirmar_retiro(self, popup):
    app = App.get_running_app()
    popup.dismiss()
    resultado = app.carrera.retirarse()
    app.mostrar_mensaje(resultado["mensaje"])
    self.actualizar()

  def ver_perfil(self, *_):
    """Muestra un resumen compacto; el perfil principal ya está visible en la cabecera."""
    self.actualizar()
    self.mensaje.text = "Este es tu perfil: foto, club, valoración, forma, dinero y contrato aparecen arriba."

  def ver_logros(self, *_):
    jugador = App.get_running_app().carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    logros = sorted(jugador.logros)
    contenido.add_widget(Label(
      text=f"LOGROS DESBLOQUEADOS: {len(logros)}\n" + ("\n".join(f"• {logro}" for logro in logros) if logros else "Todavía no desbloqueaste logros."),
      halign="left", valign="top"
    ))
    popup = Popup(title="Logros", content=contenido, size_hint=(0.78, 0.65))
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def ver_vinculos(self, *_):
    jugador = App.get_running_app().carrera.jugador
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    filas = [f"{nombre.replace('_', ' ').title()}: {nivel}/100" for nombre, nivel in jugador.vinculos.items()]
    contenido.add_widget(Label(
      text="RELACIONES DE TU CARRERA\n\n" + "\n".join(filas) + f"\n\nPareja: {jugador.pareja or 'Sin pareja'}" + (f" ({jugador.pareja_genero}) · Estado: {jugador.estado_relacion}" if jugador.pareja else "") + f"\nHijos: {len(jugador.hijos)}",
      halign="left", valign="top"
    ))
    popup = Popup(title="Mis vínculos", content=contenido, size_hint=(0.78, 0.65))
    cerrar = Button(text="Cerrar", size_hint_y=None, height=42)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def charlar_presidente(self, *_):
    app = App.get_running_app()
    carrera = app.carrera
    jugador = carrera.jugador
    if jugador.equipo is None:
      app.mostrar_mensaje("Todavía no tenés club: las charlas con la dirigencia se habilitan después de firmar un contrato. Mientras tanto, revisá las ofertas disponibles.")
      return
    contrato = jugador.contrato
    semanas = contrato.semanas_restantes if contrato is not None and contrato.esta_vigente() else 0
    if carrera.semanas_desde_charla_presidente < 4:
      app.mostrar_mensaje("Ya hablaste con la dirigencia hace poco. Volvé a intentarlo dentro de unas semanas.")
      return
    saludo = carrera.temporada.sistema_vida_social.hablar_con_presidente(jugador)["saludo"]
    carrera.semanas_desde_charla_presidente = 0
    nombre_club = jugador.equipo.nombre if jugador.equipo is not None else "Sin club (visita a la oficina de representación)"
    texto = (
      f"{saludo}\n\n"
      f"Situación: {nombre_club}.\n\n"
      f"Relación con el club: {jugador.vinculos.get('club', 50)}/100\n"
      f"Relación con el gerente: {jugador.vinculos.get('gerente', 50)}/100\n"
      f"Contrato vigente: {'Sí' if semanas else 'No'}\n"
      f"Semanas restantes: {semanas}\n\n"
      f"{'Podés revisar tu contrato o consultar el mercado de pases.' if jugador.equipo is not None else 'Todavía no tenés club. Podés revisar las ofertas contractuales y avanzar semanas para recibir nuevas oportunidades.'}"
    )
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    contenido.add_widget(Label(text=texto, halign="left", valign="middle"))
    popup = Popup(title="Charla con el presidente", content=contenido, size_hint=(0.82, 0.62))
    contrato_btn = Button(text="Ver situación contractual", size_hint_y=None, height=42)
    contrato_btn.bind(on_press=lambda *_: (popup.dismiss(), self.ver_contrato()))
    mercado_btn = Button(text="Consultar mercado de pases", size_hint_y=None, height=42)
    mercado_btn.bind(on_press=lambda *_: (popup.dismiss(), self.ver_mercado()))
    cerrar = Button(text="Cerrar", size_hint_y=None, height=40)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(contrato_btn)
    contenido.add_widget(mercado_btn)
    contenido.add_widget(cerrar)
    popup.open()

  def ver_mercado(self, *_):
    app = App.get_running_app()
    jugador = app.carrera.jugador
    mercado = app.carrera.temporada.mercado_pases
    ofertas = [
      oferta for oferta in mercado.obtener_ofertas_pendientes()
      if oferta.jugador is jugador
    ]

    contenido = BoxLayout(orientation="vertical", padding=10, spacing=7)
    if not jugador.en_lista_transferibles:
      contenido.add_widget(Label(
        text="No estás en la lista de transferibles. Podés solicitarlo desde Situación contractual.",
        size_hint_y=None,
        height=70
      ))
    if not ofertas:
      contenido.add_widget(Label(
        text="No hay ofertas pendientes. Las ofertas de clubes pueden aparecer durante las ventanas de mercado.",
        size_hint_y=None,
        height=70
      ))

    popup = Popup(title="Mercado de pases", content=contenido, size_hint=(0.85, 0.8))
    for oferta in ofertas:
      boton = Button(
        text=(
          f"{oferta.comprador.nombre} ofrece ${oferta.monto}\n"
          f"Salario: ${oferta.salario_semanal}/semana"
        ),
        size_hint_y=None,
        height=65
      )
      boton.bind(on_press=lambda _, o=oferta: self.aceptar_oferta_usuario(o, popup))
      contenido.add_widget(boton)

    cerrar = Button(text="Cerrar", size_hint_y=None, height=38)
    cerrar.bind(on_press=popup.dismiss)
    contenido.add_widget(cerrar)
    popup.open()

  def aceptar_oferta_usuario(self, oferta, popup):
    app = App.get_running_app()
    ok = oferta.aceptar()
    popup.dismiss()
    app.mostrar_mensaje(
      f"Transferencia concretada a {oferta.comprador.nombre}." if ok
      else "No se pudo concretar la transferencia."
    )
    self.actualizar()

  def volver(self, *_):
    App.get_running_app().mostrar_pantalla("menu")


class PantallaPartido(Screen):
  """Partido en vivo con alineación fija, cronología y decisiones contextuales."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.raiz = BoxLayout(orientation="vertical", padding=8, spacing=7)
    with self.raiz.canvas.before:
      Color(0.025, 0.045, 0.075, 1)
      self._fondo_partido = Rectangle(pos=self.raiz.pos, size=self.raiz.size)
    self.raiz.bind(pos=lambda w, v: setattr(self._fondo_partido, "pos", v), size=lambda w, v: setattr(self._fondo_partido, "size", v))

    cabecera = BoxLayout(size_hint_y=None, height=34, spacing=6)
    cabecera.add_widget(Label(text="PARTIDO EN VIVO", font_size=16, bold=True, color=(0.96, 0.78, 0.34, 1), halign="left"))
    cabecera.add_widget(Label(text="FOOTBALL CAREER", font_size=11, color=(0.65, 0.75, 0.84, 1), halign="right"))
    boton_musica = Button(text="MÚSICA", size_hint_x=None, width=68, font_size=10)
    boton_musica.bind(on_press=lambda *_: App.get_running_app().alternar_musica())
    cabecera.add_widget(boton_musica)
    boton_efectos = Button(text="EFECTOS", size_hint_x=None, width=68, font_size=10)
    boton_efectos.bind(on_press=lambda *_: App.get_running_app().alternar_efectos())
    cabecera.add_widget(boton_efectos)
    volumen = Button(text="VOL.", size_hint_x=None, width=50, font_size=10)
    volumen.bind(on_press=lambda *_: App.get_running_app().abrir_configuracion_audio())
    cabecera.add_widget(volumen)
    self.raiz.add_widget(cabecera)

    panel_marcador = TarjetaPremium(orientation="vertical", padding=8, spacing=1, size_hint_y=None, height=82, fondo=(0.075, 0.13, 0.19, 1))
    self.marcador = Label(text="", size_hint_y=None, height=48, font_size=21, bold=True, color=(1, 1, 1, 1))
    panel_marcador.add_widget(self.marcador)
    self.disciplina = BoxLayout(orientation="horizontal", size_hint_y=None, height=26, spacing=14)
    self.contador_goles = self._crear_contador_evento("assets/ui/eventos/gol.png", "0 GOLES")
    self.contador_amarillas = self._crear_contador_evento("assets/ui/eventos/amarilla.png", "0 AMARILLAS")
    self.contador_rojas = self._crear_contador_evento("assets/ui/eventos/roja.png", "0 ROJAS")
    self.disciplina.add_widget(self.contador_goles)
    self.disciplina.add_widget(self.contador_amarillas)
    self.disciplina.add_widget(self.contador_rojas)
    panel_marcador.add_widget(self.disciplina)
    self.raiz.add_widget(panel_marcador)

    # Zona central de partido: el evento y el duelo ocupan el foco visual.
    zona_central = BoxLayout(orientation="horizontal", spacing=8)
    panel_izq = TarjetaPremium(orientation="vertical", padding=8, spacing=4, size_hint_x=0.24, fondo=(0.045, 0.075, 0.10, 1))
    panel_izq.add_widget(Label(text="PLANTEL DEL PARTIDO", size_hint_y=None, height=28, bold=True, color=(0.43, 0.94, 0.61, 1), font_size=14))
    self.vista_plantel = "titulares"
    selector_plantel = BoxLayout(size_hint_y=None, height=38, spacing=4)
    self.boton_titulares = Button(text="11 TITULARES", font_size=11)
    self.boton_suplentes = Button(text="SUPLENTES", font_size=11)
    self.boton_titulares.bind(on_press=lambda *_: self._cambiar_vista_plantel("titulares"))
    self.boton_suplentes.bind(on_press=lambda *_: self._cambiar_vista_plantel("suplentes"))
    selector_plantel.add_widget(self.boton_titulares)
    selector_plantel.add_widget(self.boton_suplentes)
    panel_izq.add_widget(selector_plantel)
    self.alineacion = GridLayout(cols=1, spacing=2, size_hint_y=None)
    self.alineacion.bind(minimum_height=self.alineacion.setter("height"))
    scroll_alineacion = ScrollView(do_scroll_x=False, bar_width=4)
    scroll_alineacion.add_widget(self.alineacion)
    panel_izq.add_widget(scroll_alineacion)
    zona_central.add_widget(panel_izq)

    panel_evento = TarjetaPremium(orientation="vertical", padding=9, spacing=7, size_hint_x=0.48, fondo=(0.045, 0.075, 0.10, 1))
    self.comentarista = Label(text="EL ÁRBITRO AUTORIZA EL INICIO DEL ENCUENTRO", size_hint_y=None, height=58, halign="center", valign="middle", color=(1, 0.78, 0.32, 1), bold=True, font_size=14)
    self.comentarista.bind(size=lambda w, value: setattr(w, "text_size", (value[0] - 12, value[1] - 4)))
    panel_evento.add_widget(self.comentarista)
    self.estado_jugada = Label(text="Preparando el partido...", size_hint_y=None, height=82, halign="center", valign="middle", color=(0.95, 0.97, 1, 1), font_size=13)
    self.estado_jugada.bind(size=lambda w, value: setattr(w, "text_size", (value[0] - 12, value[1] - 4)))
    panel_evento.add_widget(self.estado_jugada)
    self.duelo_visual = TarjetaPremium(orientation="horizontal", padding=7, spacing=6, size_hint_y=None, height=0, fondo=(0.025, 0.05, 0.075, 1))
    panel_evento.add_widget(self.duelo_visual)
    self.botones_accion = GridLayout(cols=3, spacing=6, size_hint_y=None, height=150)
    self.botones_accion.bind(pos=self._dibujar_arco, size=self._dibujar_arco)
    panel_evento.add_widget(self.botones_accion)
    zona_central.add_widget(panel_evento)

    panel_derecho = TarjetaPremium(orientation="vertical", padding=8, spacing=4, size_hint_x=0.28, fondo=(0.045, 0.075, 0.10, 1))
    panel_derecho.add_widget(Label(text="CRONOLOGÍA", size_hint_y=None, height=28, bold=True, color=(0.43, 0.94, 0.61, 1)))
    self.eventos = Label(text="Esperando el inicio...", halign="left", valign="top", size_hint_y=None)
    self.eventos.bind(width=lambda w, value: setattr(w, "text_size", (value, None)))
    self.eventos.bind(texture_size=lambda w, value: setattr(w, "height", value[1] + 8))
    scroll_eventos = ScrollView(do_scroll_x=False, bar_width=4)
    scroll_eventos.add_widget(self.eventos)
    panel_derecho.add_widget(scroll_eventos)
    zona_central.add_widget(panel_derecho)
    self.raiz.add_widget(zona_central)

    control = BoxLayout(size_hint_y=None, height=38, spacing=6)
    control.add_widget(Label(text="VELOCIDAD", size_hint_x=0.24, color=(0.70, 0.80, 0.88, 1)))
    self.velocidad = Spinner(text="Normal", values=("Lenta", "Normal", "Rápida"), size_hint_x=0.76)
    control.add_widget(self.velocidad)
    self.raiz.add_widget(control)
    self.boton_avanzar = Button(text="EL TIEMPO AVANZA AUTOMÁTICAMENTE", size_hint_y=None, height=28, disabled=True)
    self.raiz.add_widget(self.boton_avanzar)
    volver = Button(text="VOLVER A LA CARRERA (PAUSAR)", size_hint_y=None, height=34)
    volver.bind(on_press=self.pausar_y_volver)
    self.raiz.add_widget(volver)
    self.add_widget(self.raiz)
    self.partido = None
    self.decision_pendiente = False
    self.reloj_evento = None
    self.situacion_actual = None
    self.ultimo_minuto_situacion = -10
    self.vista_plantel = "titulares"
    self._arco_activo = False
    self.alineaciones_partido = {}

  def _crear_contador_evento(self, ruta, texto):
    bloque = BoxLayout(orientation="horizontal", spacing=5, size_hint_x=None, width=135)
    bloque.add_widget(Image(source=ruta, size_hint_x=None, width=23, fit_mode="contain"))
    etiqueta = Label(text=texto, font_size=11, color=(0.82, 0.88, 0.93, 1), halign="left")
    etiqueta.bind(size=lambda w, value: setattr(w, "text_size", value))
    bloque.add_widget(etiqueta)
    bloque.etiqueta = etiqueta
    return bloque

  def _dibujar_arco(self, *_):
    """Muestra un arco ilustrado con red y nueve zonas, no una cuadrícula vacía."""
    canvas = self.botones_accion.canvas.before
    canvas.clear()
    if not getattr(self, "_arco_activo", False):
      return
    ruta = "assets/ui/arco_zonas.png"
    if not os.path.exists(ruta):
      return
    textura = CoreImage(ruta).texture
    x, y = self.botones_accion.pos
    w, h = self.botones_accion.size
    with canvas:
      Color(1, 1, 1, 1)
      Rectangle(texture=textura, pos=(x, y), size=(w, h))

  def _activar_arco(self, activo=True):
    self._arco_activo = activo
    self._dibujar_arco()

  def pausar_y_volver(self, *_):
    """Pausa el reloj del encuentro y vuelve a la carrera sin perder el partido."""
    self._detener_reloj()
    app = App.get_running_app()
    if hasattr(app, "mostrar_pantalla"):
      app.mostrar_pantalla("carrera")
    elif hasattr(app, "pantallas"):
      app.pantallas.current = "carrera"

  def on_pre_enter(self, *_):
    self._detener_reloj()
    app = App.get_running_app()
    self.partido = getattr(app, "partido_actual", None)
    self.botones_accion.clear_widgets()
    self.duelo_visual.clear_widgets()
    self.duelo_visual.height = 0
    self.decision_pendiente = False
    self.situacion_actual = None
    self.ultimo_minuto_situacion = -10
    self.comentarista.text = "EL ÁRBITRO AUTORIZA EL INICIO DEL ENCUENTRO"
    self.estado_jugada.text = "Preparando el partido..."
    self.alineaciones_partido = {}
    if self.partido is None:
      self.estado_jugada.text = "No hay un partido cargado. Volvé a la carrera y elegí el próximo encuentro."
      return
    if self.partido.estado == "terminado":
      self.estado_jugada.text = "Este partido ya terminó. Procesá la semana desde el resumen."
      self._actualizar()
      return
    if self.partido.estado == "pendiente":
      self.partido.jugador_controlado = app.carrera.jugador
      self.partido.iniciar()
    self.estado_jugada.text = "El reloj avanza solo. Las jugadas de tu futbolista detienen el partido para que decidas."
    self._actualizar()
    self._iniciar_reloj()

  def on_leave(self, *_):
    self._detener_reloj()

  def _detener_reloj(self):
    if self.reloj_evento is not None:
      self.reloj_evento.cancel()
      self.reloj_evento = None

  def _iniciar_reloj(self):
    self._detener_reloj()
    if self.partido is not None and self.partido.estado != "terminado" and not self.decision_pendiente:
      self.reloj_evento = Clock.schedule_once(self._tick, self._segundos_por_minuto())

  def _segundos_por_minuto(self):
    return {"Lenta": 0.80, "Normal": 0.42, "Rápida": 0.20}.get(self.velocidad.text, 0.42)

  def _tick(self, _dt):
    self.reloj_evento = None
    p = self.partido
    if p is None or p.estado == "terminado" or self.decision_pendiente:
      return False
    antes = p.minuto
    resultado = p.avanzar_intervalo(1)
    self._actualizar()
    if resultado.get("terminado"):
      self._detener_reloj()
      self._mostrar_final()
      return False
    if p.minuto > antes:
      self._posible_situacion()
    if not self.decision_pendiente and p.estado != "terminado":
      self.reloj_evento = Clock.schedule_once(self._tick, self._segundos_por_minuto())
    return False

  def _actualizar(self):
    p = self.partido
    if p is None:
      return
    p.calcular_resultado()
    self.marcador.text = f"{p.local.nombre}  {p.resultado[0]} - {p.resultado[1]}  {p.visitante.nombre}\nMINUTO {p.minuto}'"
    amarillas = len(p.amonestados)
    rojas = sum(1 for evento in p.eventos if evento.get("tipo") == "roja")
    self.contador_goles.etiqueta.text = f"{len(p.goles_local) + len(p.goles_visitante)} GOLES"
    self.contador_amarillas.etiqueta.text = f"{amarillas} AMARILLAS"
    self.contador_rojas.etiqueta.text = f"{rojas} ROJAS"
    self._actualizar_alineacion()
    lineas = []
    for gol in p.goles_local:
      lineas.append((gol.get("minuto", 0), f"[GOL] {gol.get('minuto', 0)}' {gol['jugador'].nombre} · {p.local.nombre}"))
    for gol in p.goles_visitante:
      lineas.append((gol.get("minuto", 0), f"[GOL] {gol.get('minuto', 0)}' {gol['jugador'].nombre} · {p.visitante.nombre}"))
    for asistencia in p.asistencias:
      lineas.append((asistencia.get("minuto", 0), f"[ASISTENCIA] {asistencia.get('minuto', 0)}' {asistencia['jugador'].nombre}"))
    for tarjeta in p.amonestados:
      jugador_tarjeta = tarjeta["jugador"]
      equipo_tarjeta = p.local if jugador_tarjeta in getattr(p.local, "jugadores", []) else p.visitante
      lineas.append((tarjeta.get("minuto", 0), f"[AMARILLA] {tarjeta.get('minuto', 0)}' {jugador_tarjeta.nombre} · {equipo_tarjeta.nombre}"))
    for evento in p.eventos:
      if evento.get("tipo") == "roja":
        jugador_roja = evento.get("jugador")
        equipo_roja = p.local if jugador_roja in getattr(p.local, "jugadores", []) else p.visitante
        lineas.append((evento.get("minuto", 0), f"[ROJA] {evento.get('minuto', 0)}' {jugador_roja.nombre} · {equipo_roja.nombre}"))
      elif evento.get("tipo") in ("decision_jugador", "penal", "tiro_libre", "corner") and evento.get("mensaje"):
        etiqueta_evento = {"penal": "[PENAL]", "tiro_libre": "[TIRO LIBRE]", "corner": "[CORNER]", "decision_jugador": "[JUGADA]"}.get(evento.get("tipo"), "[EVENTO]")
        lineas.append((evento.get("minuto", 0), f"{etiqueta_evento} {evento.get('minuto', 0)}' · {evento['mensaje']}"))
    lineas.sort(key=lambda item: item[0])
    self.eventos.text = "\n".join(texto for _, texto in lineas[-28:]) or "El partido está en juego. Esperando la primera acción..."

  def _cambiar_vista_plantel(self, vista):
    self.vista_plantel = vista
    self._actualizar_alineacion()

  def _once_equilibrado(self, equipo, controlado):
    jugadores = [j for j in equipo.jugadores if j.esta_disponible() and not getattr(j, "expulsado", False)]
    porteros = [j for j in jugadores if j.obtener_posicion_normalizada() == "arquero"]
    defensores = [j for j in jugadores if j.obtener_posicion_normalizada() == "defensor"]
    medios = [j for j in jugadores if j.obtener_posicion_normalizada() == "mediocampista"]
    delanteros = [j for j in jugadores if j.obtener_posicion_normalizada() == "delantero"]
    otros = [j for j in jugadores if j not in porteros + defensores + medios + delanteros]
    once = []
    if porteros:
      once.append(max(porteros, key=lambda j: getattr(j, "valoracion", 0)))
    for grupo, cantidad in ((defensores, 4), (medios, 3), (delanteros, 3)):
      ordenados = sorted(grupo, key=lambda j: getattr(j, "valoracion", 0), reverse=True)
      once.extend([j for j in ordenados if j not in once][:cantidad])
    candidatos = sorted(otros + defensores + medios + delanteros + porteros, key=lambda j: getattr(j, "valoracion", 0), reverse=True)
    for j in candidatos:
      if len(once) >= 11:
        break
      if j not in once:
        once.append(j)
    if controlado in jugadores and controlado not in once:
      reemplazo = next((j for j in reversed(once) if j is not (once[0] if once else None) and j.obtener_posicion_normalizada() != "arquero"), None)
      if reemplazo:
        once[once.index(reemplazo)] = controlado
      elif len(once) < 11:
        once.append(controlado)
    return once[:11]

  def _actualizar_alineacion(self):
    self.alineacion.clear_widgets()
    p = self.partido
    if p is None:
      return
    controlado = App.get_running_app().carrera.jugador
    self.boton_titulares.background_color = (0.15, 0.48, 0.32, 1) if self.vista_plantel == "titulares" else (0.13, 0.17, 0.23, 1)
    self.boton_suplentes.background_color = (0.15, 0.48, 0.32, 1) if self.vista_plantel == "suplentes" else (0.13, 0.17, 0.23, 1)
    for equipo in (p.local, p.visitante):
      clave_equipo = id(equipo)
      if clave_equipo not in self.alineaciones_partido:
        self.alineaciones_partido[clave_equipo] = self._once_equilibrado(equipo, controlado if controlado in equipo.jugadores else None)
      once = self.alineaciones_partido[clave_equipo]
      suplentes = [j for j in equipo.jugadores if j not in once and not getattr(j, "expulsado", False)]
      encabezado = Label(text=f"[b]{equipo.nombre}[/b]", markup=True, size_hint_y=None, height=26, halign="left", font_size=13)
      encabezado.bind(size=lambda w, value: setattr(w, "text_size", value))
      self.alineacion.add_widget(encabezado)
      jugadores_vista = once if self.vista_plantel == "titulares" else sorted(suplentes, key=lambda j: getattr(j, "valoracion", 0), reverse=True)
      for indice, jugador in enumerate(jugadores_vista):
        simbolos = []
        if any(g.get("jugador") is jugador for g in p.goles_local + p.goles_visitante): simbolos.append("[GOL]")
        if any(a.get("jugador") is jugador for a in p.asistencias): simbolos.append("[AS]")
        if any(t.get("jugador") is jugador for t in p.amonestados): simbolos.append("[TA]")
        if any(e.get("tipo") == "roja" and e.get("jugador") is jugador for e in p.eventos): simbolos.append("[TR]")
        if any(e.get("tipo") in ("cambio", "sustitucion") and (e.get("jugador") is jugador or e.get("sale") is jugador or e.get("entra") is jugador) for e in p.eventos): simbolos.append("[CAMBIO]")
        posicion = getattr(jugador, "posicion", "?").upper()
        nombre = jugador.nombre if len(jugador.nombre) <= 15 else jugador.nombre[:13] + "…"
        prefijo = "▶" if jugador is controlado else str(indice + 1)
        texto = f"{prefijo}  {posicion[:3]}  {nombre}  {getattr(jugador, 'valoracion', 0)} {' '.join(simbolos)}"
        tarjeta = Label(text=texto, size_hint_y=None, height=29, font_size=11, halign="left", valign="middle")
        tarjeta.bind(size=lambda w, value: setattr(w, "text_size", value))
        self.alineacion.add_widget(tarjeta)
      self.alineacion.add_widget(Label(text=f"DT: {getattr(equipo, 'dt', 'Sin entrenador')} · {len(once)} titulares / {len(suplentes)} suplentes", size_hint_y=None, height=28, font_size=10, color=(0.98, 0.77, 0.34, 1), halign="left"))

  def _posible_situacion(self):
    p = self.partido
    app = App.get_running_app()
    jugador = app.carrera.jugador
    if p is None or p.estado != "en juego" or jugador.equipo not in (p.local, p.visitante):
      return
    if p.minuto - self.ultimo_minuto_situacion < 5:
      return
    if random.random() < 0.0025:
      self.ultimo_minuto_situacion = p.minuto
      self._pedir_penal()
      return
    if random.random() < 0.006:
      self.ultimo_minuto_situacion = p.minuto
      self._pedir_tiro_libre()
      return
    if random.random() < 0.009:
      self.ultimo_minuto_situacion = p.minuto
      self._pedir_corner()
      return
    if random.random() < 0.045:
      self.ultimo_minuto_situacion = p.minuto
      self._pedir_duelo_individual()

  def _pedir_duelo_individual(self):
    p = self.partido
    jugador = App.get_running_app().carrera.jugador
    rival_equipo = p.visitante if jugador.equipo == p.local else p.local
    rivales = p.obtener_jugadores_disponibles(rival_equipo)
    rival = random.choice(rivales) if rivales else None
    atacante = random.random() < 0.62 if jugador.obtener_posicion_normalizada() != "defensor" else random.random() < 0.30
    self.situacion_actual = {"tipo": "ataque" if atacante else "defensa", "rival": rival}
    self.decision_pendiente = True
    self._detener_reloj()
    self.botones_accion.clear_widgets()
    valor_jugador = getattr(jugador, "valoracion", 70)
    valor_rival = getattr(rival, "valoracion", 70) if rival is not None else 70
    probabilidad = max(18, min(88, round(50 + (valor_jugador - valor_rival) * 1.15)))
    nombre_rival = rival.nombre.upper() if rival is not None else "RIVAL"
    duelo_texto = f"{jugador.nombre.upper()}  ·  VAL {valor_jugador}\nVS\n{nombre_rival}  ·  VAL {valor_rival}"
    self.duelo_visual.clear_widgets()
    self.duelo_visual.height = 108
    for nombre, valor, resaltado, jugador_duelo in [
      (jugador.nombre, valor_jugador, True, jugador),
      (nombre_rival, valor_rival, False, rival),
    ]:
      tarjeta = TarjetaPremium(orientation="vertical", spacing=3, padding=6,
        size_hint_x=0.46,
        fondo=(0.075, 0.12, 0.15, 1) if resaltado else (0.13, 0.09, 0.10, 1))
      tarjeta.add_widget(Label(text="TU FUTBOLISTA" if resaltado else "RIVAL",
        size_hint_y=None, height=17, font_size=9, color=(0.35, 0.96, 0.61, 1) if resaltado else (1, 0.65, 0.52, 1)))
      tarjeta.add_widget(Label(text=nombre.upper(), font_size=12, bold=True,
        color=(0.96, 0.97, 1, 1), halign="center"))
      tarjeta.add_widget(Label(text=f"VAL {valor}", font_size=15, bold=True,
        color=(0.35, 0.96, 0.61, 1) if resaltado else (1, 0.75, 0.45, 1)))
      if jugador_duelo is not None:
        clave = "regate" if resaltado and atacante else ("pase" if resaltado else "marca")
        stat = getattr(jugador_duelo, "estadisticas", {}).get(clave, valor)
        tarjeta.add_widget(Label(text=f"{clave.upper()} {stat}", size_hint_y=None, height=16,
          font_size=10, color=(0.72, 0.80, 0.87, 1)))
      self.duelo_visual.add_widget(tarjeta)
      if resaltado:
        self.duelo_visual.add_widget(Label(text="VS", size_hint_x=0.12, bold=True,
          font_size=16, color=(0.96, 0.76, 0.30, 1)))
    self._activar_arco(False)
    if atacante:
      tipo_jugada = random.choice(("gambeta", "pase", "remate"))
      self.situacion_actual["subtipo"] = tipo_jugada
      if tipo_jugada == "gambeta":
        self.comentarista.text = f"{jugador.nombre.upper()} RECIBE POR LA BANDA. EL DEFENSOR SALE A MARCARLO."
        self.estado_jugada.text = f"{p.minuto}' · GAMBETEO INDIVIDUAL\nElegí hacia dónde intentás superar al rival.\nÉXITO ESTIMADO: {probabilidad}%"
        acciones = [("IZQUIERDA", "encarar", "izquierda"), ("CENTRO", "encarar", "centro"), ("DERECHA", "encarar", "derecha")]
      elif tipo_jugada == "pase":
        self.comentarista.text = f"{jugador.nombre.upper()} LEVANTA LA CABEZA Y BUSCA UN COMPAÑERO."
        self.estado_jugada.text = f"{p.minuto}' · DECISIÓN DE PASE\nElegí el tipo de entrega; un pase bueno puede crear una ocasión.\nÉXITO ESTIMADO: {probabilidad}%"
        acciones = [("AL PIE", "pasar", "al_pie"), ("AL ESPACIO", "pasar", "al_espacio"), ("PARED", "pasar", "pared")]
      else:
        self.comentarista.text = f"¡{jugador.nombre.upper()} PERFILADO PARA REMATAR!"
        self.estado_jugada.text = f"{p.minuto}' · OCASIÓN DE REMATE\nElegí la zona del arco. La elección y tus atributos afectan la definición.\nÉXITO ESTIMADO: {probabilidad}%"
        self._activar_arco(True)
        acciones = [("", "rematar", "abajo_izquierda"), ("", "rematar", "abajo_centro"), ("", "rematar", "abajo_derecha"), ("", "rematar", "centro_izquierda"), ("", "rematar", "centro"), ("", "rematar", "centro_derecha"), ("", "rematar", "arriba_izquierda"), ("", "rematar", "arriba_centro"), ("", "rematar", "arriba_derecha")]
    else:
      self.comentarista.text = f"EL RIVAL AVANZA. {jugador.nombre.upper()} DEBE CERRARLE EL CAMINO."
      self.estado_jugada.text = f"{p.minuto}' · DUELO DEFENSIVO\nElegí cómo responder al atacante.\nÉXITO ESTIMADO: {probabilidad}%"
      acciones = [("ENTRAR", "presionar", "agresivo"), ("INTERCEPTAR", "interceptar", "línea_pase"), ("CONTENER", "contener", "posicion")]
    self.botones_accion.cols = 3
    self.botones_accion.height = 260 if getattr(self, "_arco_activo", False) else 150
    for etiqueta, accion, direccion in acciones:
      sobre_arco = getattr(self, "_arco_activo", False) and etiqueta == ""
      boton = BotonPremium(text=etiqueta, font_size=12, size_hint_y=None, height=44,
        background_color=(0.03, 0.12, 0.09, 0.04) if sobre_arco else (0.20, 0.88, 0.43, 1),
        color=(1, 1, 1, 0) if sobre_arco else (0.035, 0.07, 0.09, 1))
      boton.bind(on_press=lambda _, a=accion, d=direccion: self.elegir_accion(a, d))
      self.botones_accion.add_widget(boton)

  def _pedir_penal(self):
    self._activar_arco(True)
    self.duelo_visual.clear_widgets()
    self.duelo_visual.height = 0
    self.decision_pendiente = True
    self.situacion_actual = {"tipo": "penal"}
    self._detener_reloj()
    self.botones_accion.clear_widgets()
    self.botones_accion.cols = 3
    self.botones_accion.height = 260
    self.botones_accion.cols = 3
    equipo = App.get_running_app().carrera.jugador.equipo
    self.comentarista.text = f"¡PENAL PARA {equipo.nombre.upper()}! {App.get_running_app().carrera.jugador.nombre.upper()} TOMA DISTANCIA PARA REMATAR."
    self.estado_jugada.text = f"{self.partido.minuto}' · PENAL\nElegí directamente sobre una de las nueve zonas del arco.\nLa precisión, definición y el arquero influyen en el resultado."
    zonas_visuales = [("", "abajo_izquierda"), ("", "abajo_centro"), ("", "abajo_derecha"), ("", "medio_izquierda"), ("", "centro"), ("", "medio_derecha"), ("", "arriba_izquierda"), ("", "arriba_centro"), ("", "arriba_derecha")]
    for etiqueta, zona in zonas_visuales:
      boton = Button(text=etiqueta, font_size=10, background_normal="", background_down="", background_color=(0.03, 0.12, 0.09, 0.02), color=(1, 1, 1, 0))
      boton.bind(on_press=lambda _, z=zona: self.elegir_penal(z))
      self.botones_accion.add_widget(boton)

  def _pedir_tiro_libre(self):
    self._activar_arco(True)
    self.decision_pendiente = True
    self.situacion_actual = {"tipo": "tiro_libre"}
    self._detener_reloj()
    self.duelo_visual.clear_widgets()
    self.duelo_visual.height = 0
    self.botones_accion.clear_widgets()
    self.botones_accion.cols = 3
    self.botones_accion.height = 260
    self.botones_accion.cols = 3
    equipo = App.get_running_app().carrera.jugador.equipo
    self.comentarista.text = f"TIRO LIBRE PARA {equipo.nombre.upper()}. {App.get_running_app().carrera.jugador.nombre.upper()} SE PREPARA PARA EJECUTAR."
    self.estado_jugada.text = f"{self.partido.minuto}' · TIRO LIBRE\nElegí dirección y altura en el arco. La precisión y la barrera influyen en el remate."
    zonas_visuales = [("", "abajo_izquierda"), ("", "abajo_centro"), ("", "abajo_derecha"), ("", "medio_izquierda"), ("", "centro"), ("", "medio_derecha"), ("", "arriba_izquierda"), ("", "arriba_centro"), ("", "arriba_derecha")]
    for etiqueta, zona in zonas_visuales:
      boton = BotonPremium(text=etiqueta, font_size=11, size_hint_y=None, height=43, background_normal="", background_down="", background_color=(0.03, 0.12, 0.09, 0.02), color=(1, 1, 1, 0))
      boton.bind(on_press=lambda _, z=zona: self.elegir_tiro_libre(z))
      self.botones_accion.add_widget(boton)

  def _pedir_corner(self):
    self._activar_arco(False)
    self.decision_pendiente = True
    self.situacion_actual = {"tipo": "corner"}
    self._detener_reloj()
    self.duelo_visual.clear_widgets()
    self.duelo_visual.height = 0
    self.botones_accion.clear_widgets()
    self.botones_accion.cols = 3
    equipo = App.get_running_app().carrera.jugador.equipo
    self.comentarista.text = f"CÓRNER PARA {equipo.nombre.upper()}. ¿HABRÁ JUGADA PREPARADA DE {App.get_running_app().carrera.jugador.nombre.upper()}?"
    self.estado_jugada.text = f"{self.partido.minuto}' · CÓRNER\nElegí dónde colocar el centro para buscar a un compañero."
    for etiqueta, zona in [("PRIMER PALO", "primer_palo"), ("PUNTO PENAL", "centro"), ("SEGUNDO PALO", "segundo_palo")]:
      boton = BotonPremium(text=etiqueta, font_size=11, size_hint_y=None, height=46)
      boton.bind(on_press=lambda _, z=zona: self.elegir_corner(z))
      self.botones_accion.add_widget(boton)

  def elegir_tiro_libre(self, zona):
    App.get_running_app().reproducir_efecto("pelota")
    respuesta = self.partido.resolver_tiro_libre(App.get_running_app().carrera.jugador, zona)
    self._resolver_y_reanudar(respuesta)

  def elegir_corner(self, zona):
    App.get_running_app().reproducir_efecto("pelota")
    respuesta = self.partido.resolver_corner(App.get_running_app().carrera.jugador, zona)
    if respuesta.get("continuacion"):
      self.estado_jugada.text = respuesta.get("mensaje", "Centro conectado.")
      self.botones_accion.clear_widgets()
      self.botones_accion.cols = 2
      for etiqueta, accion in respuesta["continuacion"]:
        boton = BotonPremium(text=etiqueta, font_size=12, size_hint_y=None, height=46)
        boton.bind(on_press=lambda _, a=accion: self._resolver_continuacion(a))
        self.botones_accion.add_widget(boton)
      return
    self._resolver_y_reanudar(respuesta)

  def elegir_accion(self, accion, direccion=None):
    app = App.get_running_app()
    if accion in ("rematar", "pasar", "encarar", "presionar", "interceptar", "contener", "cabezazo"):
      app.reproducir_efecto("pelota")
    respuesta = self.partido.resolver_accion_controlada(accion, app.carrera.jugador, direccion=direccion)
    if respuesta.get("continuacion"):
      opciones = respuesta["continuacion"]
      self.estado_jugada.text = respuesta.get("mensaje", "¡Se abrió una ocasión!")
      if len(opciones) == 1:
        self._resolver_continuacion(opciones[0][1])
        return
      self.botones_accion.clear_widgets()
      self.botones_accion.cols = len(opciones)
      for etiqueta, siguiente in opciones:
        boton = BotonPremium(text=etiqueta, font_size=12, size_hint_y=None, height=48)
        boton.bind(on_press=lambda _, a=siguiente: self._resolver_continuacion(a))
        self.botones_accion.add_widget(boton)
      return
    self._resolver_y_reanudar(respuesta)

  def _resolver_continuacion(self, accion):
    # Una ocasión ganada no remata sola: el usuario todavía elige la zona del arco.
    App.get_running_app().reproducir_efecto("pelota")
    if accion in ("rematar", "cabezazo"):
      self._activar_arco(True)
      self.decision_pendiente = True
      self.situacion_actual = {"tipo": "remate_final", "accion": accion}
      self._detener_reloj()
      self.estado_jugada.text = f"{self.partido.minuto}' · OCASIÓN DE REMATE\nElegí una zona del arco para definir la jugada."
      self.comentarista.text = f"¡SE ABRIÓ EL ESPACIO! {App.get_running_app().carrera.jugador.nombre.upper()} PUEDE DEFINIR."
      self.botones_accion.clear_widgets()
      self.botones_accion.cols = 3
      self.botones_accion.height = 260
      zonas = [
        ("", "abajo_izquierda"), ("", "abajo_centro"), ("", "abajo_derecha"),
        ("", "medio_izquierda"), ("", "centro"), ("", "medio_derecha"),
        ("", "arriba_izquierda"), ("", "arriba_centro"), ("", "arriba_derecha")
      ]
      for etiqueta, zona in zonas:
        boton = Button(text="", background_normal="", background_down="", background_color=(0.03, 0.12, 0.09, 0.02), color=(1, 1, 1, 0))
        boton.bind(on_press=lambda _, z=zona, a=accion: self._resolver_y_reanudar(self.partido.resolver_accion_controlada(a, App.get_running_app().carrera.jugador, direccion=z)))
        self.botones_accion.add_widget(boton)
      return
    respuesta = self.partido.resolver_accion_controlada(accion, App.get_running_app().carrera.jugador)
    self._resolver_y_reanudar(respuesta)

  def elegir_penal(self, zona):
    App.get_running_app().reproducir_efecto("pelota")
    respuesta = self.partido.resolver_penal(App.get_running_app().carrera.jugador, zona)
    self._resolver_y_reanudar(respuesta)

  def _resolver_y_reanudar(self, respuesta):
    if not respuesta.get("ok"):
      self.estado_jugada.text = respuesta.get("mensaje", "No se pudo resolver la jugada.")
      return
    self.estado_jugada.text = respuesta.get("mensaje", "Jugada resuelta.")
    if "gol" in str(respuesta.get("mensaje", "")).lower():
      App.get_running_app().reproducir_efecto("gol")
    self._activar_arco(False)
    self.botones_accion.height = 150
    self.comentarista.text = respuesta.get("mensaje", "JUGADA RESUELTA").upper()[:110]
    self.decision_pendiente = False
    self.situacion_actual = None
    self.botones_accion.clear_widgets()
    self._actualizar()
    Clock.schedule_once(lambda _dt: self._iniciar_reloj(), 1.0)

  def _mostrar_final(self):
    p = self.partido
    self._detener_reloj()
    self.botones_accion.clear_widgets()
    self.estado_jugada.text = f"FINAL DEL PARTIDO\n{p.local.nombre} {p.resultado[0]} - {p.resultado[1]} {p.visitante.nombre}"
    contenido = BoxLayout(orientation="vertical", padding=12, spacing=8)
    contenido.add_widget(Label(text=self.estado_jugada.text, halign="center"))
    contenido.add_widget(Label(text=f"Tu nota: {p.calcular_nota_jugador(App.get_running_app().carrera.jugador):.1f}/10"))
    boton = Button(text="PROCESAR RESTO DE LA SEMANA", size_hint_y=None, height=48)
    contenido.add_widget(boton)
    popup = Popup(title="Partido terminado", content=contenido, size_hint=(0.85, 0.45), auto_dismiss=False)
    boton.bind(on_press=lambda *_: self._cerrar_y_procesar(popup))
    popup.open()

  def _cerrar_y_procesar(self, popup):
    popup.dismiss()
    app = App.get_running_app()
    carrera = app.carrera
    carrera.jugar_siguiente_semana()
    app.mostrar_pantalla("carrera")

class FootballGameApp(App):
  def build(self):
    Window.clearcolor = (0.025, 0.045, 0.075, 1)
    self.carrera = None
    self.partido_actual = None
    self.ruta_preferencias = os.path.join(self.user_data_dir, "preferencias.json")
    self.musica_activa = True
    self.efectos_activos = True
    self.volumen_musica = 0.20
    self.volumen_efectos = 0.65
    self._cargar_preferencias()
    self._lista_temas = [os.path.join(os.path.dirname(__file__), "assets", "music", "tracks", f"tema_{i:02d}.ogg") for i in range(1, 10)]
    self._temas_pendientes = []
    self._deteniendo_musica = False
    self.musica = None
    self._sonidos_efectos = {}
    self._cargar_efectos()
    if self.musica_activa:
      self._reproducir_siguiente_tema()
    self.carrera = None
    self.partido_actual = None
    self.pantallas = ScreenManager()
    self.pantallas.add_widget(MenuPrincipal(name="menu"))
    self.pantallas.add_widget(CrearJugador(name="crear"))
    self.pantallas.add_widget(PantallaCarrera(name="carrera"))
    self.pantallas.add_widget(PantallaPartido(name="partido"))
    return self.pantallas

  def _cargar_preferencias(self):
    try:
      with open(self.ruta_preferencias, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
      self.musica_activa = bool(datos.get("musica", True))
      self.efectos_activos = bool(datos.get("efectos", True))
      self.volumen_musica = max(0.0, min(1.0, float(datos.get("volumen_musica", 0.20))))
      self.volumen_efectos = max(0.0, min(1.0, float(datos.get("volumen_efectos", 0.65))))
    except (OSError, ValueError, TypeError):
      pass

  def _guardar_preferencias(self):
    try:
      os.makedirs(os.path.dirname(self.ruta_preferencias), exist_ok=True)
      with open(self.ruta_preferencias, "w", encoding="utf-8") as archivo:
        json.dump({
          "musica": self.musica_activa,
          "efectos": self.efectos_activos,
          "volumen_musica": self.volumen_musica,
          "volumen_efectos": self.volumen_efectos,
        }, archivo, ensure_ascii=False, indent=2)
    except OSError:
      pass

  def _cargar_efectos(self):
    base = os.path.join(os.path.dirname(__file__), "assets", "sounds")
    for nombre in ("click", "pelota", "lobby", "gol"):
      ruta = os.path.join(base, f"{nombre}.wav")
      sonido = SoundLoader.load(ruta)
      if sonido is not None:
        sonido.loop = False
        sonido.volume = self.volumen_efectos
        self._sonidos_efectos[nombre] = sonido

  def _reproducir_siguiente_tema(self, *_):
    if not self.musica_activa or not getattr(self, "_lista_temas", None):
      return
    if not self._temas_pendientes:
      self._temas_pendientes = self._lista_temas[:]
      random.shuffle(self._temas_pendientes)
      if len(self._temas_pendientes) > 1 and getattr(self, "_ultimo_tema", None) == self._temas_pendientes[-1]:
        self._temas_pendientes[0], self._temas_pendientes[-1] = self._temas_pendientes[-1], self._temas_pendientes[0]
    ruta = self._temas_pendientes.pop()
    self._ultimo_tema = ruta
    nuevo = SoundLoader.load(ruta)
    if nuevo is None:
      # Si un archivo no puede cargarse, pasar al siguiente sin bloquear el juego.
      Clock.schedule_once(self._reproducir_siguiente_tema, 0.2)
      return
    self._deteniendo_musica = True
    if self.musica is not None:
      try:
        self.musica.stop()
      except Exception:
        pass
    self.musica = nuevo
    self.musica.loop = False
    self.musica.volume = self.volumen_musica
    self.musica.bind(on_stop=self._tema_terminado)
    self._deteniendo_musica = False
    self.musica.play()

  def _tema_terminado(self, *_):
    if self.musica_activa and not self._deteniendo_musica:
      Clock.schedule_once(self._reproducir_siguiente_tema, 0.35)

  def alternar_musica(self):
    self.musica_activa = not self.musica_activa
    if self.musica_activa:
      self._reproducir_siguiente_tema()
    elif self.musica is not None:
      self._deteniendo_musica = True
      self.musica.stop()
      self._deteniendo_musica = False
    self._guardar_preferencias()
    self._actualizar_botones_audio()

  def alternar_efectos(self):
    self.efectos_activos = not self.efectos_activos
    self._guardar_preferencias()
    self._actualizar_botones_audio()
    if self.efectos_activos:
      self.reproducir_efecto("click")

  def reproducir_efecto(self, nombre):
    if not self.efectos_activos:
      return
    sonido = self._sonidos_efectos.get(nombre)
    if sonido is None:
      return
    try:
      sonido.stop()
      sonido.volume = self.volumen_efectos
      sonido.play()
    except Exception:
      pass

  def _actualizar_botones_audio(self):
    if not hasattr(self, "pantallas"):
      return
    try:
      menu = self.pantallas.get_screen("menu")
      menu.boton_musica.text = "MÚSICA: ACTIVADA" if self.musica_activa else "MÚSICA: DESACTIVADA"
      menu.boton_efectos.text = "EFECTOS: ACTIVADOS" if self.efectos_activos else "EFECTOS: DESACTIVADOS"
    except Exception:
      pass

  def abrir_configuracion_audio(self):
    contenido = BoxLayout(orientation="vertical", padding=16, spacing=12)
    contenido.add_widget(Label(text="MÚSICA DE FONDO", size_hint_y=None, height=26))
    slider_musica = Slider(min=0, max=1, value=self.volumen_musica)
    contenido.add_widget(slider_musica)
    contenido.add_widget(Label(text="EFECTOS DE SONIDO", size_hint_y=None, height=26))
    slider_efectos = Slider(min=0, max=1, value=self.volumen_efectos)
    contenido.add_widget(slider_efectos)
    fila = BoxLayout(size_hint_y=None, height=44, spacing=8)
    cerrar = Button(text="GUARDAR")
    fila.add_widget(cerrar)
    contenido.add_widget(fila)
    popup = Popup(title="Configuración de audio", content=contenido, size_hint=(0.86, 0.48))
    def guardar(*_):
      self.volumen_musica = float(slider_musica.value)
      self.volumen_efectos = float(slider_efectos.value)
      if self.musica is not None:
        self.musica.volume = self.volumen_musica
      for sonido in self._sonidos_efectos.values():
        sonido.volume = self.volumen_efectos
      self._guardar_preferencias()
      self.reproducir_efecto("click")
      popup.dismiss()
    cerrar.bind(on_press=guardar)
    popup.open()

  def mostrar_pantalla(self, nombre):
    pantalla_anterior = self.pantallas.current
    self.pantallas.current = nombre
    if nombre == "carrera":
      self.pantallas.get_screen("carrera").actualizar()
      if pantalla_anterior != "carrera":
        self.reproducir_efecto("lobby")

  def mostrar_carrera(self):
    self.mostrar_pantalla("carrera")

  def mostrar_mensaje(self, mensaje):
    if hasattr(self, "pantallas") and self.pantallas.current == "carrera":
      pantalla = self.pantallas.get_screen("carrera")
      pantalla.mensaje.text = str(mensaje)
      return

    contenido = BoxLayout(orientation="vertical", padding=12, spacing=10)
    contenido.add_widget(Label(text=str(mensaje)))
    boton = Button(text="Aceptar", size_hint_y=None, height=42)
    contenido.add_widget(boton)
    popup = Popup(title="Football Game", content=contenido, size_hint=(0.75, 0.5))
    boton.bind(on_press=popup.dismiss)
    popup.open()


if __name__ == "__main__":
  FootballGameApp().run()
