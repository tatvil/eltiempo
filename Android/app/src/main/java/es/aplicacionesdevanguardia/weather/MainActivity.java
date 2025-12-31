package es.aplicacionesdevanguardia.weather;

import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import es.aplicacionesdevanguardia.weather.api.WeatherApiService;
import es.aplicacionesdevanguardia.weather.model.WeatherData;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {

    private EditText cityEditText;
    private Button fetchButton;
    private TextView resultTextView; // Para mostrar resultados simples, luego usaremos RecyclerView


    private static final String BASE_URL = "http://villaema.es/api/api-weather-reverse.php";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); // Asegúrate de que tu layout tenga estos elementos

        cityEditText = findViewById(R.id.cityEditText);
        fetchButton = findViewById(R.id.fetchButton);
        resultTextView = findViewById(R.id.resultTextView);

        fetchButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String city = cityEditText.getText().toString().trim();
                if (!city.isEmpty()) {
                    fetchWeatherData(city);
                } else {
                    Toast.makeText(MainActivity.this, "Por favor, introduce una ciudad", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    private void fetchWeatherData(String city) {
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        WeatherApiService service = retrofit.create(WeatherApiService.class);
        Call<List<WeatherData>> call = service.getWeatherByCity(city);

        call.enqueue(new Callback<List<WeatherData>>() {
            @Override
            public void onResponse(Call<List<WeatherData>> call, Response<List<WeatherData>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<WeatherData> weatherDataList = response.body();
                    if (!weatherDataList.isEmpty()) {
                        // Para empezar, solo mostramos el primer día
                        WeatherData firstDayData = weatherDataList.get(0);
                        String displayText = "Datos para " + city + ":\n" +
                                "Día: " + firstDayData.getDia() + "\n" +
                                "Temp Máx: " + firstDayData.getTempMax() + "\n" +
                                "Temp Mín: " + firstDayData.getTempMin() + "\n" +
                                "Humedad: " + firstDayData.getHumedad();
                        resultTextView.setText(displayText);
                    } else {
                        resultTextView.setText("No hay datos para la ciudad especificada.");
                    }
                } else {
                    // Manejar errores de API (ej. 404, 500, etc.)
                    try {
                        String errorBody = response.errorBody().string();
                        resultTextView.setText("Error en la API: " + errorBody);
                    } catch (Exception e) {
                        resultTextView.setText("Error en la API: " + response.code());
                        e.printStackTrace();
                    }
                }
            }

            @Override
            public void onFailure(Call<List<WeatherData>> call, Throwable t) {
                // Manejar errores de red (ej. no hay internet, servidor no responde)
                resultTextView.setText("Error de red: " + t.getMessage());
                t.printStackTrace();
            }
        });
    }
}
