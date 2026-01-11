namespace ElTiempoAPI.Models
{
    public class RegistroViento
    {
        public DateTime Fecha { get; set; }
        public double VientoVelocidad { get; set; }
        public double VientoDireccion { get; set; }
        public bool EsLunaLlena { get; set; }
    }
}

