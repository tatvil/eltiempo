package es.aplicacionesdevanguardia.weather;

public class Clima {
        private String fecha;
        private String amanecer;
        private String anochecer;
        private double humedad;
        private double tempMax;
        private double tempMin;
        private double lluvia;
        private double nubes;
        private double vientoVelocidad;
        private double vientoDireccion;

        // Agregar los métodos getter y setter para acceder a los datos

        public String getFecha() {
            return fecha;
        }

        public void setFecha(String fecha) {
            this.fecha = fecha;
        }

        public String getAmanecer() {
            return amanecer;
        }

        public void setAmanecer(String amanecer) {
            this.amanecer = amanecer;
        }

        public String getAnochecer() {
            return anochecer;
        }

        public void setAnochecer(String anochecer) {
            this.anochecer = anochecer;
        }

        public double getHumedad() {
            return humedad;
        }

        public void setHumedad(double humedad) {
            this.humedad = humedad;
        }

        public double getTempMax() {
            return tempMax;
        }

        public void setTempMax(double tempMax) {
            this.tempMax = tempMax;
        }

        public double getTempMin() {
            return tempMin;
        }

        public void setTempMin(double tempMin) {
            this.tempMin = tempMin;
        }

        public double getLluvia() {
            return lluvia;
        }

        public void setLluvia(double lluvia) {
            this.lluvia = lluvia;
        }

        public double getNubes() {
            return nubes;
        }

        public void setNubes(double nubes) {
            this.nubes = nubes;
        }

        public double getVientoVelocidad() {
            return vientoVelocidad;
        }

        public void setVientoVelocidad(double vientoVelocidad) {
            this.vientoVelocidad = vientoVelocidad;
        }

        public double getVientoDireccion() {
            return vientoDireccion;
        }

        public void setVientoDireccion(double vientoDireccion) {
            this.vientoDireccion = vientoDireccion;
        }
}
