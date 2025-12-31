import calendar
import datetime
import mysql.connector
import yaml

# Cargar la configuración desde el archivo YAML
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# Conectar a la base de datos
conn = mysql.connector.connect(
    host=config['database']['host'],
    user=config['database']['user'],
    password=config['database']['password'],
    database=config['database']['database']
)

# Obtener la fecha de hoy
hoy = datetime.datetime.now()

# Consultar los datos del tiempo de hoy
query = """
SELECT amanecer, anochecer, min(temp_min), max(temp_max), humedad, max(viento_velocidad), avg(viento_direccion), nubes, sum(lluvia)
FROM weather
WHERE DATE(fecha) = CURDATE() AND ciudad LIKE '%Madrid%'
GROUP BY DATE(fecha);
"""
cursor = conn.cursor()
cursor.execute(query)

# Obtener los resultados
resultados = cursor.fetchone()
cursor.close()
conn.close()

# Función para convertir timedelta a formato de hora
def timedelta_to_time(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"

# Configurar los datos del tiempo
if resultados:
    amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = resultados
    # Formatear los datos
    amanecer = timedelta_to_time(amanecer) if amanecer else "No disponible"
    anochecer = timedelta_to_time(anochecer) if anochecer else "No disponible"
    humedad = int(humedad) if humedad is not None else "No disponible"
    viento_velocidad = int(viento_velocidad) if viento_velocidad is not None else "No disponible"
    viento_direccion = int(viento_direccion) if viento_direccion is not None else "No disponible"
    nubes = int(nubes) if nubes is not None else "No disponible"
    
    clima_hoy = f"""
    Datos del tiempo de hoy:
    Amanecer: {amanecer}
    Anochecer: {anochecer}
    Temperatura Mínima: {temp_min} °C
    Temperatura Máxima: {temp_max} °C
    Humedad: {humedad}%
    Velocidad del Viento: {viento_velocidad} m/s
    Dirección del Viento: {viento_direccion}
    Nubes: {nubes}%
    Lluvia: {lluvia} mm
    """
else:
    clima_hoy = "No hay datos del tiempo para hoy."

# Mostrar el calendario del mes actual
mes_actual = hoy.month
año_actual = hoy.year

calendario = calendar.TextCalendar()
calendario_mes = calendario.formatmonth(año_actual, mes_actual)

# Mostrar el resultado
print(f"\nCalendario de {calendar.month_name[mes_actual]} {año_actual}:\n")
print(calendario_mes)
print(clima_hoy)