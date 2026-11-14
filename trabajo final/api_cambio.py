from cliente_http import Cliente_HTTP
from excepciones import Error_Formato, Error_Datos
from validaciones import Validaciones

URL_CAMBIO = "https://open.er-api.com/v6/latest/USD"

class API_Cambio:
    def __init__(self):
        self.__http = Cliente_HTTP()

    def __obtener_tasas(self):
        datos = self.__http.obtener_json(URL_CAMBIO)
        if datos.get("result") != "success":
            raise Error_Formato("El servicio de monedas no pudo entregar los valores.",
                                "result distinto de success")
        tasas = datos.get("rates")
        if not isinstance(tasas, dict):
            raise Error_Formato("El servicio de monedas entrego datos inesperados.",
                                "Falta el campo rates")
        return tasas

    def __tasa_valida(self, tasas, moneda):
        valor = tasas.get(moneda)
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
            raise Error_Datos("No hay un tipo de cambio utilizable para " + moneda + ".",
                              "Tasa invalida para " + moneda)
        return valor

    def convertir_pago(self, Salario_CLP, Moneda):
        # el salario esta en pesos chilenos y se paga en la moneda del pais del proyecto
        Moneda = Validaciones.sanear_moneda(Moneda)
        if Moneda is None:
            return None
        if isinstance(Salario_CLP, bool) or not isinstance(Salario_CLP, (int, float)) or Salario_CLP <= 0:
            raise Error_Datos("El salario no es valido para calcular el pago.", "Salario invalido")

        tasas = self.__obtener_tasas()
        tasa_clp = self.__tasa_valida(tasas, "CLP")
        tasa_destino = self.__tasa_valida(tasas, Moneda)

        # la API entrega todo respecto al dolar: CLP -> USD -> moneda destino
        valor_usd = Salario_CLP / tasa_clp
        return {
            "moneda": Moneda,
            "salario_clp": Salario_CLP,
            "tipo_cambio": tasa_destino / tasa_clp,
            "pago": round(valor_usd * tasa_destino, 2)
        }
