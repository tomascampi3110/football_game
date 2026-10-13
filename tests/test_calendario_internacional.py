import unittest
from calendario_internacional import (
  CalendarioInternacional,
  BolsaClubesSudamericanos,
  SistemaSelecciones,
  aplicar_ascensos_descensos
)
from equipo import Equipo
from competiciones import Liga
from jugador import Jugador


class TestCalendarioInternacional(unittest.TestCase):
  def test_semanas_internacionales_bloqueadas(self):
    for semana in CalendarioInternacional.SEMANAS_BLOQUEADAS:
      self.assertTrue(CalendarioInternacional.es_fecha_internacional(semana))
      self.assertFalse(CalendarioInternacional.es_fecha_internacional(
        CalendarioInternacional.siguiente_semana_de_clubes(semana)
      ))

  def test_cupos_sudamericanos_no_exceden_clubes_disponibles(self):
    clubes = BolsaClubesSudamericanos().seleccionar(semilla=12)
    paises = {}
    for club in clubes:
      paises[club["pais"]] = paises.get(club["pais"], 0) + 1
    self.assertLessEqual(paises["Uruguay"], 4)
    self.assertLessEqual(paises["Colombia"], 4)
    self.assertEqual(len(clubes), sum(min(c, 4) for c in BolsaClubesSudamericanos.CUPOS_LIBERTADORES.values()))

  def test_seleccion_convoca_mejores_disponibles(self):
    seleccion = SistemaSelecciones()
    bajo = Jugador("Bajo", 22, "delantero")
    alto = Jugador("Alto", 22, "delantero")
    bajo.valoracion = 40
    alto.valoracion = 80
    seleccion.agregar_jugador("Argentina", bajo)
    seleccion.agregar_jugador("Argentina", alto)
    self.assertEqual(seleccion.convocar("Argentina", 1), [alto])

  def test_ascensos_y_descensos_intercambian_clubes(self):
    a = [Equipo(f"A{i}", "Estadio", "DT", None) for i in range(4)]
    b = [Equipo(f"B{i}", "Estadio", "DT", None) for i in range(4)]
    primera = Liga("Primera", a, 1)
    segunda = Liga("B", b, 2)
    for i, equipo in enumerate(a):
      equipo.pts = 10 - i
    for i, equipo in enumerate(b):
      equipo.pts = 10 - i
    resultado = aplicar_ascensos_descensos(primera, segunda, 2)
    self.assertEqual(len(primera.equipos), 4)
    self.assertEqual(len(segunda.equipos), 4)
    self.assertEqual(len(resultado["descienden"]), 2)
    self.assertEqual(len(resultado["ascienden"]), 2)
    self.assertTrue(all(e.liga is segunda for e in resultado["descienden"]))
    self.assertTrue(all(e.liga is primera for e in resultado["ascienden"]))


if __name__ == "__main__":
  unittest.main()
