<?php
$servername = "villaema.es";
$username = "villae9575";
$password = "_reHQ2ML";
$dbname = "inmodb";

// Crear conexión
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar conexión
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$hoy = date("Y-m-d");

$sql = "SELECT amanecer, anochecer, MIN(temp_min), MAX(temp_max), MAX(viento_velocidad), AVG(viento_direccion), MAX(nubes), MAX(lluvia) 
        FROM weather 
        WHERE fecha LIKE '%" . $hoy . "%'";

$result = $conn->query($sql);

$data = array();
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    echo json_encode($data);
} else {
    echo json_encode(array("message" => "No data found"));
}
$conn->close();
?>
