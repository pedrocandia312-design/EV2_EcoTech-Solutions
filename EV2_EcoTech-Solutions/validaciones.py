import re

class Validaciones:
    """Reglas de Validacion del sistema"""

    @staticmethod
    def validar_email(email: str) -> bool:
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validar_texto_no_vacio(texto: str) -> bool:
        return bool(texto and texto.strip())

    @staticmethod
    def sanear_ciudad(ciudad: str) -> str:
        ciudad = " ".join(ciudad.split())
        if len(ciudad) < 2 or len(ciudad) > 50:
            return None
        if not ciudad.replace(" ", "").replace("-", "").isalpha():
            return None
        return ciudad

    @staticmethod
    def validar_nivel_acceso(nivel: int) -> bool:
        return isinstance(nivel, int) and 1 <= nivel <= 5

    @staticmethod
    def sanear_email(email: str) -> str:
        # saca espacios y pasa a minuscula para que no haya duplicados
        email = email.strip().lower()
        if len(email) > 60 or not Validaciones.validar_email(email):
            return None
        return email

    @staticmethod
    def validar_clave(clave: str) -> bool:
        # minimo 8 caracteres, con mayuscula, minuscula y numero
        if len(clave) < 8 or len(clave) > 64:
            return False
        if " " in clave:
            return False
        if not re.search(r"[A-Z]", clave):
            return False
        if not re.search(r"[a-z]", clave):
            return False
        if not re.search(r"[0-9]", clave):
            return False
        return True
