import "./LluitadorEvolutionScreen.css";
import type { SavedAnalysis } from "../types";
import EvolutionSummary from "../components/EvolutionSummary";
import EvolutionCharts from "../components/EvolutionCharts";
import EvolutionPatterns from "../components/EvolutionPatterns";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";
import { getSavedAnalyses } from "../storage/analysisStorage";

type Props = {
  onBack: () => void;
};

export type EvolutionMetric = {
  fightId: string;
  label: string;
  dominantTime: number;
  defensiveTime: number;
  neutralTime: number;
  submissionAttempts: number;
  takedownAttempts: number;
  guardPulls: number;
  reversals: number;
  escapes: number;
};

function normalizeNumber(value: any) {
  if (typeof value === "number") return value;

  if (typeof value === "string") {
    const cleaned = value.replace(",", ".").replace(/[^\d.-]/g, "");
    const parsed = Number(cleaned);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  return 0;
}

function getAnalysisData(analysis: any) {
  return analysis.result ?? analysis.data ?? analysis;
}

function getOwnValue(value: any, selectedOponentId: string) {
  if (value && typeof value === "object") {
    return normalizeNumber(value[selectedOponentId]);
  }

  return normalizeNumber(value);
}

function getAnalysisLabel(analysis: SavedAnalysis, index: number) {
  const data = getAnalysisData(analysis);

  const date = analysis.createdAt ?? "";
  const shortDate = date ? String(date).slice(0, 10) : `Combat ${index + 1}`;

  const opponent =
    data.combat_info?.oponents?.find(
      (o: any) => o.id !== data.selected_oponent_id
    )?.nom_visible ?? "";

  return opponent && opponent !== "desconegut"
    ? `${shortDate} · ${opponent}`
    : shortDate;
}

function buildMetrics(analyses: SavedAnalysis[]): EvolutionMetric[] {
  return analyses.map((analysis, index) => {
    const data = getAnalysisData(analysis);
    const stats = data.estadistiques_estimades ?? {};
    const selectedOponentId = data.selected_oponent_id ?? "oponent_1";

    return {
      fightId: analysis.fightId ?? analysis.id ?? String(index),
      label: getAnalysisLabel(analysis, index),
      dominantTime: getOwnValue(stats.temps_dominant_total, selectedOponentId),
      defensiveTime: getOwnValue(stats.temps_defensiu_total, selectedOponentId),
      neutralTime: normalizeNumber(stats.temps_neutral_total),
      submissionAttempts: getOwnValue(
        stats.intents_finalitzacio,
        selectedOponentId
      ),
      takedownAttempts: getOwnValue(stats.intents_enderroc, selectedOponentId),
      guardPulls: getOwnValue(stats.guard_pulls, selectedOponentId),
      reversals: getOwnValue(stats.reversions, selectedOponentId),
      escapes: getOwnValue(stats.escapades, selectedOponentId),
    };
  });
}

function buildPositionTotals(analyses: SavedAnalysis[]) {
  const totals: Record<string, number> = {};

  analyses.forEach((analysis) => {
    const data = getAnalysisData(analysis);
    const positions = data.estadistiques_estimades?.temps_per_posicio ?? [];

    positions.forEach((item: any) => {
      const posicio = item.posicio ?? "other";
      totals[posicio] = (totals[posicio] ?? 0) + normalizeNumber(item.segons);
    });
  });

  return Object.entries(totals)
    .map(([name, segons]) => ({ name, segons }))
    .filter((item) => item.segons > 0)
    .sort((a, b) => b.segons - a.segons);
}

export default function LluitadorEvolutionScreen({ onBack }: Props) {
  const analyses = getSavedAnalyses().filter(
    (analysis: SavedAnalysis) => analysis.profileType === "lluitador"
  );

  const metrics = buildMetrics(analyses);
  const positionTotals = buildPositionTotals(analyses);

  if (!analyses.length) {
    return (
      <section className="analysis-container">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon />
        </button>

        <div className="analysis-card">
          <h2 className="analysis-main-title">Evolució</h2>
          <p className="analysis-empty">
            Encara no hi ha anàlisis guardades per calcular l’evolució.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="analysis-container">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeftIcon />
      </button>

      <div className="analysis-header">
        <div>
          <h2 className="analysis-main-title">Evolució del lluitador</h2>
          <p className="analysis-mode-label">
            Seguiment del rendiment a partir dels combats guardats.
          </p>
        </div>
      </div>

      <EvolutionSummary metrics={metrics} />
      <EvolutionCharts metrics={metrics} positionTotals={positionTotals} />
      <EvolutionPatterns analyses={analyses} />
    </section>
  );
}