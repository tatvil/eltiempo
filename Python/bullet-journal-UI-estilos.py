from datetime import datetime, timedelta
import calendar
import mysql.connector
import yaml
import threading
import subprocess
import time
import tkinter as tk
from tkinter import ttk

# Función para leer el archivo styles.css
def cargar_estilos(ruta_archivo):
    estilos = {}
    with open(ruta_archivo, 'r') as archivo:
        for linea in archivo:
            linea = linea.strip()
            if linea and not linea.startswith('/*') and not linea.startswith('//'):  # Ignorar comentarios
                if '{' in linea:
                    widget = linea.split('{')[0].strip()
                    estilos[widget] = {}
                elif '}' not in linea:
                    propiedad, valor = linea.split(':')
                    estilos[widget][propiedad.strip()] = valor.strip().replace(';', '')
    return estilos

# Aplicar los estilos cargados a los widgets ttk
def aplicar_estilos(style, estilos):
    for widget, propiedades in estilos.items():
        for propiedad, valor in propiedades.items():
            if propiedad == "background-color":
                style.configure(widget, background=valor)
            elif propiedad == "foreground-color":
                style.configure(widget, foreground=valor)
            elif propiedad == "font":
                style.configure(widget, font=valor)

# Función para ejecutar el script "recoger-datos-tiempo.py"
def ejecutar_recoger_datos():
    while True:
        subprocess.run(["python", "recoger-datos-tiempo.py"])
        time.sleep(1800)  # Espera 30 minutos

def formatear_datos_tiempo(resultados):
    if resultados:
        amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = resultados
        
        if isinstance(amanecer, datetime):
            amanecer = amanecer.strftime('%H:%M')
        elif isinstance(amanecer, timedelta):
            amanecer = str(amanecer)

        if isinstance(anochecer, datetime):
            anochecer = anochecer.strftime('%H:%M')
        elif isinstance(anochecer, timedelta):
            anochecer = str(anochecer)

        return amanecer, anochecer, round(temp_min), round(temp_max), int(humedad), int(viento_velocidad), int(viento_direccion), int(nubes), round(lluvia, 2)

# Crear el calendario del mes
def crear_calendario_mes(frame_calendario, anno, mes):
    primerdia, dias = calendar.monthrange(anno, mes)
    
    frame_tabla = ttk.Frame(frame_calendario, padding="5", relief="solid", borderwidth=2)
    frame_tabla.pack(pady=(0, 10))

    filas, columnas = 7, 7

    for fila in range(filas):
        for columna in range(columnas):
            if fila == 0:
                etiqueta = ttk.Label(frame_tabla, text=calendar.day_abbr[columna], borderwidth=1, relief="solid")
            elif fila == 1 and columna < primerdia:
                etiqueta = ttk.Label(frame_tabla, text="", borderwidth=1, relief="solid")
            elif (fila - 1) * 7 + columna - primerdia + 1 > dias:
                etiqueta = ttk.Label(frame_tabla, text="", borderwidth=1, relief="solid")
            else:
                etiqueta = ttk.Label(frame_tabla, text=(fila - 1) * 7 + columna - primerdia + 1, borderwidth=1, relief="solid")
            etiqueta.grid(row=fila, column=columna, sticky="nsew")

    for i in range(filas):
        frame_tabla.grid_rowconfigure(i, weight=1)
    for i in range(columnas):
        frame_tabla.grid_columnconfigure(i, weight=1)

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

query = """
SELECT amanecer, anochecer, MIN(temp_min), MAX(temp_max), humedad, MAX(viento_velocidad), AVG(viento_direccion), nubes, SUM(lluvia)
FROM weather
WHERE DATE(fecha) = CURDATE()
GROUP BY DATE(fecha);
"""
cursor = conn.cursor()
cursor.execute(query)
resultados = cursor.fetchone()
cursor.close()
conn.close()

# Crear y aplicar el estilo
style = ttk.Style()
style.theme_use('clam')

# Cargar y aplicar estilos desde el archivo styles.css
estilos = cargar_estilos('styles.css')
aplicar_estilos(style, estilos)

# Crear ventana principal
root = tk.Tk()
root.title("Bullet Journal")
root.geometry("800x600")

# Marco para la fecha
frame_fecha = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_fecha.grid(row=0, column=0, columnspan=2, sticky="ew")

hoy = datetime.now()
semana = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
diaSemana = semana[int(hoy.strftime("%w"))]
diaActual = hoy.strftime("%d")
mesActual = meses[int(hoy.strftime("%m")) - 1]
annoActual = hoy.strftime("%Y")
fecha = f"{diaSemana}, {diaActual} de {mesActual} de {annoActual}"

label_fecha = ttk.Label(frame_fecha, text=f'{fecha}', font=("Arial", 16))
label_fecha.pack(padx=10, pady=10)

# Mostrar datos del tiempo
datos_tiempo = formatear_datos_tiempo(resultados)

frame_tiempo = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_tiempo.grid(row=1, column=0, columnspan=2, sticky="ew")

if datos_tiempo:
    amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = datos_tiempo
    clima_hoy = f"""Amanecer: {amanecer} - Anochecer: {anochecer} - Temp: {temp_min}°C / {temp_max}°C - Humedad: {humedad}% 
                    - Viento: {viento_velocidad} m/s - Dirección: {viento_direccion}° - Nubes: {nubes}% - Lluvia: {lluvia} mm"""
else:
    clima_hoy = "No hay datos del tiempo para hoy."

label_tiempo = ttk.Label(frame_tiempo, text=clima_hoy, font=("Courier", 12))
label_tiempo.pack(padx=10, pady=10)

# Crear calendario
frame_calendario = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_calendario.grid(row=2, column=0, sticky="nsew")

encabezado_calendario = f"{mesActual} de {annoActual}"
label_encabezado = ttk.Label(frame_calendario, text=encabezado_calendario, font=("Courier", 14, "bold"))
label_encabezado.pack(pady=(0, 5))

crear_calendario_mes(frame_calendario, int(annoActual), int(hoy.month))

# Otras configuraciones de interfaz
frame_agenda = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_agenda.grid(row=3, column=0, sticky="nsew")
label_agenda = ttk.Label(frame_agenda, text="Agenda")
label_agenda.pack(padx=10, pady=10)

frame_otras_cosas = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_otras_cosas.grid(row=3, column=1, sticky="nsew")
label_otras_cosas = ttk.Label(frame_otras_cosas, text="Otras cosas")
label_otras_cosas.pack(padx=10, pady=10)

root.mainloop()
