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
import type { ScoutingChart, ScoutingChartDatum } from "../../types";
import { CHART_COLORS, normalizeNumber } from "./chartUtils";
import "./Charts.css";

type Props = {
  grafics?: ScoutingChart[] | null;
};

function normalizeChartData(dades?: ScoutingChartDatum[]) {
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

  const mainColor = CHART_COLORS[0];

  return (
    <div className="stats-charts">
      {grafics.map((grafic) => {
        const data = normalizeChartData(grafic.dades);

        if (data.length === 0) return null;

        if (grafic.tipus === "radar") {
          return (
            <div
              key={grafic.id}
              className="stats-chart-card stats-chart-card-large"
            >
              <div className="stats-chart-header">
                <h4>{grafic.titol}</h4>
                {grafic.descripcio && <span>{grafic.descripcio}</span>}
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
                      stroke={mainColor}
                      fill={mainColor}
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
          <div
            key={grafic.id}
            className="stats-chart-card stats-chart-card-large"
          >
            <div className="stats-chart-header">
              <h4>{grafic.titol}</h4>
              {grafic.descripcio && <span>{grafic.descripcio}</span>}
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
                    fill={mainColor}
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