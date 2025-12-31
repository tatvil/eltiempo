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
$ciudad = isset($_GET['ciudad']) ? trim($_GET['ciudad']) : '';
if (empty($ciudad)) {
    echo json_encode(["error" => "Falta el parámetro ciudad"]);
    exit;
}

// Consulta segura con prepared statements
$query = "SELECT fecha, amanecer, anochecer, humedad,
                 MAX(temp_max) AS temp_max, 
                 MIN(temp_min) AS temp_min, 
                 AVG(lluvia) AS lluvia, 
                 AVG(nubes) AS nubes, 
                 AVG(viento_velocidad) AS viento_velocidad,
                 AVG(viento_direccion) AS viento_direccion
          FROM weather
          WHERE DATE(fecha) >= '2024-10-01'
          AND ciudad = ?
          GROUP BY DATE(fecha)
          ORDER BY DATE(fecha)";

$stmt = $conn->prepare($query);
$stmt->bind_param("s", $ciudad);
$stmt->execute();
$result = $stmt->get_result();

$datos = [];
while ($row = $result->fetch_assoc()) {
    // Convertimos fecha a ISO 8601
    $row['fecha'] = date('c', strtotime($row['fecha']));
    $datos[] = $row;
}

echo json_encode($datos, JSON_UNESCAPED_UNICODE);

$stmt->close();
$conn->close();
?>
