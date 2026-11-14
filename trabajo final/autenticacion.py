import hashlib
import hmac
import os
import time

from usuarios import Usuario_Cliente, Usuario_Admin
from validaciones import Validaciones

ITERACIONES = 600000
MAX_FALLOS = 3
SEGUNDOS_BLOQUEO = 60

class Autenticacion:
    def __init__(self, base_datos, configuracion):
        self.__bd = base_datos
        # secreto que viene del archivo .env, no esta escrito en el codigo
        self.__pepper = configuracion.obtener("ECOTECH_PEPPER")
        if not self.__pepper:
            raise ValueError("Falta ECOTECH_PEPPER en el archivo .env")
        self.__fallos = {}

    def __cifrar(self, Clave, Sal):
        # la clave nunca se guarda tal cual, solo el hash con sal y pepper
        texto = (self.__pepper + Clave).encode("utf-8")
        resultado = hashlib.pbkdf2_hmac("sha256", texto, Sal, ITERACIONES)
        return resultado.hex()

    def segundos_bloqueo(self, Email):
        # devuelve cuantos segundos faltan para poder intentar de nuevo (0 si no esta bloqueado)
        if Email not in self.__fallos:
            return 0
        cantidad, ultimo = self.__fallos[Email]
        if cantidad < MAX_FALLOS:
            return 0
        restante = SEGUNDOS_BLOQUEO - (time.time() - ultimo)
        if restante <= 0:
            del self.__fallos[Email]
            return 0
        return int(restante) + 1

    def __anotar_fallo(self, Email):
        cantidad = 0
        if Email in self.__fallos:
            cantidad = self.__fallos[Email][0]
        self.__fallos[Email] = (cantidad + 1, time.time())

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
        # devuelve (usuario, mensaje). Si falla, usuario es None
        Email = Validaciones.sanear_email(Email)
        if Email is None or Clave == "":
            return (None, "Correo o clave incorrectos")

        espera = self.segundos_bloqueo(Email)
        if espera > 0:
            return (None, "Demasiados intentos. Espera " + str(espera) + " segundos.")

        filas = self.__bd.consultar(
            "SELECT ID_Usuario, Tipo, Nombre, Email, Ciudad_Frecuente, Nivel_Acceso, Clave_Hash, Sal "
            "FROM Usuarios WHERE Email = ?",
            (Email,)
        )

        valido = False
        fila = None
        if len(filas) > 0:
            fila = filas[0]
            if fila[6] is not None and fila[7] is not None:
                Sal = bytes.fromhex(fila[7])
                # compare_digest compara sin dar pistas por el tiempo de respuesta
                valido = hmac.compare_digest(self.__cifrar(Clave, Sal), fila[6])

        if not valido:
            # mismo mensaje exista o no el correo, y se cuenta el fallo igual
            self.__anotar_fallo(Email)
            return (None, "Correo o clave incorrectos")

        if Email in self.__fallos:
            del self.__fallos[Email]
        if fila[1] == "Admin":
            return (Usuario_Admin(fila[0], fila[2], fila[3], fila[5]), "")
        return (Usuario_Cliente(fila[0], fila[2], fila[3], fila[4]), "")
