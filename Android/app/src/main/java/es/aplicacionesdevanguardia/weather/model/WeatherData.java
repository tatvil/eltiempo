package es.aplicacionesdevanguardia.weather.model;

import com.google.gson.annotations.SerializedName;

public class WeatherData {
    @SerializedName("dia")
    private String dia;
    @SerializedName("primera_fecha_del_dia")
    private String primeraFechaDelDia;
    @SerializedName("amanecer")
    private String amanecer;
    @SerializedName("anochecer")
    private String anochecer;
    @SerializedName("temp_max")
    private String tempMax; // O Double, si es numérica y quieres operar con ella
    @SerializedName("temp_min")
    private String tempMin; // O Double
    @SerializedName("humedad")
    private String humedad; // O Double
    @SerializedName("lluvia")
    private String lluvia; // O Double
    @SerializedName("nubes")
    private String nubes; // O Double
    @SerializedName("viento_velocidad")
    private String vientoVelocidad; // O Double
    @SerializedName("viento_direccion")
    private String vientoDireccion; // O Double

    // Constructor (opcional, pero útil)
    public WeatherData(String dia, String primeraFechaDelDia, String amanecer, String anochecer,
                       String tempMax, String tempMin, String humedad, String lluvia,
                       String nubes, String vientoVelocidad, String vientoDireccion) {
        this.dia = dia;
        this.primeraFechaDelDia = primeraFechaDelDia;
        this.amanecer = amanecer;
        this.anochecer = anochecer;
        this.tempMax = tempMax;
        this.tempMin = tempMin;
        this.humedad = humedad;
        this.lluvia = lluvia;
        this.nubes = nubes;
        this.vientoVelocidad = vientoVelocidad;
        this.vientoDireccion = vientoDireccion;
    }

    // Getters y Setters para todos los campos
    // (Android Studio puede generarlos automáticamente: Alt+Insert o Clic Derecho > Generate > Getter and Setter)

    public String getDia() {
        return dia;
    }

    public void setDia(String dia) {
        this.dia = dia;
    }

    // ... Repite para todos los demás campos ...

    // Ejemplo para tempMax:
    public String getTempMax() {
        return tempMax;
    }

    public void setTempMax(String tempMax) {
        this.tempMax = tempMax;
    }

    public String getTempMin() { // Make sure this method exists
        return tempMin;
    }

    public void setTempMin(String tempMin) { // And this setter too
        this.tempMin = tempMin;
    }

    public String getHumedad() {
        return humedad;
    }

    public void setHumedad(String humedad) {
        this.humedad = humedad;
    }

    // Si los campos numéricos los quieres como Double:
    // public Double getTempMax() {
    //     try {
    //         return Double.parseDouble(tempMax);
    //     } catch (NumberFormatException e) {
    //         return null; // O manejar el error de otra forma
    //     }
    // }
    // public void setTempMax(String tempMax) {
    //     this.tempMax = tempMax;
    // }
}
