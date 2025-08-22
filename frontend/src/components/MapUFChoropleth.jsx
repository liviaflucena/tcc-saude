import { MapContainer, TileLayer, GeoJSON, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import api from "../services/api";

// Escala de cor
function colorScale(v, min, max) {
  if (max <= min) return "#fee5d9";
  const t = Math.max(0, Math.min(1, (v - min) / (max - min)));
  const from = [254, 229, 217];
  const to   = [165,  15,  21];
  const c = from.map((f, i) => Math.round(f + (to[i] - f) * t));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

export default function MapUFChoropleth({ year = 2025 }) {
  const [data, setData] = useState([]);
  const [geo, setGeo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // dados de incidência
    api.get(`/incidence?year=${year}&agg=uf`).then((res) => {
      const arr = Array.isArray(res.data?.data) ? res.data.data : res.data;
      setData(arr || []);
    });
    // geojson
    fetch("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson")
      .then((r) => r.json())
      .then(setGeo);
  }, [year]);

  if (!geo || !data.length) return <p>Carregando mapa...</p>;

  const vals = data.map((d) => Number(d.incidencia || 0)).filter(Number.isFinite);
  const min = Math.min(...(vals.length ? vals : [0]));
  const max = Math.max(...(vals.length ? vals : [0]));

  const incidenceByUF = {};
  data.forEach((d) => {
    incidenceByUF[d.uf] = {
      incidencia: Number(d.incidencia || 0),
      casos: Number(d.casos || 0),
    };
  });

  function style(feature) {
    const uf = feature.properties.sigla || feature.properties.code;
    const v = incidenceByUF[uf]?.incidencia || 0;
    return {
      fillColor: colorScale(v, min, max),
      weight: 1,
      opacity: 1,
      color: "white",
      fillOpacity: 0.8,
    };
  }

  function onEachFeature(feature, layer) {
    const uf = feature.properties.sigla || feature.properties.code;
    const stats = incidenceByUF[uf];
    if (stats) {
      layer.bindTooltip(
        `<b>${uf}</b><br/>Incidência: ${stats.incidencia.toFixed(2)}<br/>Casos: ${stats.casos}`,
        { sticky: true }
      );
    }
  }

  return (
    <div style={{ background: "#fff", padding: 16, borderRadius: 12, boxShadow: "0 2px 16px rgba(0,0,0,0.06)" }}>
      <h3 style={{ margin: "0 0 12px" }}>Mapa (choropleth) — {year}</h3>
      <MapContainer center={[-14.235, -51.9253]} zoom={4} style={{ height: 520, width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON data={geo} style={style} onEachFeature={onEachFeature} />
      </MapContainer>
      <div style={{ marginTop: 8, fontSize: 12, color: "#444" }}>
        <em>Quem tiver mais acende mais forte</em> — escala relativa ({min.toFixed(2)} a {max.toFixed(2)}).
      </div>
    </div>
  );
}
