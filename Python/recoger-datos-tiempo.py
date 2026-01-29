"""
Este script recoge los datos del tiempo de la ciudad de Madrid desde la API de OpenWeatherMap y los guarda en una base de datos MySQL.
"""
import requests
import mysql.connector
import requests
from datetime import datetime, timezone
import pytz
import yaml

# Cargar la configuración desde el archivo YAML
try:
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Error: El archivo de configuración no se encuentra.")
    exit(1)

# Conectar a la base de datos usando los datos del archivo de configuración
try:
    conn = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['database']
    )
except mysql.connector.Error as err:
    print(f"Error al conectar a la base de datos: {err}")
    exit(1)

# Crear un cursor para ejecutar consultas
cursor = conn.cursor()

# Leer la API key de OpenWeatherMap desde el archivo de configuración
API_KEY = config['api_keys']['weather_api_key']
CITY = 'Madrid,es'
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

def obtener_datos_tiempo():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()  # Devuelve los datos en formato JSON.
    else:
        print("Error al obtener los datos del tiempo")
        return None

# Función para convertir el timestamp a una fecha legible de la zona horaria local
def convertir_fecha(timestamp):
    tz_local = pytz.timezone('Europe/Madrid')  # Cambia 'Europe/Madrid' por tu zona horaria local
    fecha_utc = datetime.fromtimestamp(timestamp, pytz.UTC)  # Convertir timestamp a UTC con timezone-aware object
    fecha_local = fecha_utc.astimezone(tz_local)  # Convertir a la zona horaria local
    return fecha_local.strftime('%Y-%m-%d %H:%M:%S')

# Función para guardar los datos en la tabla weather
def guardar_datos_tiempo(datos):
    ciudad = datos['name']
    fecha = convertir_fecha(datos['dt'])  # Hora actual del clima
    amanecer = convertir_fecha(datos['sys']['sunrise'])
    anochecer = convertir_fecha(datos['sys']['sunset'])
    temp_min = datos['main']['temp_min']
    temp_max = datos['main']['temp_max']
    humedad = datos['main']['humidity']
    viento_velocidad = datos['wind']['speed']
    viento_direccion = datos['wind']['deg']
    nubes = datos['clouds']['all']
    lluvia = datos.get('rain', {}).get('1h', 0)  # Lluvia en la última hora, si existe

    # Insertar los datos en la tabla
    cursor.execute('''
        INSERT INTO weather (fecha, ciudad, amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (fecha, ciudad, amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia))

    # Confirmar los cambios
    conn.commit()

# Obtener y guardar los datos
datos_tiempo = obtener_datos_tiempo()
if datos_tiempo:
    guardar_datos_tiempo(datos_tiempo)
    diayhora = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f"{diayhora} - Datos guardados correctamente en la base de datos MySQL.")

# Cerrar la conexión al terminar
conn.close()
