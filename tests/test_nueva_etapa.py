import unittest
from carrera import Carrera

class TestNuevaEtapa(unittest.TestCase):
  def test_tutorial_de_cuatro_semanas_sin_partidos(self):
    carrera = Carrera.nueva("Prueba", 18, "delantero", opciones={"segunda_division": False, "copas_grandes": False, "ligas_extras": False})
    self.assertEqual(carrera.semanas_tutorial, 4)
    for semana in range(1, 5):
      self.assertEqual(carrera.temporada.obtener_partidos_semana(semana), [])
      resultado = carrera.jugar_siguiente_semana()
      self.assertTrue(resultado["tutorial"])
      self.assertEqual(resultado["partidos"], 0)
    self.assertEqual(carrera.temporada.semana, 5)
    self.assertEqual(len([o for o in carrera.ofertas_contractuales if o["estado"] == "pendiente"]), 3)

  def test_opciones_agregan_segunda_division_y_copa(self):
    carrera = Carrera.nueva("Prueba", 18, "delantero", opciones={"segunda_division": True, "copas_grandes": True, "ligas_extras": False})
    nombres = [c.nombre for c in carrera.temporada.competiciones]
    self.assertIn("Primera Nacional Argentina", nombres)
    self.assertIn("Copa Libertadores", nombres)

  def test_opcion_ligas_extras_incluye_brasil_y_europa(self):
    carrera = Carrera.nueva("Prueba", 18, "delantero", opciones={"segunda_division": False, "copas_grandes": False, "ligas_extras": True})
    nombres = [c.nombre for c in carrera.temporada.competiciones]
    self.assertIn("Brasil · Série A", nombres)
    self.assertIn("Inglaterra · Premier League", nombres)
    self.assertIn("España · LaLiga", nombres)

  def test_simulacion_rapida_finaliza_temporada(self):
    carrera = Carrera.nueva("Prueba", 18, "delantero")
    resultado = carrera.simular_hasta_fin_temporada()
    self.assertTrue(resultado["ok"])
    self.assertEqual(carrera.temporada.estado, "terminada")

if __name__ == "__main__":
  unittest.main()
