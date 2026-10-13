"""Reglas de calendario y selecciones nacionales del modo carrera.

La semana internacional tiene prioridad absoluta: las competiciones de clubes
no pueden programar partidos durante estas ventanas.
"""
import random


class CalendarioInternacional:
  SEMANAS_BLOQUEADAS = (8, 16, 24, 32, 40, 48)

  @classmethod
  def es_fecha_internacional(cls, semana):
    return semana in cls.SEMANAS_BLOQUEADAS

  @classmethod
  def siguiente_semana_de_clubes(cls, semana):
    while cls.es_fecha_internacional(semana):
      semana += 1
    return semana

  @classmethod
  def fechas_disponibles(cls, desde, cantidad):
    fechas = []
    semana = desde
    while len(fechas) < cantidad:
      if not cls.es_fecha_internacional(semana):
        fechas.append(semana)
      semana += 1
    return fechas


class SeleccionNacional:
  def __init__(self, pais, jugadores=None):
    self.nombre = pais
    self.pais = pais
    self.jugadores = list(jugadores or [])
    self.convocados = []
    self.historial = []

  def agregar_jugador(self, jugador):
    if jugador not in self.jugadores:
      self.jugadores.append(jugador)

  def convocar(self, cantidad=23):
    elegibles = [j for j in self.jugadores if j.esta_disponible()]
    elegibles.sort(key=lambda j: getattr(j, "valoracion", 0), reverse=True)
    self.convocados = elegibles[:cantidad]
    return self.convocados

  def registrar_resultado(self, rival, goles_propios, goles_rival, semana):
    resultado = {
      "pais": self.pais,
      "rival": rival,
      "goles_propios": goles_propios,
      "goles_rival": goles_rival,
      "semana": semana
    }
    self.historial.append(resultado)
    return resultado


class SistemaSelecciones:
  PAISES = (
    "Argentina", "Brasil", "Uruguay", "Chile", "Paraguay",
    "Colombia", "Ecuador", "Perú", "Bolivia", "Venezuela"
  )

  def __init__(self):
    self.selecciones = {pais: SeleccionNacional(pais) for pais in self.PAISES}

  def agregar_jugador(self, pais, jugador):
    if pais not in self.selecciones:
      self.selecciones[pais] = SeleccionNacional(pais)
    self.selecciones[pais].agregar_jugador(jugador)

  def convocar(self, pais, cantidad=23):
    if pais not in self.selecciones:
      return []
    return self.selecciones[pais].convocar(cantidad)


class BolsaClubesSudamericanos:
  """Clubes externos al universo de ligas simuladas, elegidos por cupos."""
  CUPOS_LIBERTADORES = {
    "Uruguay": 2, "Chile": 2,
    "Paraguay": 2, "Colombia": 2, "Ecuador": 2, "Perú": 2,
    "Bolivia": 2, "Venezuela": 2
  }
  CLUBES = {
    "Uruguay": ["Montevideo del Sur", "Atlético Oriental", "Deportivo del Plata", "Nacional de Montevideo"],
    "Chile": ["Santiago Unido", "Deportivo Andino", "Puerto Pacífico", "Universidad Central"],
    "Paraguay": ["Asunción FC", "Guaraní del Este", "Club del Paraguay", "Olimpia del Sur"],
    "Colombia": ["Bogotá Deportivo", "Atlético Cafetero", "Medellín Unido", "Cali del Valle"],
    "Ecuador": ["Quito Atlético", "Guayaquil Unido", "Deportivo Andino Ecuador", "Club del Pacífico"],
    "Perú": ["Lima Deportivo", "Cusco Unido", "Atlético del Perú", "Arequipa FC"],
    "Bolivia": ["La Paz FC", "Santa Cruz Unido", "Atlético Altiplano", "Cochabamba Deportivo"],
    "Venezuela": ["Caracas Deportivo", "Atlético Llanero", "Maracaibo FC", "Puerto Ordaz Unido"]
  }

  def seleccionar(self, cupos=None, semilla=None):
    rng = random.Random(semilla)
    cupos = cupos or self.CUPOS_LIBERTADORES
    elegidos = []
    for pais, cantidad in cupos.items():
      candidatos = list(self.CLUBES.get(pais, []))
      rng.shuffle(candidatos)
      for nombre in candidatos[:cantidad]:
        elegidos.append({"nombre": nombre, "pais": pais})
    return elegidos


def aplicar_ascensos_descensos(primera, segunda, cantidad=2):
  """Intercambia clubes al cierre de temporada y reinicia estadísticas de liga."""
  if not primera.equipos or not segunda.equipos:
    return {"descienden": [], "ascienden": []}

  descendidos = primera.tabla()[-cantidad:]
  ascendidos = segunda.tabla()[:cantidad]
  for equipo in descendidos:
    primera.equipos.remove(equipo)
    segunda.equipos.append(equipo)
    equipo.liga = segunda
  for equipo in ascendidos:
    segunda.equipos.remove(equipo)
    primera.equipos.append(equipo)
    equipo.liga = primera

  for liga in (primera, segunda):
    liga.jornadas = []
    liga.partidos = []
    liga.calendario = {}
    liga.estado = "pendiente"
    liga.campeon = None
    for equipo in liga.equipos:
      for atributo in ("gf", "gc", "pts", "pj", "g", "e", "p"):
        setattr(equipo, atributo, 0)
  return {"descienden": descendidos, "ascienden": ascendidos}
