<?php
header('Content-Type: application/json');

// Configuración de la base de datos
$db_host = 'villaema.es';
$db_user = 'villae9575';
$db_pass = '_reHQ2ML';
$db_name = 'inmodb';

// Conexión a la base de datos
$conn = new mysqli($db_host, $db_user, $db_pass, $db_name);
if ($conn->connect_error) {
    die(json_encode(["error" => "Error de conexión a la base de datos"]));
}

// Obtener la ciudad de la solicitud
$ciudad = isset($_GET['ciudad']) ? $conn->real_escape_string($_GET['ciudad']) : '';
if (empty($ciudad)) {
    echo json_encode(["error" => "Falta el parámetro ciudad"]);
    exit;
}

// Consulta SQL para obtener los datos del clima
$query="SELECT fecha, amanecer, anochecer, humedad,
                MAX(temp_max) AS temp_max, 
                MIN(temp_min) AS temp_min, 
                AVG(lluvia) AS lluvia, 
                AVG(nubes) AS nubes, 
                AVG(viento_velocidad) AS viento_velocidad,
                AVG(viento_direccion) AS viento_direccion
            FROM weather
            WHERE DATE(fecha) >= '2024-10-01'
                AND ciudad LIKE '%" . $ciudad . "%'
            GROUP BY DATE(fecha)
            ORDER BY DATE(fecha) DESC";
$result = $conn->query($query);

$datos = [];
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $datos[] = $row;
    }
    echo json_encode($datos);
} else {
    echo json_encode(["error" => "No hay datos para la ciudad especificada"]);
}

$conn->close();
?>
