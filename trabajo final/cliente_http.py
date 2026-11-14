import logging
import time

import requests

from excepciones import (Error_Conexion, Error_Tiempo_Espera, Error_HTTP, Error_Formato)

TIEMPO_ESPERA = 10
INTENTOS = 3
ESPERA_ENTRE_INTENTOS = 1

class Cliente_HTTP:
    """Hace los GET a las APIs. Lo usan API_Clima y API_Cambio."""

    def obtener_json(self, url, parametros=None):
        ultimo_error = None

        for intento in range(1, INTENTOS + 1):
            try:
                respuesta = requests.get(url, params=parametros, timeout=TIEMPO_ESPERA)
            except requests.exceptions.Timeout:
                ultimo_error = Error_Tiempo_Espera(
                    "El servicio externo se demoro demasiado en responder.",
                    "Timeout en " + url)
            except requests.exceptions.ConnectionError:
                ultimo_error = Error_Conexion(
                    "No hay conexion con el servicio externo. Revisa tu internet.",
                    "ConnectionError en " + url)
            except requests.exceptions.RequestException as error:
                ultimo_error = Error_Conexion(
                    "No se pudo completar la consulta al servicio externo.",
                    "RequestException en " + url + ": " + type(error).__name__)
            else:
                # llego una respuesta, reviso el codigo HTTP
                codigo = respuesta.status_code
                if codigo == 200:
                    return self.__leer_json(respuesta, url)

                error_http = self.__error_por_codigo(codigo, url)
                # 400, 401, 403 y 404 no se arreglan reintentando
                if codigo < 500 and codigo != 429:
                    raise error_http
                ultimo_error = error_http

            logging.warning("Intento %s de %s fallido: %s", intento, INTENTOS, ultimo_error.detalle_tecnico)
            if intento < INTENTOS:
                time.sleep(ESPERA_ENTRE_INTENTOS)

        raise ultimo_error

    def __leer_json(self, respuesta, url):
        try:
            datos = respuesta.json()
        except ValueError:
            raise Error_Formato(
                "El servicio externo entrego una respuesta que no se puede leer.",
                "JSON invalido desde " + url)
        if not isinstance(datos, dict):
            raise Error_Formato(
                "El servicio externo entrego una respuesta inesperada.",
                "El JSON de " + url + " no es un objeto")
        return datos

    def __error_por_codigo(self, codigo, url):
        detalle = "Codigo HTTP " + str(codigo) + " en " + url
        if codigo == 400:
            return Error_HTTP("La consulta no fue aceptada por el servicio (datos incorrectos).", detalle)
        if codigo in (401, 403):
            return Error_HTTP("No hay autorizacion para usar este servicio externo.", detalle)
        if codigo == 404:
            return Error_HTTP("El servicio externo no encontro lo que se pidio.", detalle)
        if codigo == 429:
            return Error_HTTP("Se hicieron demasiadas consultas. Intenta de nuevo en un rato.", detalle)
        if codigo >= 500:
            return Error_HTTP("El servicio externo esta con problemas en este momento.", detalle)
        return Error_HTTP("El servicio externo respondio algo inesperado.", detalle)
