package es.aplicacionesdevanguardia.weather;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;

public class GraficosActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_graficos); // Usa tu layout con GraphView

        GraphView graph = findViewById(R.id.grafico);
        LineGraphSeries<DataPoint> series = new LineGraphSeries<>(new DataPoint[] {
                new DataPoint(0, 5),  // Día 1: valor 5
                new DataPoint(1, 8),  // Día 2: valor 8
                new DataPoint(2, 3),  // Día 3: valor 3
                new DataPoint(3, 7)   // Día 4: valor 7
        });

        graph.addSeries(series);
    }
}
