export const CHART_COLORS = [
  "#2563eb",
  "#7c3aed",
  "#0891b2",
  "#059669",
  "#ca8a04",
  "#ea580c",
  "#dc2626",
  "#9333ea",
  "#0d9488",
  "#65a30d",
  "#db2777",
  "#475569",
  "#b45309",
  "#1d4ed8",
  "#be123c",
];

export const FIGHTER_COLORS: Record<string, string> = {
  oponent_1: "#2563eb",
  oponent_2: "#dc2626",
};

export const DEFENSE_COLORS: Record<string, string> = {
  oponent_1: "#38bdf8",
  oponent_2: "#fb7185",
};

export function normalizeNumber(value: unknown) {
  if (typeof value === "number") return value;

  if (typeof value === "string") {
    const cleaned = value.replace(",", ".").replace(/[^\d.-]/g, "");
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  return 0;
}

export function hasAnyValue<T extends Record<string, unknown>>(
  data: T[],
  keys: string[]
) {
  return data.some((item) =>
    keys.some((key) => normalizeNumber(item[key]) > 0)
  );
}

export function formatPosition(posicio?: string) {
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