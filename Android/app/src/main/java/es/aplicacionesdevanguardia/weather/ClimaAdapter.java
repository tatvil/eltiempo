package es.aplicacionesdevanguardia.weather;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class ClimaAdapter extends RecyclerView.Adapter<ClimaAdapter.ClimaViewHolder> {

    private List<Clima> climaList;

    public ClimaAdapter(List<Clima> climaList) {
        this.climaList = climaList;
    }

    @Override
    public ClimaViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View itemView = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_clima, parent, false);
        return new ClimaViewHolder(itemView);
    }

    @Override
    public void onBindViewHolder(ClimaViewHolder holder, int position) {
        Clima clima = climaList.get(position);
        holder.fecha.setText(clima.getFecha());
        holder.amanecer.setText("Amanecer: " + clima.getAmanecer());
        holder.anochecer.setText("Anochecer: " + clima.getAnochecer());
        holder.tempMax.setText("Temp Max: " + clima.getTempMax() + "°C");
        holder.tempMin.setText("Temp Min: " + clima.getTempMin() + "°C");
    }

    @Override
    public int getItemCount() {
        return climaList.size();
    }

    public class ClimaViewHolder extends RecyclerView.ViewHolder {
        TextView fecha, amanecer, anochecer, tempMax, tempMin;

        public ClimaViewHolder(View itemView) {
            super(itemView);
            fecha = itemView.findViewById(R.id.fecha);
            amanecer = itemView.findViewById(R.id.amanecer);
            anochecer = itemView.findViewById(R.id.anochecer);
            tempMax = itemView.findViewById(R.id.tempMax);
            tempMin = itemView.findViewById(R.id.tempMin);
        }
    }
}

