import requests

from validaciones import Validaciones

URL_CIUDAD = "https://geocoding-api.open-meteo.com/v1/search"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast"

class API_Clima:
    def __buscar_ciudad(self, Ciudad):
        # los parametros van en un diccionario, no pegados a la URL
        parametros = {"name": Ciudad, "count": 1, "language": "es"}
        respuesta = requests.get(URL_CIUDAD, params=parametros, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if "results" not in datos:
            return None
        return datos["results"][0]

    def __obtener_clima(self, Latitud, Longitud):
        parametros = {
            "latitude": Latitud,
            "longitude": Longitud,
            "current_weather": "true"
        }
        respuesta = requests.get(URL_CLIMA, params=parametros, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        return datos["current_weather"]

    def consultar_clima(self, Ciudad):
        # primero se sanea la entrada, si no es valida ni se llama a la API
        Ciudad = Validaciones.sanear_ciudad(Ciudad)
        if Ciudad is None:
            print("Nombre de ciudad no valido")
            return None

        try:
            lugar = self.__buscar_ciudad(Ciudad)
            if lugar is None:
                print("No se encontro la ciudad")
                return None
            clima = self.__obtener_clima(lugar["latitude"], lugar["longitude"])
            return {
                "ciudad": lugar["name"],
                "temperatura": clima["temperature"],
                "viento": clima["windspeed"],
                "hora": clima["time"]
            }
        except requests.exceptions.Timeout:
            print("La API se demoro mucho en responder")
        except requests.exceptions.ConnectionError:
            print("No hay conexion con la API")
        except requests.exceptions.HTTPError:
            print("La API respondio con un error")
        except (ValueError, KeyError):
            print("La respuesta de la API no vino como se esperaba")
        return None
