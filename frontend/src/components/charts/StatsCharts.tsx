import {
  Bar,
  BarChart,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  CHART_COLORS,
  FIGHTER_COLORS,
  formatPosition,
  hasAnyValue,
  normalizeNumber,
} from "./chartUtils";

import "./Charts.css";

type Props = {
  stats?: any;
};

function getCounterValue(counter: any, fighter: "oponent_1" | "oponent_2") {
  if (!counter || typeof counter !== "object") return 0;
  return normalizeNumber(counter[fighter]);
}

function getAttemptValue(counter: any, fighter: "oponent_1" | "oponent_2", key: "intents" | "reeixits") {
  if (!counter || typeof counter !== "object") return 0;
  const val = counter[fighter];
  if (typeof val === "object" && val !== null) return normalizeNumber(val[key]);
  return key === "intents" ? normalizeNumber(val) : 0;
}

function DomainTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;

  const item = payload[0];
  const color = item?.payload?.color ?? "#f5f7fa";

  return (
    <div
      style={{
        backgroundColor: "#111318",
        border: "1px solid rgba(201, 168, 106, 0.22)",
        borderRadius: "12px",
        padding: "12px 14px",
      }}
    >
      <div
        style={{
          color,
          fontWeight: 700,
          marginBottom: "6px",
        }}
      >
        {item.payload.name}
      </div>

      <div
        style={{
          color,
          fontWeight: 600,
        }}
      >
        Temps dominant : {item.value}s
      </div>
    </div>
  );
}

export default function StatsCharts({ stats }: Props) {
  if (!stats) return null;

  const resumAccions = stats.resum_accions ?? {};

  const positionData =
    stats.temps_per_posicio
      ?.map((item: any) => ({
        name: formatPosition(item.posicio),
        segons: normalizeNumber(item.segons),
        percentatge: normalizeNumber(item.percentatge),
      }))
      .filter((item: any) => item.segons > 0) ?? [];

  const controlData = ["oponent_1", "oponent_2"].map((fighter) => ({
    name: fighter,
    color: FIGHTER_COLORS[fighter] ?? "#64748b",
    dominant: getCounterValue(stats.temps_dominant_total, fighter as any),
  }));

  const actionData = [
    {
      name: "Finalitz. (intents)",
      oponent_1: getAttemptValue(
        resumAccions.intents_finalitzacio, 
        "oponent_1", 
        "intents"),
      oponent_2: getAttemptValue(
        resumAccions.intents_finalitzacio, 
        "oponent_2", 
        "intents"),
    },
    {
      name: "Finalitz. (reeixits)",
      oponent_1: getAttemptValue(
        resumAccions.intents_finalitzacio,
        "oponent_1", 
        "reeixits"),
      oponent_2: getAttemptValue(
        resumAccions.intents_finalitzacio, 
        "oponent_2", 
        "reeixits"),
    },
    {
      name: "Enderrocs (intents)",
      oponent_1: getAttemptValue(resumAccions.intents_enderroc, 
        "oponent_1", 
        "intents"),
      oponent_2: getAttemptValue(resumAccions.intents_enderroc, 
        "oponent_2", 
        "intents"),
    },
    {
      name: "Enderrocs (reeixits)",
      oponent_1: getAttemptValue(resumAccions.intents_enderroc, 
        "oponent_1", 
        "reeixits"),
      oponent_2: getAttemptValue(resumAccions.intents_enderroc, 
        "oponent_2", 
        "reeixits"),
    },
    {
      name: "Guard pulls",
      oponent_1: getCounterValue(resumAccions.guard_pulls, "oponent_1"),
      oponent_2: getCounterValue(resumAccions.guard_pulls, "oponent_2"),
    },
    {
      name: "Reversions",
      oponent_1: getCounterValue(resumAccions.reversions, "oponent_1"),
      oponent_2: getCounterValue(resumAccions.reversions, "oponent_2"),
    },
    {
      name: "Escapades",
      oponent_1: getCounterValue(resumAccions.escapades, "oponent_1"),
      oponent_2: getCounterValue(resumAccions.escapades, "oponent_2"),
    },
  ].filter((item) => item.oponent_1 > 0 || item.oponent_2 > 0);

  const hasDominantData = hasAnyValue(controlData, ["dominant"]);
  const hasActionData = actionData.length > 0;

  return (
    <div className="stats-charts">
      {positionData.length > 0 && (
        <div className="stats-chart-card stats-chart-card-large">
          <div className="stats-chart-header">
            <h4>Distribució del combat per posició</h4>
            <span>Segons totals i percentatge del combat</span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={340}>
              <PieChart>
                <Pie
                  data={positionData}
                  dataKey="segons"
                  nameKey="name"
                  innerRadius={72}
                  outerRadius={112}
                  paddingAngle={3}
                >
                  {positionData.map((_: any, index: number) => (
                    <Cell
                      key={index}
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Pie>

                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111318",
                    border: "1px solid rgba(201, 168, 106, 0.22)",
                    borderRadius: "12px",
                  }}
                  formatter={(value: any, _name: any, item: any) => [
                    `${value}s (${item?.payload?.percentatge ?? 0}%)`,
                    item?.payload?.name,
                  ]}
                />

                <Legend
                  formatter={(value: any) => {
                    const item = positionData.find(
                      (p: any) => p.name === value
                    );

                    return `${value} · ${item?.percentatge ?? 0}%`;
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {hasDominantData && (
        <div className="stats-chart-card stats-chart-card-centered">
          <div className="stats-chart-header">
            <h4>Domini</h4>
            <span>Temps dominant per lluitador</span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={controlData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(value) => `${value}s`} />

                <Tooltip content={<DomainTooltip />} />

                <Bar
                  dataKey="dominant"
                  radius={[10, 10, 0, 0]}
                >
                  {controlData.map((item) => (
                    <Cell
                      key={item.name}
                      fill={item.color}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {hasActionData && (
        <div className="stats-chart-card stats-chart-card-large">
          <div className="stats-chart-header">
            <h4>Accions clau</h4>
          <span>Intents i accions reeixides observables durant el combat</span>  
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={actionData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />

                <Tooltip
                  contentStyle={{
                    backgroundColor: "#111318",
                    border: "1px solid rgba(201, 168, 106, 0.22)",
                    borderRadius: "12px",
                  }}
                />

                <Legend />

                <Bar
                  dataKey="oponent_1"
                  name="Oponent 1"
                  fill={FIGHTER_COLORS.oponent_1}
                  radius={[8, 8, 0, 0]}
                />

                <Bar
                  dataKey="oponent_2"
                  name="Oponent 2"
                  fill={FIGHTER_COLORS.oponent_2}
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}