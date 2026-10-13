import unittest
from carrera import Carrera


class TestPlantelesReales(unittest.TestCase):
  def test_planteles_reales_se_cargan_y_se_completan(self):
    carrera = Carrera.nueva(
      "Prueba",
      opciones={"segunda_division": False, "copas_grandes": False, "ligas_extras": True}
    )
    equipos = carrera.temporada.obtener_equipos()
    for nombre, minimo in (("River Plate", 10), ("Racing Club", 10), ("Rosario Central", 10), ("Flamengo", 10), ("Manchester City", 10), ("Arsenal", 10), ("Liverpool", 10)):
      equipo = next(e for e in equipos if e.nombre == nombre)
      self.assertGreaterEqual(len(equipo.jugadores), 18)
      reales = [j for j in equipo.jugadores if getattr(j, "es_jugador_real", False)]
      self.assertGreaterEqual(len(reales), minimo)
    river = next(e for e in equipos if e.nombre == "River Plate")
    self.assertIn("Thiago Almada", [j.nombre for j in river.jugadores])
    boca = next(e for e in equipos if e.nombre == "Boca Juniors")
    nombres_boca = {j.nombre for j in boca.jugadores}
    self.assertTrue({"Miguel Merentiel", "Leandro Paredes", "Agustín Marchesín"}.issubset(nombres_boca))
    merentiel = next(j for j in boca.jugadores if j.nombre == "Miguel Merentiel")
    paredes = next(j for j in boca.jugadores if j.nombre == "Leandro Paredes")
    self.assertEqual(merentiel.valoracion, 82)
    self.assertEqual(paredes.valoracion, 85)
    self.assertTrue(getattr(merentiel, "es_jugador_real", False))

  def test_valoraciones_reales_se_mantienen(self):
    carrera = Carrera.nueva("Prueba", opciones={"segunda_division": False, "copas_grandes": False, "ligas_extras": False})
    boca = next(e for e in carrera.liga.equipos if e.nombre == "Boca Juniors")
    por_nombre = {j.nombre: j for j in boca.jugadores}
    self.assertEqual(por_nombre["Miguel Merentiel"].valoracion, 82)
    self.assertEqual(por_nombre["Leandro Paredes"].valoracion, 85)


  def test_primera_division_argentina_tiene_planteles_reales_ampliados(self):
    carrera = Carrera.nueva("Base completa", opciones={"segunda_division": False, "copas_grandes": False, "ligas_extras": False})
    for equipo in carrera.liga.equipos:
      reales = [j for j in equipo.jugadores if getattr(j, "es_jugador_real", False)]
      self.assertGreaterEqual(len(reales), 18, f"Plantel real incompleto: {equipo.nombre}")

  def test_grandes_clubes_internacionales_tienen_jugadores_reales(self):
    carrera = Carrera.nueva("Base internacional", opciones={"segunda_division": False, "copas_grandes": False, "ligas_extras": True})
    equipos = carrera.temporada.obtener_equipos()
    por_nombre = {e.nombre: e for e in equipos}
    for nombre in ("Real Madrid", "Barcelona", "Atlético de Madrid", "Palmeiras", "Paris Saint-Germain", "Bayern Múnich"):
      equipo = por_nombre[nombre]
      reales = [j for j in equipo.jugadores if getattr(j, "es_jugador_real", False)]
      self.assertGreaterEqual(len(reales), 10, nombre)


if __name__ == "__main__":
  unittest.main()
