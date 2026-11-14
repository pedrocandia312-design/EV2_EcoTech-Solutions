# Jerarquia de excepciones para los servicios externos.
# Todas heredan de Error_Servicio, asi en main puedo atrapar cualquiera con un solo except.

class Error_Servicio(Exception):
    """Error general al usar un servicio externo"""
    def __init__(self, mensaje_usuario, detalle_tecnico=""):
        super().__init__(mensaje_usuario)
        self.mensaje_usuario = mensaje_usuario
        # el detalle tecnico solo va al archivo de log, nunca a la pantalla
        self.detalle_tecnico = detalle_tecnico

class Error_Conexion(Error_Servicio):
    """No hay internet o no se pudo llegar al servidor"""

class Error_Tiempo_Espera(Error_Servicio):
    """El servidor se demoro demasiado"""

class Error_HTTP(Error_Servicio):
    """El servidor respondio con un codigo de error"""

class Error_Formato(Error_Servicio):
    """La respuesta no es un JSON valido o le faltan campos"""

class Error_Datos(Error_Servicio):
    """Los datos llegaron pero no son utilizables (valores fuera de rango)"""
