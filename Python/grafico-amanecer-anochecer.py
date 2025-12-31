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
SELECT fecha, amanecer, anochecer
FROM weather
WHERE DATE(fecha) >= '2024-10-01'
  AND ciudad LIKE '%madrid%'
GROUP BY DATE(fecha)
ORDER BY DATE(fecha)
"""
df = pd.read_sql(query, conn)
conn.close()

# Convertir fechas y horas a formato datetime para graficar correctamente
df['fecha'] = pd.to_datetime(df['fecha'])
df['amanecer'] = pd.to_timedelta(df['amanecer'].astype(str))
df['anochecer'] = pd.to_timedelta(df['anochecer'].astype(str))

# Convertimos las horas a minutos desde medianoche para graficar
df['amanecer_min'] = df['amanecer'].dt.total_seconds() / 60
df['anochecer_min'] = df['anochecer'].dt.total_seconds() / 60

x = np.arange(len(df))

# Suavizar las curvas
def smooth_curve(x, y):
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spline = make_interp_spline(x, y, k=3)
    y_smooth = spline(x_smooth)
    return x_smooth, y_smooth

x_smooth, amanecer_smooth = smooth_curve(x, df['amanecer_min'])
_, anochecer_smooth = smooth_curve(x, df['anochecer_min'])

# Configurar visualización
plt.figure(figsize=(10, 5))
plt.plot(x_smooth, amanecer_smooth, label='Amanecer', color='red')
plt.plot(x_smooth, anochecer_smooth, label='Anochecer', color='blue')

plt.title('Amanecer y Anochecer por Día')
plt.xlabel('Fecha')
plt.ylabel('Hora del día')

# Mostrar una etiqueta de fecha cada 3 días para evitar apelotonamiento
step = 3
plt.xticks(
    ticks=x[::step],
    labels=df['fecha'].dt.strftime('%Y-%m-%d')[::step],
    rotation=45
)

# Convertir los minutos en etiquetas legibles para el eje Y
y_ticks = np.arange(300, 1301, 60)  # Desde las 5:00 (300 min) hasta las 21:40 (1300 min)
y_labels = [f"{int(mins//60):02d}:{int(mins%60):02d}" for mins in y_ticks]
plt.yticks(y_ticks, y_labels)

plt.legend()
plt.grid()
plt.tight_layout()

# Guardar y mostrar el gráfico
output_path = os.path.join('output', 'amanecer-anochecer.png')
os.makedirs('output', exist_ok=True)
plt.savefig(output_path, bbox_inches='tight')
plt.show()

print(f"Gráfico guardado en: {output_path}")
