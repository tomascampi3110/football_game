import random
from jugador import Jugador
from equipo import Equipo
from competiciones import Liga, CopaClubes
from temporada import Temporada
from contratos import Contrato
from tienda import TiendaEquipamiento
from mejoras import MejoraCarrera
from economia import Inversion
from negociacion import NegociacionContrato
from casino import Casino
from personalizacion import personalizar_jugador, agregar_tatuaje
from retiro import SistemaRetiro
from clubes_reales import CLUBES_ARGENTINA
from catalogo_futbol import CLUBES as CATALOGO_CLUBES
from planteles_reales import PLANTELES_REALES


class Carrera:
  def __init__(self, jugador, temporada, liga):
    self.jugador = jugador
    self.temporada = temporada
    self.liga = liga
    self.casino = Casino()
    self.retiro = SistemaRetiro()
    self.historial = []
    self.ofertas_contractuales = []
    self.semanas_desde_charla_presidente = 99

  @staticmethod
  def potencial_inicial_segun_edad(edad, valoracion):
    """El potencial máximo tiende a ser mayor cuanto más joven es el jugador."""
    if edad <= 18:
      minimo, maximo = 84, 94
    elif edad <= 20:
      minimo, maximo = 80, 91
    elif edad <= 23:
      minimo, maximo = 75, 87
    elif edad <= 26:
      minimo, maximo = 70, 82
    elif edad <= 29:
      minimo, maximo = 65, 77
    else:
      minimo, maximo = 60, 72

    minimo = max(int(valoracion), minimo)
    maximo = max(minimo, maximo)
    return random.randint(minimo, maximo)

  @classmethod
  def nueva(cls, nombre, edad=None, posicion="delantero", anio=2026, opciones=None):
    tutorial_semanas = 4 if opciones is not None else 0
    opciones = opciones or {}
    equipos = []
    clubes = CLUBES_ARGENTINA
    nombres = [club["nombre"] for club in clubes]

    # La carrera del usuario siempre empieza a los 18 años.
    # Se conserva el parámetro edad por compatibilidad con las pruebas/versiones previas.
    edad_inicial = 18
    jugador_usuario = Jugador(nombre, edad_inicial, posicion)
    # El jugador controlado progresa gastando puntos de mejora; no tiene potencial.
    jugador_usuario.potencial = None
    jugador_usuario.desarrollo = 0
    jugador_usuario.dinero = 50000

    nombres_pila = ["Mateo", "Santiago", "Thiago", "Benjamín", "Joaquín", "Lautaro", "Bautista", "Franco", "Valentín", "Nicolás", "Tomás", "Facundo", "Agustín", "Bruno", "Dylan", "Máximo", "Ramiro", "Emiliano", "Julián", "Lucas", "Gabriel", "Nahuel", "Gonzalo", "Leandro", "Iván", "Federico", "Alan", "Kevin", "Ezequiel", "Matías"]
    apellidos = ["Gómez", "Fernández", "López", "Martínez", "Díaz", "Pérez", "Romero", "Sosa", "Álvarez", "Torres", "Ruiz", "Acosta", "Medina", "Herrera", "Castro", "Suárez", "Rojas", "Benítez", "Molina", "Ortiz", "Silva", "Vega", "Aguirre", "Cabrera", "Navarro", "Paz", "Ibarra", "Luna", "Quiroga", "Peralta"]
    for indice, nombre_equipo in enumerate(nombres):
      ficha_club = clubes[indice]
      entrenadores = {
        "Boca Juniors": "Rodolfo Arruabarrena",
        "River Plate": "Eduardo Coudet",
        "Racing Club": "Gustavo Costas",
        "Independiente": "Gustavo Quinteros",
        "San Lorenzo": "Damián Ayude",
        "Rosario Central": "Jorge Almirón",
        "Newell's Old Boys": "Frank Darío Kudelka",
        "Estudiantes": "Eduardo Domínguez",
        "Vélez Sarsfield": "Guillermo Barros Schelotto",
        "Talleres": "Carlos Tevez",
        "Belgrano": "Ricardo Zielinski",
        "Lanús": "Mauricio Pellegrino",
        "Huracán": "Diego Martínez",
        "Argentinos Juniors": "Nicolás Diez",
        "Banfield": "Pedro Troglio",
        "Defensa y Justicia": "Mariano Soso",
        "Platense": "Walter Zunino",
        "Unión": "Leonardo Madelón",
        "Instituto": "Daniel Oldrá",
        "Gimnasia y Esgrima La Plata": "Fernando Zaniratto",
      }
      equipo = Equipo(
        nombre_equipo,
        ficha_club["estadio"],
        entrenadores.get(nombre_equipo, f"Cuerpo técnico de {nombre_equipo}"),
        None
      )
      equipo.sigla = ficha_club["sigla"]
      equipo.ciudad = ficha_club["ciudad"]
      equipo.reputacion = ficha_club.get("valoracion", 55)
      equipo.ruta_escudo = f"assets/escudos/{ficha_club['sigla'].lower()}.png"
      equipo.presupuesto = random.randint(250000, 1500000)

      cantidad_npc = 18
      posiciones = ["arquero", "defensor", "mediocampista", "delantero"]
      plantilla_real = PLANTELES_REALES.get(nombre_equipo, [])

      # Los jugadores con ficha real se cargan primero; el resto del plantel
      # se completa con NPC para mantener el tamaño mínimo de una plantilla jugable.
      for numero, ficha_jugador in enumerate(plantilla_real):
        nombre_real, posicion_npc, edad_real, valoracion_objetivo = ficha_jugador
        npc = Jugador(nombre_real, edad_real, posicion_npc)
        for estadistica in npc.estadisticas:
          npc.estadisticas[estadistica] = max(25, min(98, int(random.gauss(valoracion_objetivo, 6))))
        npc.desarrollo = max(20, min(95, valoracion_objetivo))
        npc.calcular_valoracion()
        npc.valoracion = int(valoracion_objetivo)
        npc.potencial = cls.potencial_inicial_segun_edad(npc.edad, npc.valoracion)
        npc.es_jugador_real = True
        equipo.agregar_jugador(npc)

      numero = 0
      while len(equipo.jugadores) < cantidad_npc:
        posicion_npc = posiciones[numero % len(posiciones)]
        nombre_generado = f"{nombres_pila[(indice * 7 + numero * 3) % len(nombres_pila)]} {apellidos[(indice * 5 + numero * 11) % len(apellidos)]}"
        if any(j.nombre == nombre_generado for j in equipo.jugadores):
          numero += 1
          continue
        npc = Jugador(nombre_generado, random.randint(18, 34), posicion_npc)
        for estadistica in npc.estadisticas:
          npc.estadisticas[estadistica] = random.randint(35, 75)
        npc.desarrollo = random.randint(20, 80)
        npc.calcular_valoracion()
        npc.potencial = cls.potencial_inicial_segun_edad(npc.edad, npc.valoracion)
        npc.es_jugador_real = False
        equipo.agregar_jugador(npc)
        numero += 1

      equipo.actualizar_valoracion()
      equipos.append(equipo)

    liga = Liga("Liga Profesional Argentina", equipos, 1)
    for equipo in equipos:
      equipo.liga = liga

    # Las ligas opcionales usan clubes/estadios/DT del catálogo y planteles ficticios
    # generados de forma coherente para que puedan jugarse sin depender de servicios externos.
    equipos_por_competicion = {"Liga Profesional Argentina": equipos}
    ligas_extra = []
    def crear_equipo_catalogo(ficha, indice_global, nombre_liga):
      nombre_equipo, estadio, dt, reputacion = ficha
      equipo = Equipo(nombre_equipo, estadio, dt, None)
      equipo.reputacion = reputacion
      equipo.presupuesto = int(300000 + reputacion * reputacion * 240)
      equipo.sigla = "".join(parte[0] for parte in nombre_equipo.split()[:3]).upper()
      equipo.ciudad = "Internacional"
      equipo.ruta_escudo = ""
      plantilla_real = PLANTELES_REALES.get(nombre_equipo, [])
      for nombre_real, posicion_real, edad_real, valoracion_objetivo in plantilla_real:
        npc = Jugador(nombre_real, edad_real, posicion_real)
        for estadistica in npc.estadisticas:
          npc.estadisticas[estadistica] = max(25, min(98, int(random.gauss(valoracion_objetivo, 6))))
        npc.calcular_valoracion()
        npc.valoracion = int(valoracion_objetivo)
        npc.potencial = cls.potencial_inicial_segun_edad(npc.edad, npc.valoracion)
        npc.es_jugador_real = True
        equipo.agregar_jugador(npc)
      numero = 0
      while len(equipo.jugadores) < 18:
        posicion_npc = ["arquero", "defensor", "mediocampista", "delantero"][numero % 4]
        nombre_generado = f"{nombres_pila[(indice_global * 3 + numero * 7) % len(nombres_pila)]} {apellidos[(indice_global * 5 + numero * 11) % len(apellidos)]}"
        if any(j.nombre == nombre_generado for j in equipo.jugadores):
          numero += 1
          continue
        npc = Jugador(nombre_generado, random.randint(18, 34), posicion_npc)
        for estadistica in npc.estadisticas:
          npc.estadisticas[estadistica] = max(30, min(92, int(random.gauss(reputacion - 10, 8))))
        npc.calcular_valoracion()
        npc.potencial = cls.potencial_inicial_segun_edad(npc.edad, npc.valoracion)
        npc.es_jugador_real = False
        equipo.agregar_jugador(npc)
        numero += 1
      equipo.actualizar_valoracion()
      return equipo

    indice_global = len(equipos)
    if opciones.get("segunda_division", False):
      fichas = CATALOGO_CLUBES.get("Argentina · Primera Nacional", [])
      equipos_b = [crear_equipo_catalogo(f, indice_global + i, "Primera Nacional") for i, f in enumerate(fichas)]
      liga_b = Liga("Primera Nacional Argentina", equipos_b, 2)
      for equipo in equipos_b:
        equipo.liga = liga_b
      ligas_extra.append(liga_b)
      equipos_por_competicion[liga_b.nombre] = equipos_b
      indice_global += len(equipos_b)

    equipos_brasil = []
    if opciones.get("ligas_extras", False):
      for nombre_liga in ["Brasil · Série A", "Brasil · Série B", "Inglaterra · Premier League", "Inglaterra · Championship", "España · LaLiga", "España · Segunda División", "Italia · Serie A", "Alemania · Bundesliga", "Francia · Ligue 1"]:
        fichas = CATALOGO_CLUBES.get(nombre_liga, [])
        if not fichas:
          continue
        equipos_liga = [crear_equipo_catalogo(f, indice_global + i, nombre_liga) for i, f in enumerate(fichas)]
        liga_extra = Liga(nombre_liga, equipos_liga, 1 if "Segunda" not in nombre_liga and "Série B" not in nombre_liga and "Championship" not in nombre_liga else 2)
        for equipo in equipos_liga:
          equipo.liga = liga_extra
        ligas_extra.append(liga_extra)
        equipos_por_competicion[nombre_liga] = equipos_liga
        if nombre_liga == "Brasil · Série A":
          equipos_brasil = equipos_liga
        indice_global += len(equipos_liga)

    equipo_inicial = equipos[-1]
    equipo_inicial.presupuesto = min(equipo_inicial.presupuesto, 350000)
    equipo_inicial.actualizar_valoracion()

    temporada = Temporada(anio)
    temporada.agregar_competicion(liga)
    for liga_extra in ligas_extra:
      temporada.agregar_competicion(liga_extra)

    if opciones.get("copas_grandes", False):
      participantes = equipos[:8] + (equipos_brasil[:8] if equipos_brasil else equipos[8:16])
      copa = CopaClubes("Copa Libertadores", participantes, cantidad_grupos=4)
      temporada.agregar_competicion(copa)

    temporada.establecer_jugador_usuario(jugador_usuario)
    temporada.iniciar()
    # Tutorial de cuatro semanas sin partidos: desplazamos el calendario completo.
    if tutorial_semanas:
      temporada.calendario = {semana + tutorial_semanas: dias for semana, dias in temporada.calendario.items()}
      temporada.duracion += tutorial_semanas
    temporada.bolsa_sponsors.actualizar(1)
    temporada.bolsa_equipamiento.actualizar(1)

    carrera = cls(jugador_usuario, temporada, liga)
    carrera.opciones_competicion = dict(opciones)
    carrera.semanas_tutorial = tutorial_semanas
    carrera.equipos_por_competicion = equipos_por_competicion
    # La primera semana es de bienvenida: las ofertas llegan al avanzar, no al crear la partida.
    return carrera

  def jugar_siguiente_semana(self):
    if self.temporada.estado != "en juego":
      return {"ok": False, "mensaje": "La temporada ya terminó."}

    pendientes = [
      item for item in self.temporada.eventos_sociales_pendientes
      if not item["evento"].resuelto
    ]
    self.temporada.eventos_sociales_pendientes = pendientes
    if pendientes:
      return {
        "ok": False,
        "requiere_evento": True,
        "evento": pendientes[0]["evento"],
        "mensaje": "Tenés una notificación pendiente. Resolvela antes de avanzar."
      }

    semana_jugada = self.temporada.semana
    partidos = self.temporada.obtener_partidos_semana(semana_jugada)
    pendientes = [partido for partido in partidos if partido.estado == "pendiente"]

    # Tutorial de cuatro semanas: se avanza la carrera, pero no se simula fútbol.
    if semana_jugada <= getattr(self, "semanas_tutorial", 0):
      self.jugador.procesar_semana()
      self.temporada.avanzar_semana()
      self.semanas_desde_charla_presidente += 1
      self.otorgar_puntos_mejora(semana_jugada)
      nuevas_ofertas = self.generar_ofertas_contractuales() if semana_jugada == 4 and self.jugador.contrato is None else []
      resumen = {
        "ok": True, "tutorial": True, "semana": semana_jugada, "partidos": 0,
        "nota": None, "dinero": self.jugador.dinero,
        "semana_siguiente": self.temporada.semana,
        "ofertas_nuevas": len(nuevas_ofertas), "apuestas_liquidadas": [],
        "ventana_mercado": False, "estado": self.temporada.estado
      }
      self.historial.append(resumen)
      return resumen

    self.temporada.simular_semana()
    liquidaciones_apuestas = []
    for partido in partidos:
      if getattr(partido, "estado", None) == "terminado":
        liquidaciones_apuestas.extend(self.casino.liquidar_apuestas_partido(partido, self.jugador))
    if self.jugador.equipo is None:
      self.jugador.procesar_semana()
    self.temporada.avanzar_semana()
    self.semanas_desde_charla_presidente += 1
    self.otorgar_puntos_mejora(semana_jugada)
    if self.jugador.contrato is None or not self.jugador.contrato.esta_vigente():
      if ((getattr(self, "semanas_tutorial", 0) == 0 and (semana_jugada == 1 or semana_jugada % 2 == 0)) or (semana_jugada > getattr(self, "semanas_tutorial", 0) and semana_jugada % 2 == 0)):
        nuevas_ofertas = self.generar_ofertas_contractuales()
      else:
        nuevas_ofertas = []
    else:
      nuevas_ofertas = []

    resumen = {
      "ok": True,
      "semana": semana_jugada,
      "partidos": len(pendientes),
      "nota": self.jugador.historial_notas[-1] if self.jugador.historial_notas else None,
      "dinero": self.jugador.dinero,
      "semana_siguiente": self.temporada.semana,
      "ofertas_nuevas": len(nuevas_ofertas),
      "apuestas_liquidadas": liquidaciones_apuestas,
      "ventana_mercado": self.temporada.semana in self.temporada.mercado_pases.VENTANAS_MERCADO,
      "estado": self.temporada.estado
    }
    self.historial.append(resumen)
    return resumen


  def simular_hasta_fin_temporada(self, max_semanas=80):
    """Simula automáticamente la carrera hasta el cierre de temporada."""
    semanas = 0
    while self.temporada.estado == "en juego" and semanas < max_semanas:
      resultado = self.jugar_siguiente_semana()
      if resultado.get("requiere_evento"):
        evento = resultado["evento"]
        opciones_evento = getattr(evento, "opciones", [])
        if opciones_evento:
          evento.elegir(self.jugador, 0)
          continue
        break
      if not resultado.get("ok"):
        break
      semanas += 1
    if self.temporada.estado == "terminada":
      return {"ok": True, "semanas": semanas, "mensaje": f"Temporada simulada hasta el final en {semanas} semanas procesadas. Revisá la tabla y los resultados."}
    return {"ok": False, "semanas": semanas, "mensaje": f"Simulación detenida en semana {self.temporada.semana}; la temporada sigue en curso."}

  def otorgar_puntos_mejora(self, semana):
    """Entrega puntos acumulables según el rendimiento y el nivel de la carrera."""
    nota = self.jugador.historial_notas[-1] if self.jugador.historial_notas else 5.0
    # La progresión debe permitir varias mejoras significativas por temporada.
    # Base semanal + bonificaciones por rendimiento y pertenecer a un club.
    base = 8
    if nota >= 8:
      base += 5
    elif nota >= 7:
      base += 3
    elif nota < 5:
      base -= 2
    equipo = self.jugador.equipo
    if equipo is not None:
      base += 2 if equipo.valoracion >= 65 else 1
    # Estar libre no bloquea el desarrollo: se mantiene la base completa.
    base = max(5, base)
    self.jugador.puntos_mejora += base
    return base

  def generar_ofertas_contractuales(self, inicial=False):
    """Crea ofertas de clubes que el jugador puede aceptar o rechazar."""
    if self.jugador.contrato is not None and self.jugador.contrato.esta_vigente():
      return []
    equipos = [e for e in self.liga.equipos if self.jugador not in e.jugadores]
    # No insistir siempre con el mismo club después de que el jugador rechaza una oferta.
    clubes_ya_ofrecidos = {id(o["equipo"]) for o in self.ofertas_contractuales if o["estado"] in ("rechazada", "aceptada")}
    equipos = [e for e in equipos if id(e) not in clubes_ya_ofrecidos]
    equipos.sort(key=lambda e: abs(e.valoracion - self.jugador.valoracion))
    # Ofrecer varias alternativas por tanda para que la carrera no quede atada a un único club.
    cantidad = min(3, len(equipos))
    nuevas = []
    for equipo in equipos[:cantidad]:
      if any(o["equipo"] is equipo and o["estado"] == "pendiente" for o in self.ofertas_contractuales):
        continue
      # El salario considera el nivel del club, además de la valoración del jugador.
      nivel_club = max(35, min(90, getattr(equipo, "reputacion", getattr(equipo, "valoracion", 55))))
      multiplicador_club = 0.45 + (nivel_club / 100) ** 2 * 1.35
      variacion = random.uniform(0.95, 1.05)
      salario_base = max(1000, self.jugador.valoracion * 70)
      salario = max(1000, int(salario_base * multiplicador_club * variacion))
      oferta = {"equipo": equipo, "salario": salario, "duracion": 52, "estado": "pendiente"}
      self.ofertas_contractuales.append(oferta)
      nuevas.append(oferta)
    return nuevas

  def responder_oferta_contractual(self, oferta, aceptar):
    if oferta not in self.ofertas_contractuales or oferta["estado"] != "pendiente":
      return {"ok": False, "mensaje": "Esta oferta ya no está disponible."}
    if not aceptar:
      oferta["estado"] = "rechazada"
      return {"ok": True, "mensaje": "Oferta rechazada."}
    if self.jugador.equipo is not None:
      self.jugador.equipo.eliminar_jugador(self.jugador)
    equipo = oferta["equipo"]
    equipo.agregar_jugador(self.jugador)
    self.jugador.contrato = Contrato(self.jugador, equipo, oferta["salario"], oferta["duracion"])
    oferta["estado"] = "aceptada"
    self.liga.recalcular_tabla() if hasattr(self.liga, "recalcular_tabla") else None
    return {"ok": True, "mensaje": f"Firmaste con {equipo.nombre} por ${oferta['salario']:,} semanales."}

  def negociar_contrato(self):
    equipo = self.jugador.equipo
    if equipo is None:
      return None
    salario = max(1000, self.jugador.valoracion * 100)
    return NegociacionContrato(self.jugador, equipo, salario, 52)

  def solicitar_renovacion(self):
    negociacion = self.negociar_contrato()
    return negociacion.pedir_renovacion(), negociacion

  def solicitar_lista_transferibles(self):
    import random

    jugador = self.jugador
    contrato = jugador.contrato
    probabilidad = 0.50

    if jugador.historial_notas:
      promedio = sum(jugador.historial_notas[-5:]) / len(jugador.historial_notas[-5:])
      if promedio < 5:
        probabilidad += 0.20
      elif promedio >= 8:
        probabilidad -= 0.15

    if contrato is not None and contrato.esta_vigente():
      if contrato.semanas_restantes > 39:
        probabilidad -= 0.15
      elif contrato.semanas_restantes <= 12:
        probabilidad += 0.15

    probabilidad -= max(0, jugador.vinculos.get("club", 50) - 50) / 300
    probabilidad = max(0.10, min(0.90, probabilidad))

    if random.random() <= probabilidad:
      jugador.solicitar_lista_transferibles()
      return {
        "ok": True,
        "mensaje": "El club aceptó tu solicitud. Podés recibir ofertas en la próxima ventana de mercado."
      }

    jugador.vinculos["club"] = max(0, jugador.vinculos.get("club", 50) - 3)
    return {
      "ok": False,
      "mensaje": "El club rechazó tu solicitud por ahora. La relación con la dirigencia se resintió un poco."
    }

  def comprar_equipamiento(self, identificador):
    return TiendaEquipamiento.comprar_y_equipar(
      self.jugador,
      identificador
    )

  def comprar_oferta_equipamiento(self, indice):
    return self.temporada.bolsa_equipamiento.comprar(
      self.jugador,
      indice
    )

  def comprar_mejora(self, identificador):
    return MejoraCarrera.comprar(self.jugador, identificador)

  def comprar_inversion(self, identificador):
    if identificador not in Inversion.CATALOGO:
      return {"ok": False, "mensaje": "La inversión seleccionada no existe."}

    oferta = Inversion.CATALOGO[identificador]
    if any(getattr(inv, "identificador", None) == identificador for inv in self.jugador.inversiones):
      return {"ok": False, "mensaje": "Ya tenés esta inversión. Mejorala hasta el nivel máximo en lugar de comprar otra."}
    if self.jugador.valoracion < oferta.get("valoracion_minima", 0):
      return {"ok": False, "mensaje": f"Necesitás valoración {oferta['valoracion_minima']} para acceder a esta inversión."}
    patrimonio = self.jugador.dinero + sum(getattr(inv, "dinero_invertido", 0) for inv in self.jugador.inversiones)
    if patrimonio < oferta.get("patrimonio_minimo", 0):
      return {"ok": False, "mensaje": f"Necesitás un patrimonio de ${oferta['patrimonio_minimo']:,} para acceder a esta inversión."}
    if self.jugador.dinero < oferta["costo"]:
      return {"ok": False, "mensaje": "No tenés dinero suficiente para esa inversión."}

    inversion = Inversion(
      oferta["nombre"],
      oferta["tipo"],
      oferta["costo"],
      oferta["ingreso_semanal"]
    )
    if not self.jugador.agregar_inversion(inversion):
      return {"ok": False, "mensaje": "No se pudo registrar la inversión."}

    self.jugador.dinero -= oferta["costo"]
    return {"ok": True, "mensaje": f"Inversión adquirida: {oferta['nombre']}."}

  def personalizar(self, atributo, valor):
    return personalizar_jugador(self.jugador, atributo, valor)

  def comprar_tatuaje(self, nombre, precio):
    return agregar_tatuaje(self.jugador, nombre, precio)

  def aceptar_sponsor(self, indice):
    if not 0 <= indice < len(self.temporada.bolsa_sponsors.ofertas):
      return False

    oferta = self.temporada.bolsa_sponsors.ofertas[indice]
    return oferta.aceptar(self.jugador)

  def resolver_evento_social(self, evento, indice_opcion):
    resultado = evento.elegir(self.jugador, indice_opcion)
    if resultado["ok"]:
      self.temporada.eventos_sociales_pendientes = [
        item for item in self.temporada.eventos_sociales_pendientes
        if item["evento"] is not evento
      ]
    return resultado

  def extender_carrera(self):
    return self.retiro.extender_carrera(self.jugador)

  def retirarse(self):
    if not self.retiro.debe_retirarse(self.jugador):
      return {
        "ok": False,
        "mensaje": f"Tu edad de retiro es {self.jugador.edad_retiro}. Todavía podés seguir jugando."
      }

    self.retiro.finalizar_carrera(self.jugador)
    self.temporada.estado = "terminada"
    return {
      "ok": True,
      "mensaje": "Te retiraste del fútbol profesional. La carrera quedó finalizada."
    }

  def estado_resumido(self):
    equipo = self.jugador.equipo.nombre if self.jugador.equipo else "Sin club"
    contrato = self.jugador.contrato
    salario = contrato.salario_semanal if contrato and contrato.esta_vigente() else 0
    restante = contrato.semanas_restantes if contrato and contrato.esta_vigente() else 0

    return {
      "nombre": self.jugador.nombre,
      "edad": self.jugador.edad,
      "posicion": self.jugador.posicion,
      "valoracion": self.jugador.valoracion,
      "forma": self.jugador.forma,
      "dinero": self.jugador.dinero,
      "equipo": equipo,
      "salario": salario,
      "semanas_contrato": restante,
      "semana": self.temporada.semana,
      "temporada": self.temporada.anio,
      "estado_temporada": self.temporada.estado
    }
