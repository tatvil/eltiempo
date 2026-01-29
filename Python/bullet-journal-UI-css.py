from datetime import datetime, timedelta
import calendar
from click import style
import mysql.connector
import yaml
import threading
import subprocess
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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
        time.sleep(3600)  # Espera 60 minutos

def formatear_datos_tiempo(resultados):
    if resultados:
        amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = resultados
        
        # Verificar si amanecer y anochecer son datetime o timedelta
        if isinstance(amanecer, datetime):
            amanecer = amanecer.strftime('%H:%M')
        elif isinstance(amanecer, timedelta):
            amanecer = str(amanecer)  # Manejar timedelta si es necesario

        if isinstance(anochecer, datetime):
            anochecer = anochecer.strftime('%H:%M')
        elif isinstance(anochecer, timedelta):
            anochecer = str(anochecer)  # Manejar timedelta si es necesario

        return amanecer, anochecer, round(temp_min), round(temp_max), int(humedad), int(viento_velocidad), int(viento_direccion), int(nubes), round(lluvia, 2)

def crear_calendario_mes(anno, mes):
    # Crear un calendario para el mes y año dados
    cal = None
    # Verificar si el mes es válido (1-12)
    if mes < 1 or mes > 12:
        return None
    else:
        # Buscar el primer día de la semana para el mes y año dados
        primerdia, dias = calendar.monthrange(int(anno), int(mes))
        print(primerdia, dias)
        # Crear una tabla de calendario para el mes y año dados
        frame_tabla = ttk.Frame(frame_calendario, padding="5", relief="solid", borderwidth=2)
        frame_tabla.pack(pady=(0, 10))  # Añadir margen inferior para separación

        # Definir el tamaño de la tabla
        filas = 7
        columnas = 7

        # Crear la tabla 7x6
        for fila in range(filas):
            for columna in range(columnas):
                # Crear una etiqueta para cada celda
                if fila == 0:
                    # Mostrar los nombres de los días de la semana
                    etiqueta = ttk.Label(frame_tabla, text=calendar.day_abbr[columna], borderwidth=1, relief="solid")
                elif fila == 1 and columna < primerdia:
                    # Dejar las primeras celdas vacías antes del primer día
                    etiqueta = ttk.Label(frame_tabla, text="", borderwidth=1, relief="solid")
                elif (fila - 1) * 7 + columna - primerdia + 1 > dias:
                    # Dejar las últimas celdas vacías después del último día
                    etiqueta = ttk.Label(frame_tabla, text="", borderwidth=1, relief="solid")
                else:
                    # Mostrar los días del mes
                    etiqueta = ttk.Label(frame_tabla, text=(fila - 1) * 7 + columna - primerdia + 1, borderwidth=1, relief="solid")
                etiqueta.grid(row=fila, column=columna, sticky="nsew")
                etiqueta.grid_rowconfigure(0, weight=1)


        # Configurar las filas y columnas para que se expandan
        for i in range(filas):
            frame_tabla.grid_rowconfigure(i, weight=1)
        for i in range(columnas):
            frame_tabla.grid_columnconfigure(i, weight=1)

        return frame_tabla

