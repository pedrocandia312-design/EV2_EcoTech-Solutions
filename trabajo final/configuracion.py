import logging
import os
import secrets

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_ENV = os.path.join(CARPETA, ".env")
RUTA_LOG = os.path.join(CARPETA, "errores.log")

class Configuracion:
    """Lee los datos sensibles desde el archivo .env, no desde el codigo"""

    def __init__(self):
        self.__datos = {}
        if not os.path.exists(RUTA_ENV):
            self.__crear_env()
        self.__leer_env()

    def __crear_env(self):
        # la primera vez se crea un secreto aleatorio solo para este equipo
        with open(RUTA_ENV, "w", encoding="utf-8") as archivo:
            archivo.write("ECOTECH_PEPPER=" + secrets.token_hex(32) + "\n")

    def __leer_env(self):
        with open(RUTA_ENV, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "" or linea.startswith("#") or "=" not in linea:
                    continue
                clave, valor = linea.split("=", 1)
                self.__datos[clave.strip()] = valor.strip()
        # si existe como variable de entorno, esa tiene prioridad
        for clave in list(self.__datos):
            if clave in os.environ:
                self.__datos[clave] = os.environ[clave]

    def obtener(self, clave):
        return self.__datos.get(clave)

def configurar_log():
    # los errores tecnicos se guardan aca, el usuario solo ve mensajes simples
    logging.basicConfig(
        filename=RUTA_LOG,
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
