import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import "./StatsCharts.css";

type Props = {
  stats?: any;
};

const POSITION_COLORS = [
  "#2563eb",
  "#7c3aed",
  "#0891b2",
  "#059669",
  "#ca8a04",
  "#ea580c",
  "#dc2626",
  "#9333ea",
  "#0f766e",
];

const FIGHTER_COLORS: Record<string, string> = {
  oponent_1: "#2563eb",
  oponent_2: "#dc2626",
};

const DEFENSE_COLORS: Record<string, string> = {
  oponent_1: "#38bdf8",
  oponent_2: "#fb7185",
};

function formatPosition(posicio?: string) {
  if (!posicio) return "Desconeguda";

  const labels: Record<string, string> = {
    standing: "Standing",
    scramble: "Scramble",
    side_control: "Side control",
    side_control_top: "Side control top",
    side_control_bottom: "Side control bottom",
    back_control: "Back control",
    back_control_top: "Back control top",
    back_control_bottom: "Back control bottom",
    mount: "Mount",
    mount_top: "Mount top",
    mount_bottom: "Mount bottom",
    closed_guard: "Closed guard",
    closed_guard_top: "Closed guard top",
    closed_guard_bottom: "Closed guard bottom",
    open_guard: "Open guard",
    open_guard_top: "Open guard top",
    open_guard_bottom: "Open guard bottom",
    half_guard: "Half guard",
    half_guard_top: "Half guard top",
    half_guard_bottom: "Half guard bottom",
    turtle: "Turtle",
    turtle_top: "Turtle top",
    turtle_bottom: "Turtle bottom",
    other: "Altres",
  };

  return labels[posicio] ?? posicio.replaceAll("_", " ");
}

function normalizeNumber(value: any) {
  if (typeof value === "number") return value;

  if (typeof value === "string") {
    const cleaned = value.replace(",", ".").replace(/[^\d.-]/g, "");
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  return 0;
}

function getByFighterOrGlobal(value: any, fighter: string) {
  if (value && typeof value === "object") {
    return normalizeNumber(value[fighter]);
  }

  return fighter === "oponent_1" ? normalizeNumber(value) : 0;
}

function sumTempsPerLluitador(stats: any, fighter: string, dominant: boolean) {
  return (
    stats.temps_per_posicio
      ?.filter(
        (item: any) =>
          item.lluitador === fighter && Boolean(item.dominant) === dominant
      )
      ?.reduce(
        (total: number, item: any) => total + normalizeNumber(item.segons),
        0
      ) ?? 0
  );
}

function hasAnyValue(data: any[], keys: string[]) {
  return data.some((item) =>
    keys.some((key) => normalizeNumber(item[key]) > 0)
  );
}

export default function StatsCharts({ stats }: Props) {
  if (!stats) return null;

  const positionData =
    stats.temps_per_posicio
      ?.map((item: any) => ({
        name: formatPosition(item.posicio),
        segons: normalizeNumber(item.segons),
        percentatge: normalizeNumber(item.percentatge),
      }))
      .filter((item: any) => item.segons > 0) ?? [];

  const controlData = ["oponent_1", "oponent_2"].map((fighter) => {
    const dominantDirect = getByFighterOrGlobal(
      stats.temps_dominant_total,
      fighter
    );

    const defensiuDirect = getByFighterOrGlobal(
      stats.temps_defensiu_total,
      fighter
    );

    return {
      name: fighter,
      dominant:
        dominantDirect > 0
          ? dominantDirect
          : sumTempsPerLluitador(stats, fighter, true),
      defensiu:
        defensiuDirect > 0
          ? defensiuDirect
          : sumTempsPerLluitador(stats, fighter, false),
    };
  });

  const actionData = [
    {
      name: "Finalitzacions",
      oponent_1: getByFighterOrGlobal(stats.intents_finalitzacio, "oponent_1"),
      oponent_2: getByFighterOrGlobal(stats.intents_finalitzacio, "oponent_2"),
    },
    {
      name: "Enderrocs",
      oponent_1: getByFighterOrGlobal(stats.intents_enderroc, "oponent_1"),
      oponent_2: getByFighterOrGlobal(stats.intents_enderroc, "oponent_2"),
    },
    {
      name: "Guard pulls",
      oponent_1: getByFighterOrGlobal(stats.guard_pulls, "oponent_1"),
      oponent_2: getByFighterOrGlobal(stats.guard_pulls, "oponent_2"),
    },
    {
      name: "Reversions",
      oponent_1: getByFighterOrGlobal(stats.reversions, "oponent_1"),
      oponent_2: getByFighterOrGlobal(stats.reversions, "oponent_2"),
    },
    {
      name: "Escapades",
      oponent_1: getByFighterOrGlobal(stats.escapades, "oponent_1"),
      oponent_2: getByFighterOrGlobal(stats.escapades, "oponent_2"),
    },
  ].filter((item) => item.oponent_1 > 0 || item.oponent_2 > 0);

  const hasDominantData = hasAnyValue(controlData, ["dominant"]);
  const hasDefensiveData = hasAnyValue(controlData, ["defensiu"]);
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
                      fill={POSITION_COLORS[index % POSITION_COLORS.length]}
                    />
                  ))}
                </Pie>

                <Tooltip
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
        <div className="stats-chart-card">
          <div className="stats-chart-header">
            <h4>Domini</h4>
            <span>Temps dominant per lluitador</span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={controlData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(value) => `${value}s`} />
                <Tooltip
                  formatter={(value: any) => [`${value}s`, "Temps dominant"]}
                />

                <Bar
                  dataKey="dominant"
                  name="Temps dominant"
                  radius={[10, 10, 0, 0]}
                >
                  {controlData.map((item) => (
                    <Cell
                      key={item.name}
                      fill={FIGHTER_COLORS[item.name] ?? "#64748b"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {hasDefensiveData && (
        <div className="stats-chart-card">
          <div className="stats-chart-header">
            <h4>Defensa</h4>
            <span>Temps defensiu per lluitador</span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={controlData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(value) => `${value}s`} />
                <Tooltip
                  formatter={(value: any) => [`${value}s`, "Temps defensiu"]}
                />

                <Bar
                  dataKey="defensiu"
                  name="Temps defensiu"
                  radius={[10, 10, 0, 0]}
                >
                  {controlData.map((item) => (
                    <Cell
                      key={item.name}
                      fill={DEFENSE_COLORS[item.name] ?? "#94a3b8"}
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
            <span>Intents totals observables durant el combat</span>
          </div>

          <div className="stats-chart">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={actionData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
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