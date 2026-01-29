package es.aplicacionesdevanguardia.weather.api;

import es.aplicacionesdevanguardia.weather.model.WeatherData; // Asegúrate de importar tu clase modelo
import java.util.List;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;

public interface WeatherApiService {
//    @GET("villaema.es/api/weather.php") // La ruta relativa a tu base URL
    @GET("http://villaema.es/api/api-weather-reverse.php")
    Call<List<WeatherData>> getWeatherByCity(@Query("ciudad") String ciudad);
}