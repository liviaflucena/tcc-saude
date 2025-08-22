import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import api from "../services/api";

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const MESES = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

export default function SeriesChart({ year = 2025, uf = "PB" }) {
  const [dataSet, setDataSet] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/series?year=${year}&uf=${uf}`)
      .then((res) => {
        const arr = Array.isArray(res.data?.data) ? res.data.data : res.data;
        const byMes = new Array(12).fill(0);
        arr.forEach(({ mes, casos }) => {
          if (mes >= 1 && mes <= 12) byMes[mes - 1] = Number(casos || 0);
        });
        setDataSet({
          labels: MESES,
          datasets: [
            {
              label: `Casos mensais — ${uf}/${year}`,
              data: byMes,
            },
          ],
        });
      })
      .finally(() => setLoading(false));
  }, [year, uf]);

  if (loading) return <p>Carregando série mensal...</p>;
  if (!dataSet) return <p>Sem dados.</p>;

  return (
    <div style={{ background: "#fff", padding: 16, borderRadius: 12, boxShadow: "0 2px 16px rgba(0,0,0,0.06)" }}>
      <h3 style={{ margin: "0 0 12px" }}>Série mensal — {uf} / {year}</h3>
      <Line data={dataSet} />
    </div>
  );
}
