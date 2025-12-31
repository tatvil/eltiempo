import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import os
from scipy.interpolate import make_interp_spline
import numpy as np

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
query = """
SELECT fecha, amanecer, anochecer, 
       min(temp_min) AS temp_min, 
       max(temp_max) AS temp_max, 
       max(humedad) AS humedad, 
       max(viento_velocidad) AS viento_velocidad, 
       AVG(viento_direccion) AS viento_direccion, 
       max(nubes) AS nubes, 
       max(lluvia) AS lluvia
FROM `weather`
WHERE DATE(fecha) >= '2024-10-01' AND ciudad LIKE '%Madrid%'
GROUP BY DATE(fecha)
ORDER BY DATE(fecha)
"""
df = pd.read_sql(query, conn)

# Cerrar la conexión
conn.close()

# Convertir fechas en números para aplicar la interpolación
df['fecha'] = pd.to_datetime(df['fecha'])
x = np.arange(len(df['fecha']))

# Suavizar las curvas
def smooth_curve(x, y):
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spline = make_interp_spline(x, y, k=3)  # k=3 es un spline cúbico
    y_smooth = spline(x_smooth)
    return x_smooth, y_smooth

# Aplicar suavizado a las series
x_smooth, temp_max_smooth = smooth_curve(x, df['temp_max'])
_, temp_min_smooth = smooth_curve(x, df['temp_min'])
_, humedad_smooth = smooth_curve(x, df['humedad'])
_, viento_velocidad_smooth = smooth_curve(x, df['viento_velocidad'])
# _, viento_direccion_smooth = smooth_curve(x, df['viento_direccion'])
_, nubes_smooth = smooth_curve(x, df['nubes'])
_, lluvia_smooth = smooth_curve(x, df['lluvia'])

# Fechas de luna llena (aquí debes poner las fechas reales que tienes)
luna_llena_fechas = ['2024-10-17', '2024-11-15', '2024-12-15', '2025-01-13', '2025-02-12', '2025-03-14', '2025-04-13', '2025-05-12', 
                     '2025-06-11', '2025-07-10', '2025-08-09', '2025-09-07', '2025-10-06', 
                     '2025-11-05', '2025-12-05']
luna_llena_fechas = pd.to_datetime(luna_llena_fechas)

# Configurar la visualización
plt.figure(figsize=(10, 5))
plt.plot(x_smooth, temp_max_smooth, label='Temperatura Máxima', color='red')
plt.plot(x_smooth, temp_min_smooth, label='Temperatura Mínima', color='blue')
plt.plot(x_smooth, humedad_smooth, label='Humedad', color='green')
plt.plot(x_smooth, viento_velocidad_smooth, label='Viento Velocidad', color='orange')
#plt.plot(x_smooth, viento_direccion_smooth, label='Viento Dirección', color='purple')
plt.plot(x_smooth, nubes_smooth, label='Nubes', color='brown')
plt.plot(x_smooth, lluvia_smooth, label='Lluvia', color='black')
plt.fill_between(x_smooth, temp_min_smooth, temp_max_smooth, color='lightgrey', alpha=0.5)

# Añadir marcadores de las fases de luna llena
for luna_llena in luna_llena_fechas:
    if luna_llena in df['fecha'].values:
        idx = df['fecha'].tolist().index(luna_llena)
        plt.axvline(x=idx, color='yellow', linestyle='--', label=f'Luna Llena ({luna_llena.date()})', alpha=0.7)
        plt.text(idx, df['temp_max'].max(), '🌕', color='yellow', fontsize=14, ha='center')

# Configuración del gráfico
plt.title('Temperaturas Mínimas y Máximas por Día con Fases de Luna Llena')
plt.xlabel('Fecha')
plt.ylabel('Temperatura (°C)')
plt.xticks(x, df['fecha'].dt.strftime('%Y-%m-%d'), rotation=45)
plt.legend()
plt.grid()

# Guardar el gráfico como imagen
output_path = os.path.join('output', 'temperaturas_y_luna_llena.png')
os.makedirs('output', exist_ok=True)  # Crear la carpeta si no existe
plt.savefig(output_path, bbox_inches='tight')

# Mostrar el gráfico
plt.tight_layout()
plt.show()

print(f"Gráfico guardado en: {output_path}")
