<?php
header('Content-Type: application/json');

$servername = "villaema.es";
$username = "villae9575";
$password = "_reHQ2ML";
$dbname = "inmodb";

$conn = new mysqli($servername, $username, $password, $dbname);
$conn->set_charset("utf8mb4");

if ($conn->connect_error) {
    die(json_encode(["error" => "Conexión fallida: " . $conn->connect_error]));
}

$ciudad = $_GET['ciudad'] ?? null; // Obtener ciudad de la URL si se pasa
$sql = "SELECT fecha, ciudad, temp_max, temp_min, humedad, lluvia FROM weather";
if ($ciudad) {
    $ciudad = $conn->real_escape_string($ciudad);
    $sql .= " WHERE ciudad = '$ciudad'";
}
$sql .= " ORDER BY fecha DESC LIMIT 10"; // Ejemplo: últimas 10 entradas

$result = $conn->query($sql);
$data = [];

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

echo json_encode($data);
$conn->close();
?>