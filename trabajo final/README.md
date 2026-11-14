# EcoTech Solutions - ES03 TI3021

Sistema de gestion interna de EcoTech Solutions en Python con programacion orientada a objetos y SQLite.
Esta version consume dos APIs externas (clima con Open-Meteo y tipos de cambio con ExchangeRate-API),
tiene login con claves cifradas, control de sesion y manejo de errores.

## Como ejecutarlo

1. Instalar la libreria: `pip install -r requirements.txt`
2. Ejecutar: `python main.py`

La primera vez se crea solo el archivo `.env` con un secreto para cifrar las claves
(se puede ver el formato en `.env.example`). El primer usuario que se registra queda como administrador.

## Archivos

- `main.py`: menu principal
- `autenticacion.py`, `sesion.py`: login, claves cifradas, bloqueo y control de sesion
- `cliente_http.py`, `api_clima.py`, `api_cambio.py`: consumo de las APIs
- `excepciones.py`: errores propios de los servicios externos
- `validaciones.py`: validacion de datos de entrada
- `configuracion.py`: lectura del `.env` y archivo de log
- `base_datos.py`, `registro_consultas.py`: SQLite
- `empleado.py`, `gerente.py`, `usuarios.py`: clases del sistema
- `Documentacion_Uso_IA.docx`: documentacion del uso de IA
