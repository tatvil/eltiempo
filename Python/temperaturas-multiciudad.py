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

# Lista de ciudades a graficar
ciudades = ['Madrid', 'Ampolla', 'Alfas del Pi']

# Lista de colores para diferenciar las ciudades
colores = ['red', 'blue', 'green', 'purple', 'orange']

# Fechas de luna llena
luna_llena_fechas = pd.to_datetime([
    '2024-10-17', '2024-11-15', '2024-12-15', '2025-01-13', '2025-02-12', 
    '2025-03-14', '2025-04-13', '2025-05-12', '2025-06-11', '2025-07-10',
    '2025-08-09', '2025-09-07', '2025-10-06', '2025-11-05', '2025-12-05'
])

# Función para suavizar curvas
def smooth_curve(x, y):
    if len(x) < 3:
        return x, y
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spline = make_interp_spline(x, y, k=3)
    y_smooth = spline(x_smooth)
    return x_smooth, y_smooth

# Configurar la visualización
plt.figure(figsize=(12, 6))

for i, ciudad in enumerate(ciudades):
    # Consulta SQL para cada ciudad
    query = """
    SELECT fecha, 
           MIN(temp_min) AS temp_min, 
           MAX(temp_max) AS temp_max
    FROM `weather`
    WHERE DATE(fecha) >= '2024-10-01' AND ciudad LIKE %s
    GROUP BY DATE(fecha)
    ORDER BY DATE(fecha)
    """

    df = pd.read_sql(query, conn, params=[f'%{ciudad}%'])

    if df.empty:
        print(f"No hay datos para {ciudad}, saltando...")
        continue  # Si no hay datos para la ciudad, pasar a la siguiente

    # Convertir fechas en valores numéricos
    df['fecha'] = pd.to_datetime(df['fecha'])
    x = np.arange(len(df['fecha']))

    # Suavizar curvas
    x_smooth, temp_max_smooth = smooth_curve(x, df['temp_max'])
    _, temp_min_smooth = smooth_curve(x, df['temp_min'])

    # Graficar temperaturas
    plt.plot(x_smooth, temp_max_smooth, label=f'{ciudad} - Máx', color=colores[i % len(colores)], linestyle='solid')
    plt.plot(x_smooth, temp_min_smooth, label=f'{ciudad} - Mín', color=colores[i % len(colores)], linestyle='dashed')

    # Añadir líneas para luna llena
    for luna_llena in luna_llena_fechas:
        if luna_llena in df['fecha'].values:
            idx = df[df['fecha'] == luna_llena].index[0]
            plt.axvline(x=idx, color='yellow', linestyle='--', alpha=0.5)

# Cerrar la conexión
conn.close()

# Configurar etiquetas y diseño
plt.title('Temperaturas Diarias en Varias Ciudades con Fases de Luna Llena')
plt.xlabel('Fecha')
plt.ylabel('Temperatura (°C)')
plt.xticks(rotation=45)
plt.legend()
plt.grid()

# Guardar el gráfico
output_path = os.path.join('output', 'temperaturas_multiciudad.png')
os.makedirs('output', exist_ok=True)
plt.savefig(output_path, bbox_inches='tight')

# Mostrar el gráfico
plt.tight_layout()
plt.show()

print(f"Gráfico guardado en: {output_path}")
