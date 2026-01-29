namespace ElTiempoAPI.Models
{
    public class DatoTiempo
    {
        public int Id { get; set; }
        public DateTime Fecha { get; set; }
        public string Ciudad { get; set; }
        public TimeSpan Amanecer { get; set; }
        public TimeSpan Anochecer { get; set; }
        public int Temp_Min { get; set; }
        public int Temp_Max { get; set; }
        public int Humedad { get; set; }
        public int Viento_Velocidad { get; set; }
        public int Viento_Direccion { get; set; }
        public int Nubes { get; set; }
        public int Lluvia { get; set; }
    }
}

