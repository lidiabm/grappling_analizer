
import {
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "./StatsCharts.css";

type ChartDatum = {
  label: string;
  valor: number | string;
};

type ScoutingChart = {
  id: string;
  tipus: "barres" | "radar" | string;
  titol: string;
  descripcio?: string;
  dades: ChartDatum[];
  escala?: string;
  interpretacio?: string;
};

type Props = {
  grafics?: ScoutingChart[];
};

function normalizeNumber(value: number | string) {
  if (typeof value === "number") return value;

  const parsed = Number(
    String(value).replace(",", ".").replace(/[^\d.-]/g, "")
  );

  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeChartData(dades?: ChartDatum[]) {
  return (
    dades
      ?.map((item) => ({
        name: item.label,
        valor: normalizeNumber(item.valor),
      }))
      .filter((item) => item.valor > 0) ?? []
  );
}

export default function ScoutingCharts({ grafics }: Props) {
  if (!grafics || grafics.length === 0) return null;

  return (
    <div className="stats-charts">
      {grafics.map((grafic) => {
        const data = normalizeChartData(grafic.dades);

        if (data.length === 0) return null;

        if (grafic.tipus === "radar") {
          return (
            <div key={grafic.id} className="stats-chart-card stats-chart-card-large">
              <div className="stats-chart-header">
                <h4>{grafic.titol}</h4>
                <span>{grafic.descripcio}</span>
              </div>

              <div className="stats-chart">
                <ResponsiveContainer width="100%" height={340}>
                  <RadarChart data={data}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 10]} />
                    <Tooltip />
                    <Radar
                      name="Valor"
                      dataKey="valor"
                      stroke="#2563eb"
                      fill="#2563eb"
                      fillOpacity={0.28}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              {grafic.interpretacio && <p>{grafic.interpretacio}</p>}
            </div>
          );
        }

        return (
          <div key={grafic.id} className="stats-chart-card stats-chart-card-large">
            <div className="stats-chart-header">
              <h4>{grafic.titol}</h4>
              <span>{grafic.descripcio}</span>
            </div>

            <div className="stats-chart">
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar
                    dataKey="valor"
                    name="Valor"
                    fill="#2563eb"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {grafic.interpretacio && <p>{grafic.interpretacio}</p>}
          </div>
        );
      })}
    </div>
  );
}