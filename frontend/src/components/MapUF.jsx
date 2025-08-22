import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

/**
 * Centros aproximados por UF (lat, lng).
 * Para um choropleth exato, depois trocamos por GeoJSON oficial.
 */
const UF_CENTER = {
  AC: [-9.02, -70.81],  AL: [-9.66, -36.70],  AM: [-3.07, -61.66],  AP: [1.41, -51.77],
  BA: [-12.97, -41.54], CE: [-5.20, -39.53],  DF: [-15.83, -47.86], ES: [-19.19, -40.34],
  GO: [-15.93, -50.14], MA: [-4.96, -45.27],  MG: [-18.10, -44.38], MS: [-20.51, -54.54],
  MT: [-12.64, -55.42], PA: [-3.97, -52.25],  PB: [-7.12, -36.72],  PE: [-8.38, -37.86],
  PI: [-7.60, -43.03],  PR: [-24.89, -51.55], RJ: [-22.17, -42.66], RN: [-5.79, -36.58],
  RO: [-10.83, -63.34], RR: [2.82, -60.67],   RS: [-29.84, -53.49], SC: [-27.33, -50.46],
  SE: [-10.57, -37.45], SP: [-22.19, -48.78], TO: [-10.25, -48.29]
};

// escala simples (0 → claro, max → forte)
function colorScale(v, min, max) {
  if (max <= min) return "#fee5d9";
  const t = Math.max(0, Math.min(1, (v - min) / (max - min)));
  // Interpola entre #fee5d9 (claro) e #a50f15 (escuro)
  const from = [254, 229, 217];
  const to   = [165,  15,  21];
  const c = from.map((f, i) => Math.round(f + (to[i] - f) * t));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

export default function MapUF({ year = 2025 }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.get(`/incidence?year=${year}&agg=uf`).then((res) => {
      const arr = Array.isArray(res.data?.data) ? res.data.data : res.data;
      setData(arr || []);
    }).finally(() => setLoading(false));
  }, [year]);

  const stats = useMemo(() => {
    const vals = data.map((d) => Number(d.incidencia || 0)).filter(Number.isFinite);
    const min = Math.min(...(vals.length ? vals : [0]));
    const max = Math.max(...(vals.length ? vals : [0]));
    return { min, max };
  }, [data]);

  if (loading) return <p>Carregando mapa...</p>;

  return (
    <div style={{ background: "#fff", padding: 16, borderRadius: 12, boxShadow: "0 2px 16px rgba(0,0,0,0.06)" }}>
      <h3 style={{ margin: "0 0 12px" }}>Mapa por UF — {year}</h3>
      <MapContainer center={[-14.235, -51.9253]} zoom={4} style={{ height: 520, width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {data.map(({ uf, incidencia = 0, casos = 0 }, idx) => {
          const center = UF_CENTER[uf];
          if (!center) return null;
          const color = colorScale(Number(incidencia), stats.min, stats.max);
          const radius = 6 + Math.min(18, Math.sqrt(Number(casos)) / 5); // raio cresce com casos
          return (
            <CircleMarker key={idx} center={center} radius={radius} pathOptions={{ color, fillColor: color, fillOpacity: 0.85 }}>
              <Tooltip direction="top" offset={[0, -4]} opacity={1}>
                <div style={{ fontSize: 12 }}>
                  <strong>{uf}</strong><br />
                  Incidência: {Number(incidencia).toFixed(2)} / 100k<br />
                  Casos: {Number(casos)}
                </div>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>
      <div style={{ marginTop: 8, fontSize: 12, color: "#444" }}>
        <em>Quem tiver mais acende mais forte</em> — escala relativa ao intervalo ({stats.min.toFixed(2)} a {stats.max.toFixed(2)}).
      </div>
    </div>
  );
}
