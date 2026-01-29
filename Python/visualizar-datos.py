import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import yaml
import os

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
SELECT fecha, amanecer, anochecer, min(temp_min) AS temp_min, max(temp_max) AS temp_max, avg(humedad) AS humedad, AVG(viento_velocidad) AS viento_velocidad, AVG(viento_direccion) AS viento_direccion, avg(nubes) AS nubes, max(lluvia) as lluvia
FROM `weather` 
GROUP BY DATE(fecha)
ORDER BY DATE(fecha)
"""
df = pd.read_sql(query, conn)

# Cerrar la conexión
conn.close()

# Configurar la visualización
plt.figure(figsize=(10, 5))
plt.plot(df['fecha'], df['temp_max'], label='Temperatura Máxima', marker='o', color='red')
plt.plot(df['fecha'], df['temp_min'], label='Temperatura Mínima', marker='o', color='blue')
plt.plot(df['fecha'], df['humedad'], label='Humedad', marker='o', color='green')
plt.plot(df['fecha'], df['viento_velocidad'], label='Viento Velocidad', marker='o', color='orange')
plt.plot(df['fecha'], df['viento_direccion'], label='Viento Dirección', marker='o', color='purple')
plt.plot(df['fecha'], df['nubes'], label='Nubes', marker='o', color='brown')
plt.plot(df['fecha'], df['lluvia'], label='Lluvia', marker='o', color='black')
plt.fill_between(df['fecha'], df['temp_min'], df['temp_max'], color='lightgrey', alpha=0.5)

# Configuración del gráfico
plt.title('Temperaturas Mínimas y Máximas por Día')
plt.xlabel('Fecha')
plt.ylabel('Temperatura (°C)')
plt.xticks(rotation=45)
plt.legend()
plt.grid()

# Guardar el gráfico como imagen
output_path = os.path.join('output', 'temperaturas_por_dia.png')
os.makedirs('output', exist_ok=True)  # Crear la carpeta si no existe
plt.savefig(output_path, bbox_inches='tight')

# Mostrar el gráfico
plt.tight_layout()
plt.show()

print(f"Gráfico guardado en: {output_path}")
