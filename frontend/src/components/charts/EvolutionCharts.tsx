import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  CHART_COLORS,
  formatPosition,
  hasAnyValue,
} from "./chartUtils";

import "./Charts.css";

import type { EvolutionMetric, PositionTotal } from "../../types";

type Props = {
  metrics: EvolutionMetric[];
  positionTotals: PositionTotal[];
};

export default function EvolutionCharts({
  metrics,
  positionTotals,
}: Props) {
  const hasControlData = hasAnyValue(metrics, [
    "dominantTime",
    "defensiveTime",
  ]);

  const hasPctData = hasAnyValue(metrics, [
    "dominantPct",
    "defensivePct",
  ]);

  const actionData = metrics.map((item) => ({
    label: item.label,
    Finalitzacions: item.submissionAttempts,
    Enderrocs: item.takedownAttempts,
    "Guard pulls": item.guardPulls,
    Reversions: item.reversals,
    Escapades: item.escapes,
  }));

  const hasActionData = hasAnyValue(actionData, [
    "Finalitzacions",
    "Enderrocs",
    "Guard pulls",
    "Reversions",
    "Escapades",
  ]);

  const formattedPositions = positionTotals.map((item) => ({
    ...item,
    name: formatPosition(item.name),
  }));

  return (
    <div className="stats-charts">
      {hasControlData && (
        <div className="stats-chart-card stats-chart-card-large">
          <div className="stats-chart-header">
            <h4>Evolució del control</h4>
            <span>
              Temps dominant i defensiu per combat
            </span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics}>
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 10 }}
                />

                <YAxis
                  tickFormatter={(value) => `${value}s`}
                />

                <Tooltip />
                <Legend />

                <Line
                  type="linear"
                  dataKey="dominantTime"
                  name="Temps dominant"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />

                <Line
                  type="linear"
                  dataKey="defensiveTime"
                  name="Temps defensiu"
                  stroke="#dc2626"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {hasPctData && (
        <div className="stats-chart-card stats-chart-card-large">
          <div className="stats-chart-header">
            <h4>Evolució percentual del control</h4>

            <span>
              Percentatge de domini i defensa sobre el
              temps total
            </span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics}>
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 10 }}
                />

                <YAxis
                  tickFormatter={(value) => `${value}%`}
                />

                <Tooltip
                  formatter={(value: any) => [
                    `${value}%`,
                    "",
                  ]}
                />

                <Legend />

                <Line
                  type="linear"
                  dataKey="dominantPct"
                  name="% domini"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />

                <Line
                  type="linear"
                  dataKey="defensivePct"
                  name="% defensa"
                  stroke="#dc2626"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {hasActionData && (
        <div className="stats-chart-card stats-chart-card-large">
          <div className="stats-chart-header">
            <h4>Accions clau per combat</h4>

            <span>
              Comparativa d’accions ofensives i
              defensives
            </span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={actionData}>
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 10 }}
                />

                <YAxis allowDecimals={false} />

                <Tooltip />
                <Legend />

                <Bar
                  dataKey="Finalitzacions"
                  fill="#2563eb"
                  radius={[6, 6, 0, 0]}
                />

                <Bar
                  dataKey="Enderrocs"
                  fill="#7c3aed"
                  radius={[6, 6, 0, 0]}
                />

                <Bar
                  dataKey="Guard pulls"
                  fill="#0891b2"
                  radius={[6, 6, 0, 0]}
                />

                <Bar
                  dataKey="Reversions"
                  fill="#059669"
                  radius={[6, 6, 0, 0]}
                />

                <Bar
                  dataKey="Escapades"
                  fill="#ea580c"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {formattedPositions.length > 0 && (
        <div className="stats-chart-card stats-chart-card-large">
          <div className="stats-chart-header">
            <h4>Posicions acumulades</h4>

            <span>
              Temps total per posició en tots els combats
            </span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={360}>
              <PieChart>
                <Pie
                  data={formattedPositions}
                  dataKey="segons"
                  nameKey="name"
                  innerRadius={72}
                  outerRadius={112}
                  paddingAngle={3}
                >
                  {formattedPositions.map((_, index) => (
                    <Cell
                      key={index}
                      fill={
                        CHART_COLORS[index % CHART_COLORS.length]
                      }
                    />
                  ))}
                </Pie>

                <Tooltip
                  formatter={(value: any, name: any) => [
                    `${Number(value).toFixed(1)}s`,
                    name,
                  ]}
                />

                <Legend
                  layout="vertical"
                  align="right"
                  verticalAlign="middle"
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}