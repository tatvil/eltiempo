import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import os
import numpy as np
from scipy.stats import pearsonr

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
SELECT fecha, 
       MAX(temp_max) AS temp_max, 
       MIN(temp_min) AS temp_min, 
       AVG(lluvia) AS lluvia, 
       AVG(nubes) AS nubes, 
       AVG(viento_velocidad) AS viento_velocidad,
       AVG(viento_direccion) AS viento_direccion
FROM weather
WHERE DATE(fecha) >= '2024-10-01'
 AND ciudad LIKE '%madrid%'
GROUP BY DATE(fecha)
ORDER BY DATE(fecha)
"""
df = pd.read_sql(query, conn)

# Cerrar la conexión
conn.close()

# Convertir fechas y calcular días cercanos a luna llena
df['fecha'] = pd.to_datetime(df['fecha'])
luna_llena_fechas = ['2024-10-17', '2024-11-15', '2024-12-15', '2025-01-13', '2025-02-12',
                     '2025-03-14', '2025-04-13', '2025-05-12', '2025-06-11', '2025-07-10',
                     '2025-08-09', '2025-09-07', '2025-10-06', '2025-11-05', '2025-12-05']
luna_llena_fechas = pd.to_datetime(luna_llena_fechas)
df['luna_llena'] = df['fecha'].apply(lambda x: any(abs((x - luna).days) <= 2 for luna in luna_llena_fechas))

# Gráficos para lluvia, nubes y viento
plt.figure(figsize=(15, 15))

# Lluvia
plt.subplot(4, 1, 1)
plt.plot(df['fecha'], df['lluvia'], label='Lluvia (mm)', color='blue')
plt.scatter(df[df['luna_llena']]['fecha'], df[df['luna_llena']]['lluvia'], color='yellow', label='Cercano a Luna Llena', zorder=5)
plt.title('Lluvia vs Luna Llena')
plt.xlabel('Fecha')
plt.ylabel('Lluvia (mm)')
plt.legend()
plt.grid()

# Nubes
plt.subplot(4, 1, 2)
plt.plot(df['fecha'], df['nubes'], label='% Nubes', color='gray')
plt.scatter(df[df['luna_llena']]['fecha'], df[df['luna_llena']]['nubes'], color='yellow', label='Cercano a Luna Llena', zorder=5)
plt.title('Nubes vs Luna Llena')
plt.xlabel('Fecha')
plt.ylabel('% Nubes')
plt.legend()
plt.grid()

# Velocidad del Viento
plt.subplot(4, 1, 3)
plt.plot(df['fecha'], df['viento_velocidad'], label='Velocidad del Viento (km/h)', color='green')
plt.scatter(df[df['luna_llena']]['fecha'], df[df['luna_llena']]['viento_velocidad'], color='yellow', label='Cercano a Luna Llena', zorder=5)
plt.title('Velocidad del Viento vs Luna Llena')
plt.xlabel('Fecha')
plt.ylabel('Velocidad del Viento (km/h)')
plt.legend()
plt.grid()

# Rosa de los Vientos
plt.subplot(4, 1, 4, polar=True)
radians = np.deg2rad(df['viento_direccion'])
sizes = df['viento_velocidad']
colors = ['yellow' if luna else 'blue' for luna in df['luna_llena']]
plt.scatter(radians, sizes, c=colors, alpha=0.75, label='Dirección del Viento')
plt.title('Rosa de los Vientos')
plt.legend(['Cercano a Luna Llena', 'Otros días'], loc='upper right')

# Ajustar el diseño y guardar
plt.tight_layout()
os.makedirs('output', exist_ok=True)
plt.savefig('output/lluvia_nubes_viento_luna_llena_con_rosa.png')
plt.show()

# Correlación entre luna llena y variables climáticas
print("\nCorrelaciones con días cercanos a luna llena:")
for col in ['lluvia', 'nubes', 'viento_velocidad']:
    corr, _ = pearsonr(df['luna_llena'].astype(int), df[col])
    print(f"- {col.capitalize()}: {corr:.2f}")
