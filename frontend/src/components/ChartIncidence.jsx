import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../services/api";

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

export default function ChartIncidence({ year = 2025 }) {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/incidence?year=${year}&agg=uf`)
      .then((res) => {
        const arr = Array.isArray(res.data?.data) ? res.data.data : res.data; // suporta ambos formatos
        const labels = arr.map((it) => it.uf);
        const values = arr.map((it) => Number(it.incidencia || 0));
        setChartData({
          labels,
          datasets: [
            {
              label: "Incidência por 100k hab.",
              data: values,
            },
          ],
        });
      })
      .finally(() => setLoading(false));
  }, [year]);

  if (loading) return <p>Carregando incidência...</p>;
  if (!chartData) return <p>Sem dados.</p>;

  return (
    <div style={{ background: "#fff", padding: 16, borderRadius: 12, boxShadow: "0 2px 16px rgba(0,0,0,0.06)" }}>
      <h3 style={{ margin: "0 0 12px" }}>Incidência por UF — {year}</h3>
      <Bar data={chartData} />
    </div>
  );
}
