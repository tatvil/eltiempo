<?php
header('Content-Type: application/json');

// --- 1. Database Configuration (Example with external config) ---
// In a real scenario, this would come from a file outside the web root.
// For demonstration, let's just make it clear that this should be external.
define('DB_HOST', 'villaema.es');
define('DB_USER', 'villae9575');
define('DB_PASS', '_reHQ2ML'); // !! IMPORTANT: Store this securely in a real application !!
define('DB_NAME', 'inmodb');

// --- 2. Input Validation ---
// Assuming 'ciudad' comes from a GET request.
$ciudad = $_GET['ciudad'] ?? ''; // Use null coalescing operator for cleaner default

if (empty($ciudad)) {
    http_response_code(400); // Bad Request
    echo json_encode(["error" => "Parámetro 'ciudad' es requerido."]);
    exit(); // Stop script execution
}

// Optional: Further sanitize/validate the city name if needed (e.g., alphanumeric only)
// if (!preg_match('/^[a-zA-Z\s]+$/', $ciudad)) {
//     http_response_code(400);
//     echo json_encode(["error" => "El nombre de la ciudad contiene caracteres inválidos."]);
//     exit();
// }

// --- 3. Database Connection ---
$conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);

if ($conn->connect_error) {
    http_response_code(500); // Internal Server Error
    echo json_encode(["error" => "Error de conexión a la base de datos: " . $conn->connect_error]);
    exit();
}

// --- 4. Prepare and Execute Query ---
$stmt = $conn->prepare("
    SELECT DATE(fecha) AS dia,
           MIN(fecha) AS primera_fecha_del_dia,
           MIN(amanecer) AS amanecer,
           MAX(anochecer) AS anochecer,
           MAX(temp_max) AS temp_max,
           MIN(temp_min) AS temp_min,
           AVG(humedad) AS humedad,
           AVG(lluvia) AS lluvia,
           AVG(nubes) AS nubes,
           AVG(viento_velocidad) AS viento_velocidad,
           AVG(viento_direccion) AS viento_direccion
    FROM weather
    WHERE DATE(fecha) >= '2024-10-01'
        AND ciudad LIKE CONCAT('%', ?, '%')
    GROUP BY DATE(fecha)
    ORDER BY DATE(fecha) DESC
");

if (!$stmt) {
    http_response_code(500); // Internal Server Error
    echo json_encode(["error" => "Error al preparar la consulta: " . $conn->error]);
    $conn->close();
    exit();
}

$stmt->bind_param("s", $ciudad);
$stmt->execute();
$result = $stmt->get_result();

$datos = [];
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $datos[] = $row;
    }
    http_response_code(200); // OK
    echo json_encode($datos);
} else {
    // It's usually fine to return 200 OK with an empty array or a specific message
    // if no data is found, rather than a 404, unless it signifies a resource that
    // *should* exist but doesn't. For a query, 200 OK is typical.
    http_response_code(200); // OK
    echo json_encode(["message" => "No hay datos para la ciudad especificada"]);
}

// --- 5. Close Resources ---
$stmt->close();
$conn->close();
?>