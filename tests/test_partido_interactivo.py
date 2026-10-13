import unittest
from carrera import Carrera
from partido import Partido


class TestPartidoInteractivo(unittest.TestCase):
  def preparar_partido(self):
    carrera = Carrera.nueva("Jugador de prueba")
    carrera.jugar_siguiente_semana()
    oferta = carrera.ofertas_contractuales[0]
    carrera.responder_oferta_contractual(oferta, True)
    equipo = carrera.jugador.equipo
    partido = next(
      p for p in carrera.temporada.obtener_partidos_semana(carrera.temporada.semana)
      if equipo in (p.local, p.visitante) and p.estado == "pendiente"
    )
    partido.jugador_controlado = carrera.jugador
    partido.iniciar()
    return carrera, partido


  def test_jugadas_exitosas_aumentan_multiplicador_xp(self):
    from unittest.mock import patch
    from duelo import Duelo
    carrera, partido = self.preparar_partido()
    def ganar(self):
      self.ganador = self.jugador_1
    with patch("partido.random.choice", side_effect=lambda opciones: opciones[0]), patch.object(Duelo, "resolver", ganar):
      resultado = partido.resolver_accion_controlada("encarar", carrera.jugador, direccion="izquierda")
    self.assertTrue(resultado["ok"])
    self.assertGreaterEqual(partido.multiplicador_xp, 1.08)

  def test_quinta_amarilla_suspende_proximo_partido(self):
    carrera, partido = self.preparar_partido()
    jugador = carrera.jugador
    for _ in range(4):
      partido.agregar_amonestacion(jugador)
    self.assertEqual(jugador.partidos_suspension, 0)
    partido.agregar_amonestacion(jugador)
    self.assertEqual(jugador.partidos_suspension, 1)
    self.assertFalse(jugador.esta_disponible())

  def test_remates_fallados_reducen_nota(self):
    carrera = Carrera.nueva("Nota")
    jugador = carrera.jugador
    partido = Partido(carrera.liga.equipos[0], carrera.liga.equipos[1], "Estadio")
    partido.registrar_participacion(jugador, "puntos", 0)
    nota_base = partido.calcular_nota_jugador(jugador)
    partido.registrar_participacion(jugador, "remates_fallados", 0)
    self.assertLess(partido.calcular_nota_jugador(jugador), nota_base)

  def test_avanzar_intervalo_no_simula_partido_completo(self):
    _, partido = self.preparar_partido()
    resultado = partido.avanzar_intervalo(5)
    self.assertFalse(resultado["terminado"])
    self.assertEqual(partido.minuto, 5)
    self.assertEqual(partido.estado, "en juego")

  def test_decision_del_usuario_se_registra(self):
    carrera, partido = self.preparar_partido()
    respuesta = partido.resolver_accion_controlada("encarar", carrera.jugador)
    self.assertTrue(respuesta["ok"])
    self.assertEqual(partido.eventos[-1]["tipo"], "decision_jugador")
    self.assertEqual(partido.eventos[-1]["jugador"], carrera.jugador)


  def test_penal_permita_elegir_zona_y_registre_evento(self):
    carrera, partido = self.preparar_partido()
    respuesta = partido.resolver_penal(carrera.jugador, "abajo_izquierda")
    self.assertTrue(respuesta["ok"])
    self.assertEqual(partido.eventos[-1]["tipo"], "penal")
    self.assertEqual(partido.eventos[-1]["zona"], "abajo_izquierda")

  def test_tiro_libre_registra_zona_e_intento(self):
    carrera, partido = self.preparar_partido()
    respuesta = partido.resolver_tiro_libre(carrera.jugador, "arriba_derecha")
    self.assertTrue(respuesta["ok"])
    self.assertEqual(partido.eventos[-1]["tipo"], "tiro_libre")
    self.assertEqual(partido.eventos[-1]["zona"], "arriba_derecha")

  def test_corner_genera_duelo_aereo_y_evento(self):
    carrera, partido = self.preparar_partido()
    respuesta = partido.resolver_corner(carrera.jugador, "primer_palo")
    self.assertTrue(respuesta["ok"])
    self.assertEqual(partido.eventos[-1]["tipo"], "corner")
    self.assertEqual(partido.eventos[-1]["zona"], "primer_palo")

  def test_defensa_contener_resuelve_duelo_individual(self):
    carrera, partido = self.preparar_partido()
    respuesta = partido.resolver_accion_controlada("contener", carrera.jugador)
    self.assertTrue(respuesta["ok"])
    self.assertEqual(partido.eventos[-1]["accion"], "contener")

  def test_gambeta_direccional_registra_eleccion_y_mensaje(self):
    carrera, partido = self.preparar_partido()
    respuesta = partido.resolver_accion_controlada("encarar", carrera.jugador, direccion="izquierda")
    self.assertTrue(respuesta["ok"])
    self.assertIn("mensaje", respuesta)
    self.assertEqual(partido.eventos[-1]["accion"], "encarar")

  def test_apuesta_deportiva_espera_resultado_real(self):
    carrera, partido = self.preparar_partido()
    jugador = carrera.jugador
    saldo_inicial = jugador.dinero
    invalida = carrera.casino.apostar_partido(jugador, 999, "local", 0.5, partido=partido)
    self.assertFalse(invalida["ok"])
    apuesta = carrera.casino.apostar_partido(jugador, 1000, "local", 0.5, partido=partido)
    self.assertTrue(apuesta["ok"])
    self.assertTrue(apuesta["pendiente"])
    self.assertEqual(jugador.dinero, saldo_inicial - 1000)
    self.assertEqual(len(carrera.casino.apuestas_pendientes), 1)
    partido.resultado = (1, 0)
    partido.estado = "terminado"
    liquidacion = carrera.casino.liquidar_apuestas_partido(partido, jugador)
    self.assertEqual(len(liquidacion), 1)
    self.assertFalse(carrera.casino.apuestas_pendientes)

  def test_semana_se_procesa_despues_del_partido_interactivo(self):
    carrera, partido = self.preparar_partido()
    while partido.estado != "terminado":
      partido.avanzar_intervalo(10)
      if partido.estado == "en juego" and partido.minuto % 10 == 0:
        partido.resolver_accion_controlada("pasar", carrera.jugador)
    resultado = carrera.jugar_siguiente_semana()
    self.assertTrue(resultado["ok"])
    self.assertEqual(partido.estado, "terminado")
    self.assertEqual(carrera.temporada.semana, 3)


  def test_pase_exitoso_abre_una_ultima_oportunidad(self):
    from unittest.mock import patch
    from duelo import Duelo
    carrera = Carrera.nueva("Pase")
    carrera.jugar_siguiente_semana()
    carrera.responder_oferta_contractual(carrera.ofertas_contractuales[0], True)
    rival = next(e for e in carrera.liga.equipos if e is not carrera.jugador.equipo)
    partido = Partido(carrera.jugador.equipo, rival, carrera.jugador.equipo.estadio)
    partido.iniciar()
    def ganar(self):
      self.ganador = self.jugador_1
    with patch("partido.random.choice", side_effect=lambda opciones: opciones[0]), patch.object(Duelo, "resolver", ganar):
      respuesta = partido.resolver_accion_controlada("pasar", carrera.jugador)
    self.assertTrue(respuesta["ok"])
    self.assertIn("continuacion", respuesta)
    self.assertEqual(respuesta["continuacion"][0][1], "rematar")

  def test_pase_no_registra_asistencia_si_no_hay_gol(self):
    from unittest.mock import patch
    from duelo import Duelo
    carrera, partido = self.preparar_partido()
    def ganar(self):
      self.ganador = self.jugador_1
    with patch("partido.random.choice", side_effect=lambda opciones: opciones[0]), patch.object(Duelo, "resolver", ganar):
      respuesta = partido.resolver_accion_controlada("pasar", carrera.jugador, direccion="al_pie")
    self.assertTrue(respuesta["ok"])
    self.assertEqual(partido.asistencias, [])

  def test_gambeta_no_ofrece_seguir_jugada(self):
    from unittest.mock import patch
    from duelo import Duelo
    carrera, partido = self.preparar_partido()
    def ganar(self):
      self.ganador = self.jugador_1
    with patch("partido.random.choice", side_effect=lambda opciones: opciones[0]), patch.object(Duelo, "resolver", ganar):
      respuesta = partido.resolver_accion_controlada("encarar", carrera.jugador, direccion="derecha")
    if respuesta.get("continuacion"):
      self.assertTrue(all("seguir" not in etiqueta.lower() for etiqueta, _ in respuesta["continuacion"]))

  def test_remates_fallados_bajan_nota(self):
    carrera, partido = self.preparar_partido()
    jugador = carrera.jugador
    partido.registrar_participacion(jugador, "remates_fallados", 0)
    nota_con_fallo = partido.calcular_nota_jugador(jugador)
    partido.actuaciones[jugador]["remates_fallados"] = 0
    nota_sin_fallo = partido.calcular_nota_jugador(jugador)
    self.assertLess(nota_con_fallo, nota_sin_fallo)



if __name__ == "__main__":
  unittest.main()
