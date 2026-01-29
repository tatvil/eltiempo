using Microsoft.AspNetCore.Mvc;
using MySql.Data.MySqlClient;
using ElTiempoAPI.Models;

namespace ElTiempoAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TiempoController : ControllerBase
    {
        private readonly IConfiguration _config;

        public TiempoController(IConfiguration config)
        {
            _config = config;
        }

        // -------------------------
        // 1) Endpoint general (opcional)
        // -------------------------
        [HttpGet]
        public IActionResult Get()
        {
            // tu código original aquí...
            return Ok("OK");
        }

        // -------------------------
        // 2) AQUÍ VA TU FILTRO POR CIUDAD
        // -------------------------
        [HttpGet("ciudad/{ciudad}")]
        public IActionResult GetPorCiudad(string ciudad)
        {
            var lista = new List<DatoTiempo>();
            string connString = _config.GetConnectionString("DefaultConnection");

            using var conn = new MySqlConnection(connString);
            conn.Open();

            string sql = "SELECT * FROM weather WHERE ciudad = @ciudad";

            using var cmd = new MySqlCommand(sql, conn);
            cmd.Parameters.AddWithValue("@ciudad", ciudad);

            using var reader = cmd.ExecuteReader();

            while (reader.Read())
            {
                lista.Add(Mapear(reader));
            }

            return Ok(lista);
        }

        // -------------------------
        // 3) Método Mapear (debe estar dentro del controlador)
        // -------------------------
        private DatoTiempo Mapear(MySqlDataReader reader)
        {
            return new DatoTiempo
            {
                Id = reader.GetInt32("id"),
                Fecha = reader.GetDateTime("fecha"),
                Ciudad = reader.GetString("ciudad"),
                Amanecer = reader.GetTimeSpan("amanecer"),
                Anochecer = reader.GetTimeSpan("anochecer"),
                Temp_Min = reader.GetInt32("temp_min"),
                Temp_Max = reader.GetInt32("temp_max"),
                Humedad = reader.GetInt32("humedad"),
                Viento_Velocidad = reader.GetInt32("viento_velocidad"),
                Viento_Direccion = reader.GetInt32("viento_direccion"),
                Nubes = reader.GetInt32("nubes"),
                Lluvia = reader.GetInt32("lluvia")
            };
        }

        // -------------------------
        // 4) Endpoint para obtener la lista de ciudades
        // -------------------------
        [HttpGet("ciudades")]
        public IActionResult GetCiudades()
        {
            var lista = new List<string>();
            string connString = _config.GetConnectionString("DefaultConnection");

            using var conn = new MySqlConnection(connString);
            conn.Open();

            string sql = "SELECT DISTINCT ciudad FROM weather ORDER BY ciudad";

            using var cmd = new MySqlCommand(sql, conn);
            using var reader = cmd.ExecuteReader();

            while (reader.Read())
            {
                lista.Add(reader.GetString("ciudad"));
            }

            return Ok(lista);
        }

    }
}


