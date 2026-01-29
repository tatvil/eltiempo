import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yaml
import os
from scipy.stats import linregress

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

# Consultar los datos
df = pd.read_sql(
    """
    SELECT DATE(fecha) AS fecha, 
           MAX(temp_max) AS temp_max, 
           MIN(temp_min) AS temp_min
    FROM `weather`
    WHERE DATE(fecha) >= '2024-10-01'
            AND ciudad LIKE '%Madrid%'
    GROUP BY DATE(fecha)
    ORDER BY DATE(fecha)
    """,
    conn
)

# Cerrar la conexión
conn.close()

# Convertir la columna de fecha a formato datetime
df['fecha'] = pd.to_datetime(df['fecha'])

# Fechas de luna llena (añade más si es necesario)
luna_llena_fechas = ['2024-10-17', '2024-11-15', '2024-12-15', '2025-01-13', '2025-02-12', '2025-03-14', '2025-04-13', '2025-05-12',
                     '2025-06-11', '2025-07-10', '2025-08-09', '2025-09-07', '2025-10-06', '2025-11-05', '2025-12-05']
luna_llena_fechas = pd.to_datetime(luna_llena_fechas)

# Crear una columna indicando si una fecha está cerca de una luna llena (2 días antes o después)
def es_cerca_luna_llena(fecha):
    for luna in luna_llena_fechas:
        if abs((fecha - luna).days) <= 2:
            return True
    return False

df['cerca_luna_llena'] = df['fecha'].apply(es_cerca_luna_llena)

# Calcular promedios
temp_max_promedio_cercanos = df[df['cerca_luna_llena']]['temp_max'].mean()
temp_min_promedio_cercanos = df[df['cerca_luna_llena']]['temp_min'].mean()
temp_max_promedio_normal = df[~df['cerca_luna_llena']]['temp_max'].mean()
temp_min_promedio_normal = df[~df['cerca_luna_llena']]['temp_min'].mean()

# Resultados
print(f"Promedio Temp. Máxima (cercano a luna llena): {temp_max_promedio_cercanos:.2f} °C")
print(f"Promedio Temp. Mínima (cercano a luna llena): {temp_min_promedio_cercanos:.2f} °C")
print(f"Promedio Temp. Máxima (normal): {temp_max_promedio_normal:.2f} °C")
print(f"Promedio Temp. Mínima (normal): {temp_min_promedio_normal:.2f} °C")

# Visualización
plt.figure(figsize=(12, 6))
plt.plot(df['fecha'], df['temp_max'], label='Temperatura Máxima', color='red', marker='o')
plt.plot(df['fecha'], df['temp_min'], label='Temperatura Mínima', color='blue', marker='o')

# Marcar días cercanos a luna llena
for luna in luna_llena_fechas:
    if luna in df['fecha'].values:
        plt.axvline(x=luna, color='yellow', linestyle='--', alpha=0.7, label=f'Luna Llena ({luna.date()})')

# Configuración del gráfico
plt.title('Temperaturas Máximas y Mínimas con Fechas de Luna Llena')
plt.xlabel('Fecha')
plt.ylabel('Temperatura (°C)')
plt.xticks(rotation=45)
plt.legend()
plt.grid()

# Guardar el gráfico
output_path = os.path.join('output', 'temp_vs_luna_llena.png')
os.makedirs('output', exist_ok=True)
plt.savefig(output_path, bbox_inches='tight')

# Mostrar el gráfico
plt.tight_layout()
plt.show()

print(f"Gráfico guardado en: {output_path}")
