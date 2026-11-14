import logging
from datetime import date
from getpass import getpass

from api_clima import API_Clima
from api_cambio import API_Cambio
from autenticacion import Autenticacion
from base_datos import Base_Datos
from configuracion import Configuracion, configurar_log
from empleado import Empleado
from excepciones import Error_Servicio
from gerente import Gerente
from registro_consultas import Registro_Consultas
from sesion import Sesion
from usuarios import Usuario_Cliente, Usuario_Admin
from validaciones import MONEDAS_PERMITIDAS

def registrarse(auth):
    print("\nREGISTRO DE USUARIO")
    Nombre = input("Nombre: ")
    Email = input("Correo: ")
    Ciudad = input("Ciudad frecuente: ")
    Clave = getpass("Clave (minimo 8, con mayuscula, minuscula y numero): ")
    _, mensaje = auth.registrar(Nombre, Email, Ciudad, Clave)
    print(mensaje)

def iniciar_sesion(auth):
    print("\nINICIO DE SESION (deja el correo vacio para volver)")
    while True:
        Email = input("Correo: ")
        if Email.strip() == "":
            return None
        Clave = getpass("Clave: ")
        usuario, mensaje = auth.iniciar_sesion(Email, Clave)
        if usuario is not None:
            print("Bienvenido")
            print(usuario.mostrar_info())
            return usuario
        print(mensaje)
        if "Demasiados" in mensaje:
            return None

def manejar_error(error):
    # el usuario ve un mensaje simple, el detalle tecnico queda en errores.log
    print(error.mensaje_usuario)
    logging.warning(error.detalle_tecnico)

def consultar_clima(sesion, api, registro):
    usuario = sesion.get_usuario()
    permitido, mensaje = sesion.permitir_consulta()
    if not permitido:
        print(mensaje)
        return

    if isinstance(usuario, Usuario_Cliente):
        Ciudad = input("Ciudad del proyecto (enter para usar " + usuario.get_Ciudad_Frecuente() + "): ")
        if Ciudad.strip() == "":
            Ciudad = usuario.get_Ciudad_Frecuente()
    else:
        Ciudad = input("Ciudad del proyecto: ")

    sesion.registrar_consulta()
    try:
        clima = api.consultar_clima(Ciudad)
    except Error_Servicio as error:
        manejar_error(error)
        return
    except Exception:
        print("Ocurrio un error inesperado. Intenta de nuevo mas tarde.")
        logging.exception("Error inesperado al consultar el clima")
        return

    if clima is None:
        print("Ciudad no valida. Usa solo letras, espacios o guiones.")
        return
    if clima == {}:
        print("No se encontro esa ciudad.")
        return

    print("\nClima actual en", clima["ciudad"], "-", clima["pais"])
    print("Temperatura:", clima["temperatura"], "C")
    print("Estado del tiempo:", clima["estado"])
    print("Humedad:", clima["humedad"], "%")
    print("Viento:", clima["viento"], "km/h")
    print(api.evaluar_trabajo_exterior(clima))

    resumen = str(clima["temperatura"]) + " C, " + clima["estado"] + ", humedad " + str(clima["humedad"]) + "%"
    registro.guardar(usuario.get_ID_Usuario(), "Clima", clima["ciudad"], resumen)

