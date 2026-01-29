<?php
// Habilitar la visualización de errores
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Configuración de conexión a MySQL
$servername = "villaema.es";
$username = "villae9575";
$password = "_reHQ2ML";
$dbname = "inmodb";

// Crear conexión
$conn = new mysqli($servername, $username, $password, $dbname);
$conn->set_charset("utf8mb4"); // Establecer la codificación a utf8mb4

// Verificar conexión
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

// Reemplaza 'your_api_key' por tu clave API.
$API_KEY = '69ef7f26726bba12b03c74b1e97b550f';
$ciudades = [
    'Madrid,ES',                    // Madrid, España
    'Alfas%20del%20Pi,ES',          // Alfaz del Pi, Alicante
    'L\'Ampolla,ES'                 // L'Ampolla, Tarragona
];

// Función para obtener datos del tiempo
function obtener_datos_tiempo($url) {
    $response = file_get_contents($url);
    if ($response !== FALSE) {
        return json_decode($response, true);  // Devuelve los datos en formato JSON.
    } else {
        echo "Error al obtener los datos del tiempo";
        return null;
    }
}

// Función para convertir el timestamp a una fecha legible
function convertir_fecha($timestamp) {
    return date('Y-m-d H:i:s', $timestamp);  // Formato de fecha
}

// Función para reemplazar caracteres especiales en los nombres de ciudades
function limpiar_nombre_ciudad($nombre) {
    $nombre = str_replace(
        ['Á', 'É', 'Í', 'Ó', 'Ú', 'á', 'é', 'í', 'ó', 'ú', 'ñ', 'Ñ'],
        ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u', 'n', 'N'],
        $nombre
    );
    return $nombre;
}

// Función para guardar los datos en la tabla weather
function guardar_datos_tiempo($conn, $datos) {
    $ciudad = limpiar_nombre_ciudad($datos['name']); // Limpiar caracteres especiales
    $fecha = convertir_fecha($datos['dt']);  // Hora actual del clima
    $amanecer = convertir_fecha($datos['sys']['sunrise']);
    $anochecer = convertir_fecha($datos['sys']['sunset']);
    $temp_min = $datos['main']['temp_min'];
    $temp_max = $datos['main']['temp_max'];
    $humedad = $datos['main']['humidity'];
    $viento_velocidad = $datos['wind']['speed'];
    $viento_direccion = $datos['wind']['deg'];
    $nubes = $datos['clouds']['all'];
    $lluvia = isset($datos['rain']['1h']) ? $datos['rain']['1h'] : 0;  // Lluvia en la última hora, si existe

    // Insertar los datos en la tabla
    $stmt = $conn->prepare('
        INSERT INTO weather (fecha, ciudad, amanecer, anochecer, temp_min, temp_max, humedad, viento_velocidad, viento_direccion, nubes, lluvia)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ');
    $stmt->bind_param('ssssddddddd', $fecha, $ciudad, $amanecer, $anochecer, $temp_min, $temp_max, $humedad, $viento_velocidad, $viento_direccion, $nubes, $lluvia);

    // Ejecutar y confirmar cambios
    if ($stmt->execute()) {
        echo "Datos de $ciudad guardados correctamente en la base de datos MySQL.<br>";
    } else {
        echo "Error al guardar los datos de $ciudad: " . $stmt->error . "<br>";
    }

    $stmt->close();
}

// Bucle para cada ciudad y guardar los datos
foreach ($ciudades as $ciudad) {
    $URL = "http://api.openweathermap.org/data/2.5/weather?q=$ciudad&appid=$API_KEY&units=metric";
    $datos_tiempo = obtener_datos_tiempo($URL);
    if ($datos_tiempo) {
        guardar_datos_tiempo($conn, $datos_tiempo);
    }
}

// Cerrar la conexión al terminar
$conn->close();
?>
