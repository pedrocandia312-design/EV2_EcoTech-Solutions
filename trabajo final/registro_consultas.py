from datetime import datetime

class Registro_Consultas:
    """Guarda en SQLite las consultas que se hacen a las APIs"""

    def __init__(self, base_datos):
        self.__bd = base_datos

    def guardar(self, ID_Usuario, Tipo, Detalle, Resultado):
        Fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.__bd.ejecutar(
            "INSERT INTO Consultas (ID_Usuario, Tipo, Detalle, Resultado, Fecha) "
            "VALUES (?, ?, ?, ?, ?)",
            (ID_Usuario, Tipo, Detalle, Resultado, Fecha)
        )

    def ultimas(self, Cantidad=10):
        return self.__bd.consultar(
            "SELECT Fecha, ID_Usuario, Tipo, Detalle, Resultado "
            "FROM Consultas ORDER BY ID_Consulta DESC LIMIT ?",
            (Cantidad,)
        )
