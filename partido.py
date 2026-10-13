import random
from duelo import Duelo

class Partido:
  def __init__(
    self,
    local,
    visitante,
    estadio,
    tipo="liga",
    permite_prorroga=False
  ):
    self.local = local
    self.visitante = visitante
    self.estadio = estadio
    self.tipo = tipo
    self.permite_prorroga = permite_prorroga

    self.goles_local = []
    self.goles_visitante = []
    self.asistencias = []
    self.eventos = []
    self.amonestados = []
    self.lesiones = []
    self.duelos = []

    self.resultado = (0, 0)
    self.estado = "pendiente"
    self.minuto = 0
    self.ganador = None
    self.tiempo_extra = False
    self.actuaciones = {}
    self.participantes = set()
    self.jugador_controlado = None
    self.multiplicador_xp = 1.0
    self.acciones_exitosas_controladas = 0
    self.suspendidos_al_inicio = []


  def registrar_participacion(self, jugador, evento, puntos=0):
    if jugador not in self.actuaciones:
      self.actuaciones[jugador] = {
        "puntos": 0.0,
        "goles": 0,
        "asistencias": 0,
        "amonestaciones": 0,
        "duelos_ganados": 0,
        "duelos_jugados": 0,
        "remates": 0,
        "remates_fallados": 0,
        "pases_exitosos": 0,
        "acciones_fallidas": 0
      }

    self.participantes.add(jugador)
    self.actuaciones[jugador]["puntos"] += puntos
    # "puntos" es la métrica numérica, no un evento contable: evitar sumar +1
    # cada vez que se registra una bonificación o penalización.
    if evento != "puntos" and evento in self.actuaciones[jugador]:
      self.actuaciones[jugador][evento] += 1


  def calcular_nota_jugador(self, jugador):
    """Nota equilibrada: premia aportes concretos y penaliza errores repetidos."""
    datos = self.actuaciones.get(jugador, {})
    # La nota parte de un valor neutral; no llega a 10 por participar.
    nota = 6.2 + datos.get("puntos", 0)
    nota += datos.get("goles", 0) * 1.07
    nota += datos.get("asistencias", 0) * 0.60
    nota += min(datos.get("duelos_ganados", 0), 8) * 0.08
    nota += min(datos.get("pases_exitosos", 0), 12) * 0.035
    nota -= datos.get("remates_fallados", 0) * 0.38
    nota -= datos.get("acciones_fallidas", 0) * 0.22
    nota -= datos.get("amonestaciones", 0) * 0.50
    nota -= datos.get("errores_graves", 0) * 0.35
    return round(max(1.0, min(10.0, nota)), 2)


  def iniciar(self):
    if self.estado != "pendiente":
      return

    self.estado = "en juego"
    self.minuto = 0
    todos = [j for equipo in (self.local, self.visitante) for j in getattr(equipo, "jugadores", [])]
    self.suspendidos_al_inicio = [j for j in todos if getattr(j, "partidos_suspension", 0) > 0]
    # La expulsión dura el encuentro en curso; la suspensión, en cambio, persiste.
    for jugador in todos:
      jugador.expulsado = False


  def obtener_jugadores_disponibles(self, equipo):
    if not hasattr(equipo, "jugadores"):
      return []

    jugadores = []

    for jugador in equipo.jugadores:
      if jugador.esta_disponible() and not getattr(jugador, "expulsado", False):
        jugadores.append(jugador)

    return jugadores


  def elegir_jugador(self, equipo):
    jugadores = self.obtener_jugadores_disponibles(equipo)

    if not jugadores:
      return None

    return random.choice(jugadores)


  def elegir_oponente(self, equipo):
    if equipo == self.local:
      return self.elegir_jugador(self.visitante)

    return self.elegir_jugador(self.local)


  def obtener_jugadores_por_posicion(
    self,
    equipo,
    posiciones
  ):
    jugadores = self.obtener_jugadores_disponibles(equipo)

    resultado = []

    for jugador in jugadores:
      posicion = jugador.obtener_posicion_normalizada()

      if posicion in posiciones:
        resultado.append(jugador)

    return resultado


  def elegir_arquero(self, equipo):
    arqueros = self.obtener_jugadores_por_posicion(
      equipo,
      ["arquero"]
    )

    if not arqueros:
      return self.elegir_jugador(equipo)

    return random.choice(arqueros)


  def agregar_duelo(
    self,
    jugador_1,
    jugador_2,
    tipo
  ):
    duelo = Duelo(
      jugador_1,
      jugador_2,
      tipo
    )

    duelo.resolver()

    self.duelos.append(duelo)
    self.registrar_participacion(jugador_1, "duelos_jugados")
    self.registrar_participacion(jugador_2, "duelos_jugados")

    if duelo.ganador is not None:
      self.registrar_participacion(
        duelo.ganador,
        "duelos_ganados"
      )

    return duelo


  def agregar_gol(
    self,
    jugador,
    equipo
  ):
    gol = {
      "jugador": jugador,
      "minuto": self.minuto
    }

    if equipo == self.local:
      self.goles_local.append(gol)

    else:
      self.goles_visitante.append(gol)

    jugador.goles += 1
    self.registrar_participacion(jugador, "goles")
    self.actuaciones[jugador]["puntos"] += 0.2


  def agregar_asistencia(
    self,
    jugador,
    equipo
  ):
    asistencia = {
      "jugador": jugador,
      "equipo": equipo,
      "minuto": self.minuto
    }

    self.asistencias.append(asistencia)

    jugador.asistencias += 1
    self.registrar_participacion(jugador, "asistencias")


  def agregar_amonestacion(self, jugador):
    amonestacion = {
      "jugador": jugador,
      "minuto": self.minuto
    }

    self.amonestados.append(amonestacion)

    jugador.amonestado += 1
    jugador.amarillas_temporada = getattr(jugador, "amarillas_temporada", 0) + 1
    self.registrar_participacion(jugador, "amonestaciones")
    if jugador.amarillas_temporada >= 5:
      jugador.amarillas_temporada = 0
      jugador.partidos_suspension = max(1, getattr(jugador, "partidos_suspension", 0))
      self.eventos.append({
        "tipo": "suspension", "jugador": jugador,
        "equipo": getattr(jugador, "equipo", None), "minuto": self.minuto,
        "mensaje": f"{jugador.nombre} llegó a cinco amarillas y se pierde el próximo partido."
      })


  def agregar_lesion(self, jugador):
    lesion = {
      "jugador": jugador,
      "minuto": self.minuto
    }

    self.lesiones.append(lesion)

    jugador.lesion = True
    jugador.semanas_lesion = random.randint(1, 4)
    self.registrar_participacion(jugador, "puntos", -0.1)


  def generar_jugada_aerea(self):
    atacantes_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    atacantes_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    if not atacantes_local or not atacantes_visitante:
      return

    if random.random() < 0.5:
      jugador_1 = random.choice(atacantes_local)
      jugador_2 = random.choice(
        atacantes_visitante
      )
      equipo_1 = self.local
      equipo_2 = self.visitante

    else:
      jugador_1 = random.choice(atacantes_visitante)
      jugador_2 = random.choice(
        atacantes_local
      )
      equipo_1 = self.visitante
      equipo_2 = self.local

    duelo = self.agregar_duelo(
      jugador_1,
      jugador_2,
      "aereo"
    )

    if duelo.ganador == jugador_1:
      self.generar_remate(
        jugador_1,
        equipo_1
      )


  def generar_jugada_uno_contra_uno(self):
    jugadores_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    jugadores_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    if not jugadores_local or not jugadores_visitante:
      return

    if random.random() < 0.5:
      jugador_1 = random.choice(jugadores_local)
      jugador_2 = random.choice(
        jugadores_visitante
      )
      equipo = self.local

    else:
      jugador_1 = random.choice(jugadores_visitante)
      jugador_2 = random.choice(
        jugadores_local
      )
      equipo = self.visitante

    duelo = self.agregar_duelo(
      jugador_1,
      jugador_2,
      "uno_contra_uno"
    )

    if duelo.ganador == jugador_1:
      self.generar_remate(
        jugador_1,
        equipo
      )


  def generar_pelota_dividida(self):
    jugadores_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    jugadores_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["delantero", "mediocampista", "defensor"]
      )
    )

    if not jugadores_local or not jugadores_visitante:
      return

    jugador_1 = random.choice(jugadores_local)
    jugador_2 = random.choice(
      jugadores_visitante
    )

    self.agregar_duelo(
      jugador_1,
      jugador_2,
      "pelota_dividida"
    )


  def generar_pase(self):
    mediocampistas_local = (
      self.obtener_jugadores_por_posicion(
        self.local,
        ["mediocampista", "delantero", "defensor"]
      )
    )

    mediocampistas_visitante = (
      self.obtener_jugadores_por_posicion(
        self.visitante,
        ["mediocampista", "delantero", "defensor"]
      )
    )

    if not mediocampistas_local or not mediocampistas_visitante:
      return

    if random.random() < 0.5:
      jugador_1 = random.choice(
        mediocampistas_local
      )
      jugador_2 = random.choice(
        mediocampistas_visitante
      )
      equipo = self.local

    else:
      jugador_1 = random.choice(
        mediocampistas_visitante
      )
      jugador_2 = random.choice(
        mediocampistas_local
      )
      equipo = self.visitante

    duelo = self.agregar_duelo(
      jugador_1,
      jugador_2,
      "pase"
    )

    # Un pase o duelo ganado no es una asistencia: la asistencia se registra
    # únicamente cuando el equipo convierte un gol posterior.


  def generar_remate(
    self,
    jugador,
    equipo,
    direccion=None
  ):
    arquero = self.elegir_arquero(
      self.visitante
      if equipo == self.local
      else self.local
    )

    if arquero is None:
      return

    duelo = self.agregar_duelo(
      jugador,
      arquero,
      "remate"
    )

    # Ganar el duelo contra el arquero no garantiza gol: también importan
    # el ángulo, la presión y la calidad de la ocasión. Evita que rematar
    # en cada situación produzca goleadas automáticas.
    probabilidad_conversion = 0.46
    if jugador.obtener_posicion_normalizada() == "delantero":
      probabilidad_conversion += 0.08
    if getattr(jugador, "forma", 50) >= 75:
      probabilidad_conversion += 0.04
    if direccion:
      probabilidad_conversion += 0.045 if "izquierda" in direccion or "derecha" in direccion else -0.025
    probabilidad_conversion = max(0.20, min(0.62, probabilidad_conversion))
    datos = self.actuaciones.setdefault(jugador, {"puntos": 0.0, "goles": 0, "asistencias": 0, "amonestaciones": 0, "duelos_ganados": 0, "duelos_jugados": 0, "remates": 0, "remates_fallados": 0, "pases_exitosos": 0, "acciones_fallidas": 0})
    datos["remates"] = datos.get("remates", 0) + 1
    if duelo.ganador == jugador and random.random() < probabilidad_conversion:
      self.agregar_gol(jugador, equipo)
      self.intentar_asistencia(jugador, equipo)
    else:
      datos["remates_fallados"] = datos.get("remates_fallados", 0) + 1


  def intentar_asistencia(
    self,
    jugador,
    equipo
  ):
    compañeros = (
      self.obtener_jugadores_disponibles(
        equipo
      )
    )

    compañeros = [
      compañero
      for compañero in compañeros
      if compañero != jugador
    ]

    if not compañeros:
      return

    if random.random() < 0.7:
      asistente = random.choice(
        compañeros
      )

      self.agregar_asistencia(
        asistente,
        equipo
      )


  def generar_amarilla(self):
    equipo = random.choice([
      self.local,
      self.visitante
    ])

    jugadores = self.obtener_jugadores_disponibles(equipo)
    if not jugadores:
      return
    jugador = random.choice(jugadores)
    ya_amonestado = sum(1 for tarjeta in self.amonestados if tarjeta["jugador"] is jugador)
    if ya_amonestado and random.random() < 0.30:
      self.eventos.append({
        "tipo": "roja",
        "jugador": jugador,
        "equipo": equipo,
        "minuto": self.minuto,
        "mensaje": f"{jugador.nombre} recibió la segunda amarilla y fue expulsado."
      })
      jugador.expulsado = True
      jugador.partidos_suspension = max(1, getattr(jugador, "partidos_suspension", 0))
      return
    self.agregar_amonestacion(jugador)


  def generar_lesion(self):
    equipo = random.choice([
      self.local,
      self.visitante
    ])

    jugador = self.elegir_jugador(equipo)

    if jugador is None:
      return

    reduccion = 0
    for objeto in getattr(jugador, "equipamiento", {}).values():
      if getattr(objeto, "activo", False):
        reduccion += objeto.obtener_reduccion_lesion()

    probabilidad = max(0.02, 0.25 * (1 - min(0.90, reduccion)))
    if random.random() < probabilidad:
      self.agregar_lesion(jugador)


  def generar_evento(self):
    numero = random.random()

    if numero < 0.035:
      self.generar_jugada_aerea()

    elif numero < 0.125:
      self.generar_jugada_uno_contra_uno()

    elif numero < 0.155:
      self.generar_pelota_dividida()

    elif numero < 0.185:
      self.generar_pase()

    elif numero < 0.198:
      self.generar_amarilla()

    elif numero < 0.203:
      self.generar_lesion()


  def avanzar_minuto(self):
    if self.estado != "en juego":
      return

    self.minuto += 1

    self.generar_evento()


  def calcular_resultado(self):
    self.resultado = (
      len(self.goles_local),
      len(self.goles_visitante)
    )


  def determinar_ganador(self):
    if self.resultado[0] > self.resultado[1]:
      self.ganador = self.local

    elif self.resultado[1] > self.resultado[0]:
      self.ganador = self.visitante

    else:
      self.ganador = None


  def resolver_empate(self):
    if self.resultado[0] != self.resultado[1]:
      self.determinar_ganador()
      return

    jugador_local = self.elegir_jugador(
      self.local
    )

    jugador_visitante = self.elegir_jugador(
      self.visitante
    )

    if (
      jugador_local is None
      or jugador_visitante is None
    ):
      self.ganador = random.choice([
        self.local,
        self.visitante
      ])
      return

    duelo = self.agregar_duelo(
      jugador_local,
      jugador_visitante,
      "pelota_dividida"
    )

    if duelo.ganador == jugador_local:
      self.ganador = self.local

    else:
      self.ganador = self.visitante

    self.eventos.append({
      "tipo": "desempate",
      "jugador": duelo.ganador,
      "equipo": self.ganador,
      "minuto": self.minuto
    })


  def iniciar_prorroga(self):
    if not self.permite_prorroga:
      return

    if self.resultado[0] != self.resultado[1]:
      return

    self.tiempo_extra = True
    self.minuto = 90

    self.eventos.append({
      "tipo": "inicio_prorroga",
      "minuto": 90
    })


  def resolver_accion_controlada(self, accion, jugador, direccion=None):
    """Resuelve una decisión del jugador humano y la registra en el partido."""
    if self.estado != "en juego" or jugador is None:
      return {"ok": False, "mensaje": "No hay una jugada activa."}

    equipo = getattr(jugador, "equipo", None)
    if equipo not in (self.local, self.visitante):
      return {"ok": False, "mensaje": "El futbolista no participa de este partido."}

    rival = self.visitante if equipo == self.local else self.local
    rivales = self.obtener_jugadores_disponibles(rival)
    companeros = [j for j in self.obtener_jugadores_disponibles(equipo) if j is not jugador]
    rival_directo = random.choice(rivales) if rivales else None
    exito = False
    mensaje = ""

    if accion in ("rematar", "cabezazo"):
      ejecutor = jugador
      if accion == "cabezazo":
        ejecutor = getattr(self, "objetivo_corner_pendiente", None) or jugador
        self.objetivo_corner_pendiente = None
      antes = len(self.goles_local) + len(self.goles_visitante)
      self.generar_remate(ejecutor, equipo, direccion=direccion)
      despues = len(self.goles_local) + len(self.goles_visitante)
      exito = despues > antes
      zona_texto = f" hacia {direccion.replace('_', ' ')}" if direccion else ""
      if exito:
        mensaje = f"¡GOOOL de {ejecutor.nombre}! El remate{zona_texto} terminó en la red."
      else:
        self.registrar_participacion(jugador, "puntos", -0.10)
        mensaje = f"{ejecutor.nombre} remató{zona_texto}, pero el arquero lo contuvo o el tiro salió desviado."

    elif accion == "asegurar":
      self.registrar_participacion(jugador, "puntos", 0.12)
      exito = True
      mensaje = f"{jugador.nombre} mantuvo la posesión y el ataque sigue vivo."
    elif accion in ("pasar", "encarar", "presionar", "interceptar", "contener"):
      if rival_directo is None:
        exito = random.random() < 0.65
      else:
        tipo = {
          "pasar": "pase",
          "encarar": "uno_contra_uno",
          "presionar": "pelota_dividida",
          "interceptar": "pase",
          "contener": "cuerpo_a_cuerpo"
        }[accion]
        # En defensa, contener prioriza fuerza/equilibrio y reduce la apuesta
        # de una entrada agresiva; sigue resolviéndose como duelo individual.
        duelo = self.agregar_duelo(jugador, rival_directo, tipo)
        exito = duelo.ganador == jugador
        if direccion in ("izquierda", "centro", "derecha", "al_pie", "al_espacio", "pared"):
          ajuste = {"izquierda": 0.025, "centro": -0.015, "derecha": 0.025,
            "al_pie": 0.045, "al_espacio": -0.025, "pared": -0.01}.get(direccion, 0)
          if not exito and random.random() < max(0.05, min(0.75, 0.5 + ajuste)):
            exito = True
          elif exito and random.random() < max(0.02, min(0.35, 0.10 - ajuste)):
            exito = False
      if exito:
        self.registrar_participacion(jugador, "puntos", 0.18)
        if accion == "pasar" and companeros:
          receptor = random.choice(companeros)
          self.registrar_participacion(jugador, "pases_exitosos", 1)
          self.registrar_participacion(receptor, "puntos", 0.08)
          # Un pase exitoso crea una ocasión concreta, no una asistencia automática.
          tipo_pase = {"al_pie": "al pie", "al_espacio": "al espacio", "pared": "de primera para una pared"}.get(direccion, "")
          mensaje = f"Buen pase {tipo_pase} de {jugador.nombre}; {receptor.nombre} controla. ¡Queda una última oportunidad para definir!"
          continuacion = [("REMATAR AL ARCO", "rematar")]
        elif accion == "encarar":
          if direccion and random.random() < 0.035:
            mensaje = f"¡CAÑO DE {jugador.nombre.upper()}! Le pasó la pelota entre las piernas y lo dejó atrás."
            self.registrar_participacion(jugador, "puntos", 0.10)
          else:
            mensaje = f"{jugador.nombre} gambeteó hacia {direccion or 'adelante'} y superó a su marcador."
          continuacion = [("REMATAR CON VENTAJA", "rematar")]
        elif accion == "contener":
          mensaje = f"{jugador.nombre} ganó el choque físico y frenó el avance rival."
        elif accion == "interceptar":
          mensaje = f"{jugador.nombre} leyó la jugada y cortó la línea de pase."
        elif accion == "asegurar":
          mensaje = f"{jugador.nombre} aseguró la posesión y el equipo mantiene el ataque."
        else:
          mensaje = f"{jugador.nombre} recuperó la pelota con una buena presión."
      else:
        self.registrar_participacion(jugador, "puntos", -0.12)
        self.registrar_participacion(jugador, "acciones_fallidas", 1)
        mensaje = f"La jugada de {jugador.nombre} no salió: el rival recuperó la pelota."
      if accion == "presionar" and random.random() < (0.22 if not exito else 0.055):
        self.agregar_amonestacion(jugador)
        mensaje += f" Además, {jugador.nombre} recibió tarjeta amarilla por la entrada."
    else:
      return {"ok": False, "mensaje": "Acción desconocida."}

    if exito and accion in ("encarar", "pasar", "presionar", "interceptar", "contener", "asegurar"):
      self.acciones_exitosas_controladas += 1
      self.multiplicador_xp = min(2.0, 1.0 + self.acciones_exitosas_controladas * 0.08)
    self.eventos.append({"tipo": "decision_jugador", "accion": accion, "jugador": jugador, "equipo": equipo, "minuto": self.minuto, "exito": exito, "multiplicador_xp": self.multiplicador_xp, "mensaje": mensaje})
    self.calcular_resultado()
    respuesta = {"ok": True, "exito": exito, "mensaje": mensaje, "resultado": self.resultado}
    if exito and accion in ("pasar", "encarar") and "continuacion" in locals():
      respuesta["continuacion"] = continuacion
    return respuesta

  def resolver_tiro_libre(self, jugador, zona):
    """Tiro libre directo: el usuario elige la zona y los atributos determinan el resultado."""
    zonas = {"arriba_izquierda", "arriba_centro", "arriba_derecha", "medio_izquierda", "centro", "medio_derecha", "abajo_izquierda", "abajo_centro", "abajo_derecha"}
    if self.estado != "en juego" or jugador is None or zona not in zonas:
      return {"ok": False, "mensaje": "No hay un tiro libre válido para resolver."}
    equipo = getattr(jugador, "equipo", None)
    if equipo not in (self.local, self.visitante):
      return {"ok": False, "mensaje": "El jugador no participa de este partido."}
    rival = self.visitante if equipo == self.local else self.local
    arquero = self.elegir_arquero(rival)
    if arquero is None:
      return {"ok": False, "mensaje": "El rival no tiene arquero disponible."}
    precision = jugador.obtener_estadistica("precision")
    definicion = jugador.obtener_estadistica("definicion")
    reaccion = arquero.obtener_estadistica("reaccion")
    altura = "arriba" in zona or "abajo" in zona
    esquina = "izquierda" in zona or "derecha" in zona
    probabilidad = 0.16 + (precision + definicion - 100) / 500
    probabilidad += 0.05 if esquina else 0
    probabilidad += 0.025 if altura else 0
    probabilidad -= (reaccion - 50) / 600
    probabilidad = max(0.05, min(0.38, probabilidad))
    gol = random.random() < probabilidad
    if gol:
      self.agregar_gol(jugador, equipo)
      mensaje = f"¡Golazo de tiro libre! {jugador.nombre} la colocó en {zona.replace('_', ' ')}."
      self.registrar_participacion(jugador, "puntos", 0.35)
    else:
      mensaje = f"Tiro libre de {jugador.nombre} hacia {zona.replace('_', ' ')}: el arquero o la barrera lo rechazó."
      self.registrar_participacion(jugador, "puntos", -0.06)
      self.registrar_participacion(jugador, "remates_fallados", 1)
    self.eventos.append({"tipo": "tiro_libre", "minuto": self.minuto, "jugador": jugador, "arquero": arquero, "zona": zona, "gol": gol, "equipo": equipo, "mensaje": mensaje})
    self.calcular_resultado()
    return {"ok": True, "exito": gol, "mensaje": mensaje, "resultado": self.resultado}

  def resolver_corner(self, jugador, zona):
    """Centro de córner dirigido a una zona; si se conecta, habilita un cabezazo."""
    zonas = {"primer_palo", "centro", "segundo_palo"}
    if self.estado != "en juego" or jugador is None or zona not in zonas:
      return {"ok": False, "mensaje": "No hay un córner válido para resolver."}
    equipo = getattr(jugador, "equipo", None)
    if equipo not in (self.local, self.visitante):
      return {"ok": False, "mensaje": "El jugador no participa de este partido."}
    companeros = [j for j in self.obtener_jugadores_disponibles(equipo) if j is not jugador]
    rival_equipo = self.visitante if equipo == self.local else self.local
    defensores = self.obtener_jugadores_disponibles(rival_equipo)
    if not companeros or not defensores:
      return {"ok": False, "mensaje": "No hay jugadores disponibles para disputar el centro."}
    objetivo = max(companeros, key=lambda j: j.obtener_estadistica("salto") + j.obtener_estadistica("fuerza"))
    defensor = max(defensores, key=lambda j: j.obtener_estadistica("salto") + j.obtener_estadistica("marca"))
    duelo = self.agregar_duelo(objetivo, defensor, "aereo")
    conectado = duelo.ganador is objetivo
    if conectado:
      self.objetivo_corner_pendiente = objetivo
    mensaje = (f"Córner al {zona.replace('_', ' ')}: {objetivo.nombre} ganó el duelo aéreo y puede definir."
      if conectado else f"Córner al {zona.replace('_', ' ')}: {defensor.nombre} despejó el centro.")
    self.eventos.append({"tipo": "corner", "minuto": self.minuto, "jugador": jugador, "objetivo": objetivo, "defensor": defensor, "zona": zona, "exito": conectado, "equipo": equipo, "mensaje": mensaje})
    self.registrar_participacion(jugador, "puntos", 0.10 if conectado else 0.02)
    self.calcular_resultado()
    respuesta = {"ok": True, "exito": conectado, "mensaje": mensaje, "resultado": self.resultado}
    if conectado:
      respuesta["continuacion"] = [("CABECEAR AL ARCO", "cabezazo")]
    return respuesta

  def resolver_penal(self, jugador, zona):
    """Resuelve un penal con dirección elegida por el usuario y duelo contra el arquero."""
    zonas = {
      "arriba_izquierda", "arriba_centro", "arriba_derecha",
      "medio_izquierda", "centro", "medio_derecha",
      "abajo_izquierda", "abajo_centro", "abajo_derecha"
    }
    if self.estado != "en juego" or jugador is None or zona not in zonas:
      return {"ok": False, "mensaje": "No hay un penal válido para resolver."}
    equipo = getattr(jugador, "equipo", None)
    if equipo not in (self.local, self.visitante):
      return {"ok": False, "mensaje": "El jugador no participa de este partido."}
    rival = self.visitante if equipo == self.local else self.local
    arquero = self.elegir_arquero(rival)
    if arquero is None:
      return {"ok": False, "mensaje": "El rival no tiene un arquero disponible."}

    precision = jugador.obtener_estadistica("precision")
    definicion = jugador.obtener_estadistica("definicion")
    reaccion = arquero.obtener_estadistica("reaccion")
    anticipacion = arquero.obtener_estadistica("anticipacion")
    # Los extremos y las esquinas son más difíciles de atajar, pero tienen un margen de error.
    esquina = "izquierda" in zona or "derecha" in zona
    altura = "arriba" in zona or "abajo" in zona
    probabilidad_gol = 0.76 + ((precision + definicion) - 100) / 450
    if esquina:
      probabilidad_gol += 0.07
    if altura:
      probabilidad_gol += 0.02
    probabilidad_gol -= (reaccion + anticipacion - 100) / 650
    probabilidad_gol = max(0.38, min(0.94, probabilidad_gol))
    gol = random.random() < probabilidad_gol
    if gol:
      self.agregar_gol(jugador, equipo)
      mensaje = f"¡GOOOL! {jugador.nombre} colocó el penal en {zona.replace('_', ' ')}."
      self.registrar_participacion(jugador, "puntos", 0.35)
    else:
      mensaje = f"¡Atajó el arquero! {jugador.nombre} eligió {zona.replace('_', ' ')}, pero el remate no terminó en gol."
      self.registrar_participacion(jugador, "puntos", -0.10)
      self.registrar_participacion(jugador, "remates_fallados", 1)
    self.eventos.append({
      "tipo": "penal", "minuto": self.minuto, "jugador": jugador,
      "arquero": arquero, "zona": zona, "gol": gol, "equipo": equipo,
      "mensaje": mensaje
    })
    self.calcular_resultado()
    return {"ok": True, "exito": gol, "mensaje": mensaje, "resultado": self.resultado}


  def avanzar_intervalo(self, minutos=5):
    """Avanza el reloj en bloques para permitir decisiones interactivas."""
    if self.estado == "pendiente":
      self.iniciar()
    if self.estado != "en juego":
      return {"terminado": True, "minuto": self.minuto}

    limite = 120 if self.tiempo_extra else 90
    for _ in range(max(1, int(minutos))):
      if self.minuto >= limite:
        break
      self.avanzar_minuto()

    self.calcular_resultado()
    if self.minuto >= limite:
      if self.minuto >= 90 and self.resultado[0] == self.resultado[1] and self.permite_prorroga and not self.tiempo_extra:
        self.iniciar_prorroga()
        return {"terminado": False, "prorroga": True, "minuto": self.minuto, "resultado": self.resultado}
      if self.tiempo_extra and self.minuto >= 120 and self.resultado[0] == self.resultado[1]:
        self.resolver_empate()
      self.finalizar()
      return {"terminado": True, "minuto": self.minuto, "resultado": self.resultado}
    return {"terminado": False, "minuto": self.minuto, "resultado": self.resultado}

  def simular(self):
    if self.estado != "pendiente":
      return

    self.iniciar()

    while self.minuto < 90:
      self.avanzar_minuto()

    self.calcular_resultado()

    if (
      self.resultado[0] == self.resultado[1]
      and self.permite_prorroga
    ):
      self.iniciar_prorroga()

      while self.minuto < 120:
        self.avanzar_minuto()

      self.calcular_resultado()

      if self.resultado[0] == self.resultado[1]:
        self.resolver_empate()

    self.finalizar()


  def sumar_puntos(self):
    if self.tipo != "liga":
      return

    if self.resultado[0] > self.resultado[1]:
      self.local.pts += 3
      self.local.g += 1
      self.visitante.p += 1

    elif self.resultado[1] > self.resultado[0]:
      self.visitante.pts += 3
      self.visitante.g += 1
      self.local.p += 1

    else:
      self.local.pts += 1
      self.visitante.pts += 1
      self.local.e += 1
      self.visitante.e += 1


  def actualizar_estadisticas_equipos(self):
    if self.tipo != "liga":
      return

    self.local.pj += 1
    self.visitante.pj += 1

    self.local.gf += len(
      self.goles_local
    )

    self.local.gc += len(
      self.goles_visitante
    )

    self.visitante.gf += len(
      self.goles_visitante
    )

    self.visitante.gc += len(
      self.goles_local
    )


  def finalizar(self):
    if self.estado != "en juego":
      return

    if (
      self.jugador_controlado is not None
      and self.jugador_controlado in self.local.jugadores + self.visitante.jugadores
      and self.jugador_controlado.esta_disponible()
    ):
      self.registrar_participacion(
        self.jugador_controlado,
        "puntos"
      )

    self.calcular_resultado()

    if self.ganador is None:
      self.determinar_ganador()

    self.estado = "terminado"

    for jugador in list(self.participantes):
      datos = self.actuaciones.get(jugador, {})
      nota = self.calcular_nota_jugador(jugador)
      jugador.registrar_actuacion(nota, datos)

      from logros import SistemaLogros
      SistemaLogros().actualizar(
        jugador,
        {
          "nota": nota,
          "goles": datos.get("goles", 0)
        }
      )

      for objeto in list(getattr(jugador, "equipamiento", {}).values()):
        if getattr(objeto, "activo", False):
          objeto.desgastar()
        if not getattr(objeto, "activo", False):
          jugador.equipamiento.pop(objeto.espacio, None)

    if self.jugador_controlado is not None and self.jugador_controlado in self.participantes:
      bonus_xp = round(8 * (self.multiplicador_xp - 1.0))
      if bonus_xp > 0:
        self.jugador_controlado.puntos_mejora += bonus_xp
        self.eventos.append({"tipo": "xp_multiplicador", "jugador": self.jugador_controlado,
          "minuto": self.minuto, "mensaje": f"Multiplicador de jugadas x{self.multiplicador_xp:.2f}: +{bonus_xp} XP."})
    for suspendido in self.suspendidos_al_inicio:
      suspendido.partidos_suspension = max(0, getattr(suspendido, "partidos_suspension", 0) - 1)
    self.sumar_puntos()
    self.actualizar_estadisticas_equipos()


