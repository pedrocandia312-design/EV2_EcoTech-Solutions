from datetime import date
from getpass import getpass

from api_clima import API_Clima
from autenticacion import Autenticacion
from base_datos import Base_Datos
from empleado import Empleado
from gerente import Gerente
from usuarios import Usuario_Cliente, Usuario_Admin

def registrarse(auth):
    print("\nREGISTRO DE USUARIO")
    Nombre = input("Nombre: ")
    Email = input("Correo: ")
    Ciudad = input("Ciudad frecuente: ")
    Clave = getpass("Clave (minimo 8, con mayuscula, minuscula y numero): ")
    ok, mensaje = auth.registrar(Nombre, Email, Ciudad, Clave)
    print(mensaje)

def iniciar_sesion(auth):
    intentos = 0
    while intentos < 3:
        Email = input("\nCorreo: ")
        Clave = getpass("Clave: ")
        usuario = auth.iniciar_sesion(Email, Clave)
        if usuario is not None:
            print("Bienvenido")
            print(usuario.mostrar_info())
            return usuario
        intentos += 1
        # el mensaje no dice si fallo el correo o la clave
        print("Correo o clave incorrectos. Intento", intentos, "de 3")
    print("Demasiados intentos fallidos")
    return None

def consultar_clima(usuario, api):
    Ciudad = ""
    if isinstance(usuario, Usuario_Cliente):
        Ciudad = input("Ciudad (enter para usar " + usuario.get_Ciudad_Frecuente() + "): ")
        if Ciudad.strip() == "":
            Ciudad = usuario.get_Ciudad_Frecuente()
    else:
        Ciudad = input("Ciudad: ")

    clima = api.consultar_clima(Ciudad)
    if clima is not None:
        print("\nClima actual en", clima["ciudad"])
        print("Temperatura:", clima["temperatura"], "C")
        print("Viento:", clima["viento"], "km/h")
        print("Hora de la medicion:", clima["hora"])

def probar_empleado_gerente():
    empleado1 = Empleado(
        1,
        "Juan Perez",
        "Santiago",
        "912345678",
        "juan.perez@ecotech.cl",
        date(2026,10,16),
        850000
    )
    print("\nDATOS DEL EMPLEADO")
    print(empleado1.Obtener_Detalles())

    Resultado = empleado1.registrar_tiempo(8, "Desarrollo de software")
    print("Registro de tiempo exitoso", Resultado)

    gerente1 = Gerente(empleado1, 1500000, True)
    print(gerente1.Generar_Reporte())

def menu_usuario(usuario, api):
    while True:
        print("\n1. Consultar clima")
        if isinstance(usuario, Usuario_Admin):
            print("2. Probar empleado y gerente")
            print("3. Cerrar sesion")
        else:
            print("2. Cerrar sesion")
        opcion = input("Opcion: ").strip()

        if opcion == "1":
            consultar_clima(usuario, api)
        elif opcion == "2" and isinstance(usuario, Usuario_Admin):
            probar_empleado_gerente()
        elif opcion == "2" and isinstance(usuario, Usuario_Cliente):
            break
        elif opcion == "3" and isinstance(usuario, Usuario_Admin):
            break
        else:
            print("Opcion no valida")

def main():
    print("=="* 20)
    print("ECOTECH SOLUTIONS")
    print("Sistema de gestion interna")
    print("=="* 20)

    bd = Base_Datos()
    if not bd.probar_conexion():
        return
    bd.Crear_Tablas()

    auth = Autenticacion(bd)
    api = API_Clima()

    while True:
        print("\n1. Registrarse")
        print("2. Iniciar sesion")
        print("3. Salir")
        opcion = input("Opcion: ").strip()

        if opcion == "1":
            registrarse(auth)
        elif opcion == "2":
            usuario = iniciar_sesion(auth)
            if usuario is not None:
                menu_usuario(usuario, api)
        elif opcion == "3":
            print("Hasta luego")
            break
        else:
            print("Opcion no valida")

if __name__ == "__main__":
    main()
