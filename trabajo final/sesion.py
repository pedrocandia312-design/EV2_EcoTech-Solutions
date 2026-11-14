import time

TIEMPO_MAXIMO_INACTIVIDAD = 300   # 5 minutos sin hacer nada y se cierra la sesion
MAXIMO_CONSULTAS = 10             # consultas permitidas por sesion
ESPERA_MINIMA = 2                 # segundos entre una consulta y otra

class Sesion:
    """Controla cuanto tiempo y cuanto puede usar las APIs un usuario ya autenticado"""

    def __init__(self, usuario):
        self.__usuario = usuario
        self.__ultima_actividad = time.time()
        self.__ultima_consulta = 0
        self.__consultas = 0

    def get_usuario(self):
        return self.__usuario

    def esta_activa(self):
        return time.time() - self.__ultima_actividad < TIEMPO_MAXIMO_INACTIVIDAD

    def actividad(self):
        self.__ultima_actividad = time.time()

    def permitir_consulta(self):
        if not self.esta_activa():
            return (False, "La sesion expiro por inactividad. Inicia sesion de nuevo.")
        if self.__consultas >= MAXIMO_CONSULTAS:
            return (False, "Llegaste al maximo de consultas de esta sesion. Cierra sesion y vuelve a entrar.")
        espera = ESPERA_MINIMA - (time.time() - self.__ultima_consulta)
        if espera > 0:
            return (False, "Espera " + str(int(espera) + 1) + " segundo(s) antes de otra consulta.")
        return (True, "")

    def registrar_consulta(self):
        self.__consultas += 1
        self.__ultima_consulta = time.time()
        self.__ultima_actividad = time.time()
