import json
import os

class Jugador:
    def __init__(self, nombre: str, gamertag: str, equipo: str = None):
        self.nombre = nombre
        self.gamertag = gamertag
        self.equipo = equipo
        self.puntos = 0

    def sumar_puntos(self, puntos_ganados: int):
        assert puntos_ganados >= 0, "Los puntos ganados no pueden ser negativos."
        self.puntos += puntos_ganados
        print(f"{self.gamertag} sumó {puntos_ganados} puntos. Total: {self.puntos}")

    def __str__(self):
        eq_display = self.equipo if self.equipo else "Agente libre"
        return f"{self.gamertag} ({self.nombre}) — Equipo: {eq_display} | Puntos: {self.puntos}"


class Equipo:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.jugadores = []
        self.ganados = 0
        self.perdidos = 0

    def agregar_jugador(self, jugador: Jugador):
        assert len(self.jugadores) < 5, "El equipo ya alcanzó el máximo de 5 jugadores."
        jugador.equipo = self.nombre
        self.jugadores.append(jugador)
        print(f"[OK] {jugador.gamertag} se unió al equipo {self.nombre}")

    def registrar_resultado(self, gano: bool):
        if gano:
            self.ganados += 1
        else:
            self.perdidos += 1

    def __str__(self):
        return f"Equipo {self.nombre} | Jugadores: {len(self.jugadores)} | Récord: {self.ganados}V-{self.perdidos}D"


class Partido:
    def __init__(self, equipo1: Equipo, equipo2: Equipo):
        self.equipo1 = equipo1
        self.equipo2 = equipo2
        self.marcador1 = 0
        self.marcador2 = 0
        self.jugado = False
        self.ganador = None

    def registrar_marcador(self, marcador1: int, marcador2: int):
        assert marcador1 >= 0 and marcador2 >= 0, "El marcador no puede ser negativo."
        assert marcador1 != marcador2, "Este torneo no permite empates."
        
        self.marcador1 = marcador1
        self.marcador2 = marcador2
        self.jugado = True
        
        if marcador1 > marcador2:
            self.ganador = self.equipo1
            self.equipo1.registrar_resultado(gano=True)
            self.equipo2.registrar_resultado(gano=False)
        else:
            self.ganador = self.equipo2
            self.equipo1.registrar_resultado(gano=False)
            self.equipo2.registrar_resultado(gano=True)

    def __str__(self):
        if not self.jugado:
            return f"  {self.equipo1.nombre} vs {self.equipo2.nombre} — Partido pendiente"
        else:
            return f"X {self.equipo1.nombre} {self.marcador1} - {self.marcador2} {self.equipo2.nombre} | Ganador: {self.ganador.nombre}"


class Torneo:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.equipos = []
        self.partidos = []

    def agregar_equipo(self, equipo: Equipo):
        if self.buscar_equipo(equipo.nombre) is not None:
            print("/!\ Ya existe un equipo con ese nombre.")
        else:
            self.equipos.append(equipo)
            print(f"@ Equipo agregado al torneo: {equipo.nombre}")

    def buscar_equipo(self, nombre_equipo: str) -> Equipo:
        for eq in self.equipos:
            if eq.nombre == nombre_equipo:
                return eq
        return None

    def programar_partido(self, nombre_equipo1: str, nombre_equipo2: str) -> Partido:
        try:
            eq1 = self.buscar_equipo(nombre_equipo1)
            eq2 = self.buscar_equipo(nombre_equipo2)
            
            if not eq1 or not eq2:
                raise ValueError(f"Uno o ambos equipos no están registrados: {nombre_equipo1}, {nombre_equipo2}")
            
            nuevo_partido = Partido(eq1, eq2)
            self.partidos.append(nuevo_partido)
            print(f"@ Partido programado exitosamente: {eq1.nombre} vs {eq2.nombre}")
            return nuevo_partido
        except ValueError as error:
            print(f"X {error}")
            return None

    def tabla_posiciones(self):
        print(f"\n=== TABLA DE POSICIONES - {self.nombre.upper()} ===")
        equipos_ordenados = sorted(self.equipos, key=lambda x: x.ganados, reverse=True)
        for idx, eq in enumerate(equipos_ordenados, 1):
            print(f"{idx}º {eq}")
        print("=========================================\n")

    def guardar_datos(self, archivo: str = "torneo_datos.json"):
        try:
            datos_serializados = {
                "nombre_torneo": self.nombre,
                "equipos": []
            }
            
            for eq in self.equipos:
                info_equipo = {
                    "nombre": eq.nombre,
                    "ganados": eq.ganados,
                    "perdidos": eq.perdidos,
                    "jugadores": [
                        {
                            "nombre": j.nombre,
                            "gamertag": j.gamertag,
                            "puntos": j.puntos
                        } for j in eq.jugadores
                    ]
                }
                datos_serializados["equipos"].append(info_equipo)
                
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_serializados, f, indent=4, ensure_ascii=False)
            print("> Datos del torneo guardados exitosamente.")
            
        except (IOError, OSError) as error:
            print(f"X Error al guardar los datos: {error}")

    def cargar_datos(self, archivo: str = "torneo_datos.json"):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
            self.nombre = datos.get("nombre_torneo", self.nombre)
            self.equipos = []
            self.partidos = []
            
            for data_eq in datos.get("equipos", []):
                nuevo_equipo = Equipo(data_eq["nombre"])
                nuevo_equipo.ganados = data_eq["ganados"]
                nuevo_equipo.perdidos = data_eq["perdidos"]
                
                for data_jug in data_eq.get("jugadores", []):
                    nuevo_jugador = Jugador(data_jug["nombre"], data_jug["gamertag"], nuevo_equipo.nombre)
                    nuevo_jugador.puntos = data_jug["puntos"]
                    nuevo_equipo.jugadores.append(nuevo_jugador)
                    
                self.equipos.append(nuevo_equipo)
                
            print(f"> Datos cargados exitosamente: {len(self.equipos)} equipos.")
            
        except FileNotFoundError:
            print("X No se encontró el archivo de datos. Se iniciará un torneo vacío.")
        except json.JSONDecodeError:
            print("X El archivo de datos está corrupto o mal formado.")
        except (IOError, OSError) as error:
            print(f"X Error al cargar los datos: {error}")