def recoger_datos_tiempo():

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

    # Consultar los datos del tiempo de hoy
    query = """
    SELECT amanecer, anochecer, MIN(temp_min), MAX(temp_max), humedad, MAX(viento_velocidad), AVG(viento_direccion), nubes, SUM(lluvia)
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
    return resultados

# Función para formatear los datos del tiempo
def formatear_datos_tiempo(resultados):
    if resultados:
        amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = resultados
        
        # Amanecer y anochecer
        total_seconds = int(amanecer.total_seconds())
        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        amanecer = f"{horas:02}:{minutos:02}"
        
        total_seconds = int(anochecer.total_seconds())
        horas = total_seconds // 3600
        minutos = (total_seconds % 3600) // 60
        anochecer = f"{horas:02}:{minutos:02}"

        return amanecer, anochecer, round(temp_min), round(temp_max), int(humedad), int(viento_velocidad), int(viento_direccion), int(nubes), round(lluvia, 2)
    return None

# Iniciar el hilo para recoger datos cada 60 minutos
thread = threading.Thread(target=ejecutar_recoger_datos, daemon=True)
thread.start()

# Crear ventana principal
root = tk.Tk()  
root.title("Bullet Journal")
root.geometry("800x600")

# Cargar y aplicar estilos desde el archivo styles.css
estilos = cargar_estilos('styles.css')  # Cargar estilos en una variable
aplicar_estilos(style, estilos)  # Aplicar los estilos al estilo ttk

# FECHA
# Crear marco superior para la fecha
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

# TIEMPO
# Configurar los datos del tiempo
datos_tiempo = formatear_datos_tiempo(recoger_datos_tiempo())

# Cargar y redimensionar iconos usando Pillow
amanecer_img = Image.open("icons/amanecerflecha.png")
amanecer_img = amanecer_img.resize((25, 25))  # Especifica el tamaño deseado (ancho, alto)
amanecer_icon = ImageTk.PhotoImage(amanecer_img)

anochecer_img = Image.open("icons/sunriseflechadebajo.png")
anochecer_img = anochecer_img.resize((25, 25))  # Especifica el tamaño deseado
anochecer_icon = ImageTk.PhotoImage(anochecer_img)

# Crear marco para los datos del tiempo
frame_tiempo = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_tiempo.grid(row=1, column=0, columnspan=2, sticky="ew")

if datos_tiempo:
    amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia = datos_tiempo
 
    frame_amanecer_anochecer = ttk.Frame(frame_tiempo)
    frame_amanecer_anochecer.pack(pady=5)

    # Etiqueta con imagen de Amanecer
    label_amanecer_icon = ttk.Label(frame_amanecer_anochecer, image=amanecer_icon)
    label_amanecer_icon.pack(side="left", padx=5)
    
    # Etiqueta para la hora de Amanecer
    label_amanecer_hora = ttk.Label(frame_amanecer_anochecer, text=amanecer, font=("Courier", 12))
    label_amanecer_hora.pack(side="left", padx=5)
    
    # Etiqueta con imagen de Anochecer
    label_anochecer_icon = ttk.Label(frame_amanecer_anochecer, image=anochecer_icon)
    label_anochecer_icon.pack(side="left", padx=5)
    
    # Etiqueta para la hora de Anochecer
    label_anochecer_hora = ttk.Label(frame_amanecer_anochecer, text=anochecer, font=("Courier", 12))
    label_anochecer_hora.pack(side="left", padx=5)

    # Otros datos del clima
    clima_otros = f"""Temperatura: {temp_min} °C / {temp_max} °C - Humedad: {humedad}% - Viento: {viento_velocidad} m/s - Dirección: {viento_direccion}° - Nubes: {nubes}% - Lluvia: {lluvia} mm"""
    
    label_tiempo = ttk.Label(frame_tiempo, text=clima_otros, font=("Courier", 12))
    label_tiempo.pack(padx=10, pady=10)
else:
    label_tiempo = ttk.Label(frame_tiempo, text="No hay datos del tiempo para hoy.", font=("Courier", 12))
    label_tiempo.pack(padx=10, pady=10)

# Mantener una referencia de las imágenes
label_amanecer_icon.image = amanecer_icon
label_anochecer_icon.image = anochecer_icon

# CALENDARIO
# Crear marco izquierdo para el calendario
frame_calendario = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_calendario.grid(row=2, column=0, sticky="nsew")

# Mostrar el encabezado del calendario (ej. "Septiembre 2024")
encabezado_calendario = f"{mesActual} de {annoActual}"
label_encabezado = ttk.Label(frame_calendario, text=encabezado_calendario, font=("Courier", 14, "bold"))
label_encabezado.pack(pady=(0, 5))  # Margen inferior para separación

# Crear un widget Text para el calendario
text_calendario = tk.Text(frame_calendario, height=10, width=24, font=("Courier", 12))  # Usar fuente monoespaciada
calendario_mes = calendar.TextCalendar().formatmonth(int(annoActual), int(hoy.month))
calendario_mes = crear_calendario_mes(annoActual, hoy.month)

# AGENDA
# Crear marco izquierdo para la agenda
frame_agenda = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_agenda.grid(row=3, column=0, sticky="nsew")
label_agenda = ttk.Label(frame_agenda, text="Agenda")
label_agenda.pack(padx=10, pady=10)

# PANTALLA DE INFORMACION GENERAL
# Crear marco derecho para otras cosas
# Ideas: 
#   - Tareas pendientes, notas, recordatorios, etc.
#   - Santo del dia, Santos proximos, novenas
#   - Frases motivacionales, citas, pensamientos
#   - Cumpleaños, aniversarios, eventos especiales
#   - Fase de la luna

frame_otras_cosas = ttk.Frame(root, padding="5", relief="solid", borderwidth=2)
frame_otras_cosas.grid(row=2, column=1, rowspan=2, sticky="nsew")
label_otras_cosas = ttk.Label(frame_otras_cosas, text="Otras cosas que aún no he pensado")
label_otras_cosas.pack(padx=10, pady=10)

# Configurar las filas y columnas para que se expandan
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=3)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)

# Iniciar el bucle principal
root.mainloop()
