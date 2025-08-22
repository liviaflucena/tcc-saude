import { useState } from "react";
import ChartIncidence from "./components/ChartIncidence";
import SeriesChart from "./components/SeriesChart";
import MapUFChoropleth from "./components/MapUFChoropleth";

export default function App() {
  const [year, setYear] = useState(2025);
  const [uf, setUf] = useState("PB");

  return (
    <div style={{ fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif", background: "#f6f7fb", minHeight: "100vh" }}>
      <header style={{ padding: "16px 24px", background: "#101828", color: "#fff", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h2 style={{ margin: 0 }}>TCC Saúde • Dashboard</h2>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <label>Ano:&nbsp;</label>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            style={{ width: 100, padding: 6, borderRadius: 8, border: "1px solid #ccc" }}
          />
          <label>UF:&nbsp;</label>
          <input
            type="text"
            value={uf}
            onChange={(e) => setUf(e.target.value.toUpperCase())}
            style={{ width: 60, padding: 6, borderRadius: 8, border: "1px solid #ccc", textTransform: "uppercase" }}
            maxLength={2}
          />
        </div>
      </header>

      <main style={{ padding: 24, display: "grid", gap: 24, gridTemplateColumns: "1fr", maxWidth: 1200, margin: "0 auto" }}>
       <MapUFChoropleth year={year} />
  <ChartIncidence year={year} />
  <SeriesChart year={year} uf={uf} />
      </main>
    </div>
  );
}
