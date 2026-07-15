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
        print(f"√ {jugador.gamertag} se unió al equipo {self.nombre}")

    def registrar_resultado(self, gano: bool):
        if gano:
            self.ganados += 1
        else:
            self.perdidos += 1

    def __str__(self):
        return f"ˆ Equipo {self.nombre} | Jugadores: {len(self.jugadores)} | Récord: {self.ganados}V-{self.perdidos}D"


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
        self.equipos = {}
        self.partidos = []

    def agregar_equipo(self, equipo: Equipo):
        if equipo.nombre not in self.equipos:
            self.equipos[equipo.nombre] = equipo
        else:
            print(f"El equipo {equipo.nombre} ya está registrado en el torneo.")

    def buscar_equipo(self, nombre_equipo: str) -> Equipo:
        return self.equipos.get(nombre_equipo, None)

    def programar_partido(self, equipo1_nombre: str, equipo2_nombre: str) -> Partido:
        eq1 = self.buscar_equipo(equipo1_nombre)
        eq2 = self.buscar_equipo(equipo2_nombre)
        
        if eq1 and eq2:
            nuevo_partido = Partido(eq1, eq2)
            self.partidos.append(nuevo_partido)
            return nuevo_partido
        else:
            print("Error: Uno o ambos equipos no se encuentran registrados.")
            return None

    def tabla_posiciones(self):
        print(f"\n=== TABLA DE POSICIONES - {self.nombre.upper()} ===")
        equipos_ordenados = sorted(self.equipos.values(), key=lambda x: (x.ganados, -x.perdidos), reverse=True)
        for idx, eq in enumerate(equipos_ordenados, 1):
            print(f"{idx}. {eq.nombre} | Récord: {eq.ganados}V-{eq.perdidos}D | Integrantes: {len(eq.jugadores)}")
        print("=========================================\n")

    def guardar_datos(self, archivo: str = "torneo_datos.json"):
        try:
            datos_serializados = {
                "nombre_torneo": self.nombre,
                "equipos": []
            }
            
            for eq in self.equipos.values():
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
            print(f"√ Estado del torneo guardado exitosamente en '{archivo}'.")
            
        except IOError as e:
            print(f"Error de E/S al intentar escribir en el archivo {archivo}: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al guardar los datos: {e}")

    def cargar_datos(self, archivo: str = "torneo_datos.json"):
        try:
            if not os.path.exists(archivo):
                print(f"El archivo '{archivo}' no existe. Iniciando torneo vacío.")
                return

            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                
            self.nombre = datos.get("nombre_torneo", self.nombre)
            self.equipos = {}
            self.partidos = []
            
            for data_eq in datos.get("equipos", []):
                nuevo_equipo = Equipo(data_eq["nombre"])
                nuevo_equipo.ganados = data_eq["ganados"]
                nuevo_equipo.perdidos = data_eq["perdidos"]
                
                for data_jug in data_eq.get("jugadores", []):
                    nuevo_jugador = Jugador(data_jug["nombre"], data_jug["gamertag"], nuevo_equipo.nombre)
                    nuevo_jugador.puntos = data_jug["puntos"]
                    nuevo_equipo.jugadores.append(nuevo_jugador)
                    
                self.equipos[nuevo_equipo.nombre] = nuevo_equipo
                
            print(f"√ Estado del torneo cargado exitosamente desde '{archivo}'.")
            
        except json.JSONDecodeError:
            print(f"Error: El archivo '{archivo}' está dañado o no posee un formato JSON válido.")
        except IOError as e:
            print(f"Error de E/S al intentar leer el archivo {archivo}: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado al cargar los datos: {e}")


if __name__ == "__main__":
    print("=== INICIANDO SISTEMA DE GESTIÓN DE ESPORTS ===")
    
    mi_torneo = Torneo("Interuniversitario de Esports 2026")
    
    print("\n--- Creación de Equipos ---")
    unibe = Equipo("UNIBE")
    pucmm = Equipo("PUCMM")
    
    mi_torneo.agregar_equipo(unibe)
    mi_torneo.agregar_equipo(pucmm)
    
    print("\n--- Registro de Jugadores ---")
    brian = Jugador("Brian Melo", "MeloCS")
    andres = Jugador("Andres Sanches", "Fat_")
    
    unibe.agregar_jugador(brian)
    pucmm.agregar_jugador(andres)
    
    print(brian)
    print(andres)
    
    print("\n--- Programación de Partidos ---")
    match_clasico = mi_torneo.programar_partido("UNIBE", "PUCMM")
    print(match_clasico)
    
    print("\n--- Resolviendo Marcadores (Ejecución de Match) ---")
    if match_clasico:
        match_clasico.registrar_marcador(3, 1)
        brian.sumar_puntos(30)
        print(match_clasico)
        
    print("\n--- Estado de las Escuadras Post-Match ---")
    print(unibe)
    print(pucmm)
    
    mi_torneo.tabla_posiciones()
    
    print("--- Probando Persistencia de Datos (Escritura y Lectura) ---")
    nombre_archivo_test = "torneo_datos.json"
    
    mi_torneo.guardar_datos(nombre_archivo_test)
    
    torneo_clonado = Torneo("Torneo Temporal Vacío")
    torneo_clonado.cargar_datos(nombre_archivo_test)
    
    print(f"\nNombre del torneo restaurado: {torneo_clonado.nombre}")
    torneo_clonado.tabla_posiciones()
    
    print("--- Verificación de Robustez de Reglas del Negocio (Tratamiento de Errores) ---")
    try:
        print("Intentando registrar un marcador con empate (No permitido)...")
        partido_invalido = Partido(unibe, pucmm)
        partido_invalido.registrar_marcador(2, 2)
    except AssertionError as error:
        print(f"Capturado correctamente por seguridad del sistema: [AssertionError] -> {error}")

    try:
        print("\nIntentando asignar puntuación negativa individual...")
        brian.sumar_puntos(-5)
    except AssertionError as error:
        print(f"Capturado correctamente por seguridad del sistema: [AssertionError] -> {error}")
        
    print("\n=== PROGRAMA FINALIZADO SIN ERRORES CRÍTICOS ===")