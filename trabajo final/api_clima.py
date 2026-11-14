from cliente_http import Cliente_HTTP
from excepciones import Error_Formato, Error_Datos
from validaciones import Validaciones

URL_CIUDAD = "https://geocoding-api.open-meteo.com/v1/search"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast"

# codigos WMO que entrega Open-Meteo
ESTADOS = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
    45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna ligera", 53: "Llovizna", 55: "Llovizna intensa",
    56: "Llovizna helada", 57: "Llovizna helada intensa",
    61: "Lluvia ligera", 63: "Lluvia", 65: "Lluvia intensa",
    66: "Lluvia helada", 67: "Lluvia helada intensa",
    71: "Nevada ligera", 73: "Nevada", 75: "Nevada intensa", 77: "Granizo fino",
    80: "Chubascos ligeros", 81: "Chubascos", 82: "Chubascos fuertes",
    85: "Chubascos de nieve", 86: "Chubascos de nieve fuertes",
    95: "Tormenta electrica", 96: "Tormenta con granizo", 99: "Tormenta fuerte con granizo"
}

class API_Clima:
    def __init__(self):
        self.__http = Cliente_HTTP()

    def __buscar_ciudad(self, Ciudad):
        # los parametros van en un diccionario, no pegados a la URL
        parametros = {"name": Ciudad, "count": 1, "language": "es"}
        datos = self.__http.obtener_json(URL_CIUDAD, parametros)
        resultados = datos.get("results")
        if not resultados:
            return None
        return resultados[0]

    def __obtener_clima(self, Latitud, Longitud):
        parametros = {
            "latitude": Latitud,
            "longitude": Longitud,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        }
        datos = self.__http.obtener_json(URL_CLIMA, parametros)
        actual = datos.get("current")
        if not isinstance(actual, dict):
            raise Error_Formato("El servicio de clima no entrego datos actuales.",
                                "Falta el campo current en la respuesta")
        return actual

    def __verificar(self, actual):
        # reviso que existan los campos y que los valores tengan sentido
        for campo in ("temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"):
            if campo not in actual or isinstance(actual[campo], bool) \
                    or not isinstance(actual[campo], (int, float)):
                raise Error_Datos("Los datos del clima llegaron incompletos.",
                                  "Campo invalido o faltante: " + campo)
        if not -90 <= actual["temperature_2m"] <= 60:
            raise Error_Datos("La temperatura recibida no es creible.", "Temperatura fuera de rango")
        if not 0 <= actual["relative_humidity_2m"] <= 100:
            raise Error_Datos("La humedad recibida no es creible.", "Humedad fuera de rango")
        if actual["wind_speed_10m"] < 0:
            raise Error_Datos("El viento recibido no es creible.", "Viento negativo")

    def consultar_clima(self, Ciudad):
        # primero se sanea la entrada, si no es valida ni se llama a la API
        Ciudad = Validaciones.sanear_ciudad(Ciudad)
        if Ciudad is None:
            return None

        lugar = self.__buscar_ciudad(Ciudad)
        if lugar is None:
            return {}
        actual = self.__obtener_clima(lugar["latitude"], lugar["longitude"])
        self.__verificar(actual)

        codigo = int(actual["weather_code"])
        return {
            "ciudad": lugar.get("name", Ciudad),
            "pais": lugar.get("country", ""),
            "temperatura": actual["temperature_2m"],
            "humedad": actual["relative_humidity_2m"],
            "viento": actual["wind_speed_10m"],
            "codigo": codigo,
            "estado": ESTADOS.get(codigo, "Condicion no identificada")
        }

    def evaluar_trabajo_exterior(self, clima):
        # regla simple para ayudar a planificar el proyecto
        motivos = []
        if clima["codigo"] >= 51:
            motivos.append("hay precipitaciones o tormenta")
        if clima["viento"] > 40:
            motivos.append("el viento es fuerte")
        if clima["temperatura"] > 35:
            motivos.append("hace demasiado calor")
        if clima["temperatura"] < 0:
            motivos.append("hay riesgo de heladas")
        if len(motivos) == 0:
            return "Condiciones adecuadas para trabajar al aire libre."
        return "Se recomienda reprogramar actividades al aire libre porque " + " y ".join(motivos) + "."
