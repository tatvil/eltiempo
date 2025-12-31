import calendar
import datetime
import mysql.connector
import yaml
import threading
import subprocess
import time
import tkinter as tk
from tkinter import ttk

# Función para ejecutar el script "recoger-datos-tiempo.py"
def ejecutar_recoger_datos():
    while True:
        subprocess.run(["python", "recoger-datos-tiempo.py"])
        time.sleep(1800)  # Espera 30 minutos

# Iniciar el hilo para recoger datos cada 30 minutos
thread = threading.Thread(target=ejecutar_recoger_datos, daemon=True)
thread.start()

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
WHERE DATE(fecha) = CURDATE()
GROUP BY DATE(fecha);
"""
cursor = conn.cursor()
cursor.execute(query)

# Obtener los resultados
resultados = cursor.fetchone()
cursor.close()
conn.close()

# Configurar los datos del tiempo
if resultados:
    amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = resultados
    clima_hoy = f"""
    Amanecer: {amanecer}
    Anochecer: {anochecer}
    Temperatura Mínima: {temp_min} °C
    Temperatura Máxima: {temp_max} °C
    Humedad: {int(humedad)}%
    Velocidad del Viento: {int(viento_velocidad)} m/s
    Dirección del Viento: {int(viento_direccion)}°
    Nubes: {int(nubes)}%
    Lluvia: {lluvia} mm
    """
else:
    clima_hoy = "No hay datos del tiempo para hoy."

# Crear la interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Bullet Journal")

# Arrancar la pantalla maximizada
root.state('zoomed')  # Para Windows

# Mostrar el calendario del mes actual
mes_actual = hoy.month
año_actual = hoy.year

calendario = calendar.TextCalendar()

# Mostrar el encabezado del calendario (ej. "September 2024")
encabezado_calendario = f"{calendar.month_name[mes_actual]} {año_actual}"
label_encabezado = ttk.Label(root, text=encabezado_calendario, font=("Courier", 18, "bold"))

# Crear un widget Text para el calendario
text_calendario = tk.Text(root, height=10, width=30, font=("Courier", 16))  # Usar fuente monoespaciada
calendario_mes = calendario.formatmonth(año_actual, mes_actual).split('\n', 1)[1]  # Eliminar la primera línea

text_calendario.insert(tk.END, calendario_mes)
text_calendario.config(state=tk.DISABLED)  # Hacer el texto no editable

# Usar pack para el encabezado y el calendario
label_encabezado.pack(pady=(10, 0))  # Añadir margen superior
text_calendario.pack(pady=(5, 10))  # Añadir margen entre el encabezado y el calendario

# Etiqueta para los datos del clima
label_clima = ttk.Label(root, text=clima_hoy, font=("Courier", 14))
label_clima.place(relx=0.5, rely=0.5, anchor="center")  # Colocar los datos del clima en el centro de la pantalla

# Ejecutar la aplicación
root.mainloop()
