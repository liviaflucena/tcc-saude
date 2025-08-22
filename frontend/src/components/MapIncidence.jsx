import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { useEffect, useState } from "react";
import api from "../services/api";

function MapIncidence() {
  const [data, setData] = useState([]);

  useEffect(() => {
    api.get("/incidence?year=2025&agg=uf").then((res) => {
      setData(res.data);
    });
  }, []);

  return (
    <MapContainer center={[-15.7797, -47.9297]} zoom={4} style={{ height: "500px", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {data.map((item, idx) => (
        <Marker key={idx} position={[-10 + Math.random() * 20, -50 + Math.random() * 20]}>
          <Popup>
            {item.uf}: {item.incidencia.toFixed(2)} casos/100k
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default MapIncidence;