if __name__ == "__main__":
    print("=== INICIANDO SISTEMA DE GESTIÓN DE ESPORTS ===")
    
    # 1. Crear el torneo y cargar datos previos
    torneo = Torneo("Copa UNIBE Esports")
    
    # 2. Intentar cargar_datos() al inicio (para probar el caso de archivo inexistente)
    torneo.cargar_datos()
    
    # 3. Crear equipos y jugadores; agregarlos al torneo
    print("\n--- Creación de Equipos y Jugadores ---")
    eq_unibe = Equipo("Unibe")
    eq_barna = Equipo("Barna")
    eq_pucmm = Equipo("Pucmm")
    eq_intec = Equipo("Intec")
    
    torneo.agregar_equipo(eq_unibe)
    torneo.agregar_equipo(eq_barna)
    torneo.agregar_equipo(eq_pucmm)
    torneo.agregar_equipo(eq_intec)
    
    # Agregar al menos 2 jugadores por equipo
    eq_unibe.agregar_jugador(Jugador("Andres Sanchez", "Fat"))
    eq_unibe.agregar_jugador(Jugador("Brian Melo", "Garcia"))
    
    eq_barna.agregar_jugador(Jugador("Jose Pereda", "Alfredo"))
    eq_barna.agregar_jugador(Jugador("Michael Bittar", "Elias"))
    
    eq_pucmm.agregar_jugador(Jugador("Jose Aristides", "Ciprian"))
    eq_pucmm.agregar_jugador(Jugador("Diego Castellanos", "Padilla"))
    
    eq_intec.agregar_jugador(Jugador("Juanico Cedano", "Comarazamy"))
    eq_intec.agregar_jugador(Jugador("Juan Elias", "Curiel"))
    
    # 4. Programar partidos y registrar marcadores (sin empates)
    print("\n--- Programación de Partidos ---")
    partido1 = torneo.programar_partido("Unibe", "Barna")
    partido2 = torneo.programar_partido("Pucmm", "Intec")
    partido3 = torneo.programar_partido("Unibe", "Pucmm")
    
    print("\n--- Registro de Resultados ---")
    if partido1:
        partido1.registrar_marcador(3, 1)
    if partido2:
        partido2.registrar_marcador(2, 3)
    if partido3:
        partido3.registrar_marcador(3, 0)
        
    # 5. Demostrar los tres casos de error controlado
    print("\n--- Demostrando Casos de Error Controlado ---")
    
    # Caso 1: Equipo inexistente
    print("\n[Caso de Error 1] Intentando programar partido con un equipo que no existe:")
    torneo.programar_partido("Unibe", "BarnaInexistentes")
    
    # Caso 2: Empate atrapado con try/except
    print("\n[Caso de Error 2] Intentando registrar un marcador con empate (No permitido):")
    try:
        if partido1:
            partido1.registrar_marcador(2, 2)
    except AssertionError as error:
        print(f"X Error de validación: {error}")
        
    # Caso 3: Cupo de jugadores atrapado con try/except
    print("\n[Caso de Error 3] Intentando agregar un sexto jugador a un mismo equipo:")
    try:
        # Ya tiene 2 jugadores, agregamos 3 más para llegar a 5
        eq_unibe.agregar_jugador(Jugador("Player 3", "P3"))
        eq_unibe.agregar_jugador(Jugador("Player 4", "P4"))
        eq_unibe.agregar_jugador(Jugador("Player 5", "P5"))
        # El sexto debe fallar
        print("Intentando agregar el sexto jugador...")
        eq_unibe.agregar_jugador(Jugador("Player 6", "P6"))
    except AssertionError as error:
        print(f"X Error de validación: {error}")
        
    # 6. Mostrar tabla de posiciones
    torneo.tabla_posiciones()
    
    # 7. Guardar los datos y cargarlos nuevamente para verificar
    print("--- Guardado y Carga de Persistencia ---")
    torneo.guardar_datos()
    
    print("\nVerificando carga de los datos guardados en una nueva instancia:")
    nuevo_torneo = Torneo("Copa UNIBE Esports (Cargado)")
    nuevo_torneo.cargar_datos()
    nuevo_torneo.tabla_posiciones()
    
    print("=== PROGRAMA FINALIZADO SIN ERRORES CRÍTICOS ===")