def calcular_pago(sesion, api, registro, empleado):
    usuario = sesion.get_usuario()
    permitido, mensaje = sesion.permitir_consulta()
    if not permitido:
        print(mensaje)
        return

    print("\nEmpleado:", empleado.get_Nombre(), "- Salario:", empleado.get_Salario(), "CLP")
    print("Monedas disponibles:", ", ".join(MONEDAS_PERMITIDAS))
    Moneda = input("Moneda del pais donde se ejecuta el proyecto: ")

    sesion.registrar_consulta()
    try:
        pago = api.convertir_pago(empleado.get_Salario(), Moneda)
    except Error_Servicio as error:
        manejar_error(error)
        return
    except Exception:
        print("Ocurrio un error inesperado. Intenta de nuevo mas tarde.")
        logging.exception("Error inesperado al calcular el pago")
        return

    if pago is None:
        print("Moneda no valida. Elige una de la lista.")
        return

    print("\nTipo de cambio: 1 CLP =", round(pago["tipo_cambio"], 6), pago["moneda"])
    print("Pago a", empleado.get_Nombre() + ":", pago["pago"], pago["moneda"])
    print("Fuente de los tipos de cambio: ExchangeRate-API (exchangerate-api.com)")

    resumen = str(pago["pago"]) + " " + pago["moneda"] + " por " + str(pago["salario_clp"]) + " CLP"
    registro.guardar(usuario.get_ID_Usuario(), "Pago", empleado.get_Nombre() + " en " + pago["moneda"], resumen)

def ver_historial(registro):
    filas = registro.ultimas(10)
    if len(filas) == 0:
        print("Todavia no hay consultas guardadas.")
        return
    print("\nULTIMAS CONSULTAS")
    for fila in filas:
        print(fila[0], "| usuario", fila[1], "|", fila[2], "|", fila[3], "|", fila[4])

def probar_empleado_gerente(empleado):
    print("\nDATOS DEL EMPLEADO")
    print(empleado.Obtener_Detalles())
    Resultado = empleado.registrar_tiempo(8, "Desarrollo de software")
    print("Registro de tiempo exitoso", Resultado)
    gerente1 = Gerente(empleado, 1500000, True)
    print(gerente1.Generar_Reporte())

def menu_usuario(usuario, api_clima, api_cambio, registro, empleado):
    sesion = Sesion(usuario)
    es_admin = isinstance(usuario, Usuario_Admin)

    while True:
        # solo se llega aqui estando autenticado, y la sesion se vence por inactividad
        if not sesion.esta_activa():
            print("\nLa sesion expiro por inactividad. Inicia sesion de nuevo.")
            return

        print("\n1. Consultar clima de un proyecto")
        print("2. Calcular pago internacional")
        if es_admin:
            print("3. Ver historial de consultas")
            print("4. Probar empleado y gerente")
            print("5. Cerrar sesion")
        else:
            print("3. Cerrar sesion")
        opcion = input("Opcion: ").strip()

        if not sesion.esta_activa():
            print("\nLa sesion expiro por inactividad. Inicia sesion de nuevo.")
            return
        sesion.actividad()

        if opcion == "1":
            consultar_clima(sesion, api_clima, registro)
        elif opcion == "2":
            calcular_pago(sesion, api_cambio, registro, empleado)
        elif opcion == "3" and es_admin:
            ver_historial(registro)
        elif opcion == "4" and es_admin:
            probar_empleado_gerente(empleado)
        elif (opcion == "5" and es_admin) or (opcion == "3" and not es_admin):
            print("Sesion cerrada.")
            return
        else:
            print("Opcion no valida")

def main():
    configurar_log()
    print("=="* 20)
    print("ECOTECH SOLUTIONS")
    print("Sistema de gestion interna")
    print("=="* 20)

    bd = Base_Datos()
    if not bd.probar_conexion():
        return
    bd.Crear_Tablas()

    try:
        auth = Autenticacion(bd, Configuracion())
    except ValueError as error:
        print(error)
        return
    registro = Registro_Consultas(bd)
    api_clima = API_Clima()
    api_cambio = API_Cambio()

    # empleado de ejemplo para calcular el pago internacional
    empleado = Empleado(1, "Juan Perez", "Santiago", "912345678",
                        "juan.perez@ecotech.cl", date(2026, 10, 16), 850000)

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
                menu_usuario(usuario, api_clima, api_cambio, registro, empleado)
        elif opcion == "3":
            print("Hasta luego")
            break
        else:
            print("Opcion no valida")

if __name__ == "__main__":
    main()
