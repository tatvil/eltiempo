using ElTiempoAPI.Models;
using MySql.Data.MySqlClient;

namespace ElTiempoAPI.Services
{
    public class RosaService
    {
        private readonly IConfiguration _config;

        private static readonly List<DateTime> LunasLlenas = new()
        {
            new DateTime(2024,10,17), new DateTime(2024,11,15), new DateTime(2024,12,15),
            new DateTime(2025,01,13), new DateTime(2025,02,12), new DateTime(2025,03,14),
            new DateTime(2025,04,13), new DateTime(2025,05,12), new DateTime(2025,06,11),
            new DateTime(2025,07,10), new DateTime(2025,08,09), new DateTime(2025,09,07),
            new DateTime(2025,10,06), new DateTime(2025,11,05), new DateTime(2025,12,05),
            new DateTime(2026,01,04), new DateTime(2026,02,03), new DateTime(2026,03,05),
            new DateTime(2026,04,04), new DateTime(2026,05,04), new DateTime(2026,06,02),
            new DateTime(2026,07,02), new DateTime(2026,08,01), new DateTime(2026,08,30),
            new DateTime(2026,09,29), new DateTime(2026,10,29), new DateTime(2026,11,27),
            new DateTime(2026,12,27)
        };

        public RosaService(IConfiguration config)
        {
            _config = config;
        }

        public List<RegistroViento> ObtenerDatos(string ciudad, string desde)
        {
            var lista = new List<RegistroViento>();

            try
            {
                string? connString = _config.GetSection("ConnectionStrings")?.GetSection("DefaultConnection")?.Value;
                if (string.IsNullOrEmpty(connString))
                    throw new Exception("La cadena de conexión MySqlConnection no está configurada.");

                using var conn = new MySqlConnection(connString);
                conn.Open();

                string sql = @"
                    SELECT DATE(fecha) AS fecha,
                           AVG(viento_velocidad) AS viento_velocidad,
                           AVG(viento_direccion) AS viento_direccion
                    FROM weather
                    WHERE DATE(fecha) >= @desde
                      AND ciudad LIKE @ciudad
                    GROUP BY DATE(fecha)
                    ORDER BY DATE(fecha)
                ";

                using var cmd = new MySqlCommand(sql, conn);
                cmd.Parameters.AddWithValue("@desde", desde);
                cmd.Parameters.AddWithValue("@ciudad", $"%{ciudad}%");

                using var reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    var fecha = reader.GetDateTime("fecha");

                    double velocidad = reader.IsDBNull(reader.GetOrdinal("viento_velocidad"))
                        ? 0
                        : reader.GetDouble("viento_velocidad");

                    double direccion = reader.IsDBNull(reader.GetOrdinal("viento_direccion"))
                        ? 0
                        : reader.GetDouble("viento_direccion");

                    lista.Add(new RegistroViento
                    {
                        Fecha = fecha,
                        VientoVelocidad = velocidad,
                        VientoDireccion = direccion,
                        EsLunaLlena = LunasLlenas.Any(l => Math.Abs((fecha - l).Days) <= 2)
                    });
                }
            }
            catch (Exception ex)
            {
                // Esto te permitirá ver el error real en Azure
                throw new Exception("Error en RosaService: " + ex.Message);
            }

            return lista;
        }
    }
}

