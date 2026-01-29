import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import os
import numpy as np
import datetime

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

ciudad='Alfas'
fecha=datetime.datetime.now().strftime('%Y-%m-%d')

# Consultar los datos
query = f"""
SELECT fecha, 
       AVG(viento_velocidad) AS viento_velocidad,
       AVG(viento_direccion) AS viento_direccion
FROM weather
WHERE DATE(fecha) >= '2024-10-01'
        AND ciudad LIKE '%{ciudad}%'
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

# Rosa de los Vientos
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, polar=True)  # Configuración del eje polar
radians = np.deg2rad(df['viento_direccion'])
sizes = df['viento_velocidad']
colors = ['orange' if luna else 'blue' for luna in df['luna_llena']]

# Agregar una flecha para indicar el norte
ax.annotate('', xy=(0, max(sizes)), xytext=(0, 0),
            arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='->', lw=2))

# Dibujar la rosa de los vientos
scatter = ax.scatter(radians, sizes, c=colors, alpha=0.75)
ax.set_title(f'Rosa de los Vientos - {ciudad}', va='bottom')

# Guardar y mostrar
os.makedirs('output', exist_ok=True)
plt.savefig(f'output/rosa_de_vientos_{ciudad}_{fecha}.png')
plt.show()