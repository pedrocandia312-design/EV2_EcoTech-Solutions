import hashlib
import hmac
import os

from usuarios import Usuario_Cliente, Usuario_Admin
from validaciones import Validaciones

class Autenticacion:
    def __init__(self, base_datos):
        self.__bd = base_datos

    def __cifrar(self, Clave, Sal):
        # la clave nunca se guarda tal cual, solo el hash con sal
        resultado = hashlib.pbkdf2_hmac("sha256", Clave.encode("utf-8"), Sal, 100000)
        return resultado.hex()

    def registrar(self, Nombre, Email, Ciudad, Clave):
        # valida todo antes de tocar la base de datos
        Email = Validaciones.sanear_email(Email)
        if Email is None:
            return (False, "Correo invalido")
        if not Validaciones.validar_clave(Clave):
            return (False, "La clave debe tener minimo 8 caracteres, con mayuscula, minuscula y numero")

        existentes = self.__bd.consultar("SELECT COUNT(*) FROM Usuarios")
        if len(existentes) == 0:
            return (False, "No se pudo revisar la base de datos")

        # el primer usuario registrado queda como administrador
        try:
            if existentes[0][0] == 0:
                nuevo = Usuario_Admin(0, Nombre, Email, 5)
                Tipo = "Admin"
                Ciudad_Final = None
                Nivel = 5
            else:
                nuevo = Usuario_Cliente(0, Nombre, Email, Ciudad)
                Tipo = "Cliente"
                Ciudad_Final = nuevo.get_Ciudad_Frecuente()
                Nivel = None
        except ValueError as error:
            return (False, str(error))

        repetido = self.__bd.consultar("SELECT 1 FROM Usuarios WHERE Email = ?", (Email,))
        if len(repetido) > 0:
            return (False, "Ese correo ya esta registrado")

        Sal = os.urandom(16)
        resultado = self.__bd.ejecutar(
            "INSERT INTO Usuarios (Tipo, Nombre, Email, Ciudad_Frecuente, Nivel_Acceso, Clave_Hash, Sal) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (Tipo, nuevo.get_Nombre(), Email, Ciudad_Final, Nivel, self.__cifrar(Clave, Sal), Sal.hex())
        )
        if resultado is None:
            return (False, "No se pudo guardar el usuario")
        return (True, "Usuario registrado como " + Tipo)

    def iniciar_sesion(self, Email, Clave):
        Email = Validaciones.sanear_email(Email)
        if Email is None:
            return None

        filas = self.__bd.consultar(
            "SELECT ID_Usuario, Tipo, Nombre, Email, Ciudad_Frecuente, Nivel_Acceso, Clave_Hash, Sal "
            "FROM Usuarios WHERE Email = ?",
            (Email,)
        )
        if len(filas) == 0:
            return None

        fila = filas[0]
        if fila[6] is None or fila[7] is None:
            return None

        Sal = bytes.fromhex(fila[7])
        # compare_digest compara sin dar pistas por el tiempo de respuesta
        if not hmac.compare_digest(self.__cifrar(Clave, Sal), fila[6]):
            return None

        if fila[1] == "Admin":
            return Usuario_Admin(fila[0], fila[2], fila[3], fila[5])
        return Usuario_Cliente(fila[0], fila[2], fila[3], fila[4])
