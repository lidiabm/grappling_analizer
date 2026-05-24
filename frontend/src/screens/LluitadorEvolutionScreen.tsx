import { useMemo, useState } from "react";
import { analyzeFighterEvolution } from "../api";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";
import { getSavedAnalyses } from "../storage/analysisStorage";
import type { FighterEvolutionResponse, SavedAnalysis } from "../types";
import "./LluitadorEvolutionScreen.css";

type Props = {
  onBack: () => void;
};

function formatDate(value?: string) {
  if (!value) return "Sense data";

  return new Date(value).toLocaleDateString("ca-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function getAnalysisDate(analysis: SavedAnalysis) {
  return analysis.fightDate || analysis.createdAt;
}

function getAnalysisTimestamp(analysis?: SavedAnalysis) {
  if (!analysis) return 0;

  const date = getAnalysisDate(analysis);
  const timestamp = new Date(date).getTime();

  return Number.isNaN(timestamp) ? 0 : timestamp;
}

function isOldReallyOlder(
  oldAnalysis?: SavedAnalysis,
  newAnalysis?: SavedAnalysis
) {
  if (!oldAnalysis || !newAnalysis) return false;

  return getAnalysisTimestamp(oldAnalysis) < getAnalysisTimestamp(newAnalysis);
}

function LluitadorEvolutionScreen({ onBack }: Props) {
  const analyses = useMemo(() => {
    return getSavedAnalyses()
      .filter(
        (analysis) =>
          analysis.profileType === "lluitador" &&
          analysis.result.mode === "single_athlete"
      )
      .sort(
        (a, b) => getAnalysisTimestamp(b) - getAnalysisTimestamp(a)
      );
  }, []);

  const [oldAnalysisId, setOldAnalysisId] = useState("");
  const [newAnalysisId, setNewAnalysisId] = useState("");
  const [result, setResult] = useState<FighterEvolutionResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState("");

  const oldAnalysis = analyses.find((analysis) => analysis.id === oldAnalysisId);
  const newAnalysis = analyses.find((analysis) => analysis.id === newAnalysisId);

  const hasValidChronology = isOldReallyOlder(oldAnalysis, newAnalysis);

  const canAnalyze =
    Boolean(oldAnalysis) &&
    Boolean(newAnalysis) &&
    oldAnalysisId !== newAnalysisId &&
    hasValidChronology &&
    !isAnalyzing;

  async function handleAnalyzeEvolution() {
    if (!oldAnalysis || !newAnalysis) {
      setError("Has de seleccionar dos anàlisis.");
      return;
    }

    if (oldAnalysis.id === newAnalysis.id) {
      setError("Has de seleccionar dos anàlisis diferents.");
      return;
    }

    if (!isOldReallyOlder(oldAnalysis, newAnalysis)) {
      setError("L’anàlisi antic ha de ser anterior a l’anàlisi recent.");
      return;
    }

    setIsAnalyzing(true);
    setError("");
    setResult(null);

    try {
      const response = await analyzeFighterEvolution({
        old_analysis: oldAnalysis.result,
        new_analysis: newAnalysis.result,
      });

      setResult(response);
      setOldAnalysisId("");
      setNewAnalysisId("");
    } catch (err) {
      console.error(err);
      setError("No s’ha pogut generar l’evolució del lluitador.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <section className="fighter-evolution-screen app-content">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeftIcon />
      </button>

      <header className="fighter-evolution-header">
        <span className="fighter-evolution-eyebrow">Evolució personal</span>
        <h2 className="fighter-evolution-title">Evolució del lluitador</h2>
        <p className="fighter-evolution-subtitle">
          Compara dos anàlisis propis per veure què ha millorat, què s’ha
          mantingut i quines prioritats hauries de treballar.
        </p>
      </header>

      {analyses.length < 2 ? (
        <section className="fighter-evolution-empty">
          <span className="fighter-evolution-eyebrow">Dades insuficients</span>
          <h3>No hi ha prou anàlisis guardats</h3>
          <p>
            Necessites com a mínim dos anàlisis propis del lluitador per poder
            calcular una evolució fiable.
          </p>
        </section>
      ) : (
        <>
          <section className="fighter-evolution-compare-card">
            <div className="fighter-evolution-compare-header">
              <div>
                <span className="fighter-evolution-eyebrow">Comparativa</span>
                <h3>Selecciona dos combats</h3>
              </div>

              <span className="fighter-evolution-counter">
                {analyses.length} anàlisis disponibles
              </span>
            </div>

            <div className="fighter-evolution-selector-grid">
              <AnalysisSelector
                label="Anàlisi antic"
                description="Escull el combat que servirà com a punt de partida."
                value={oldAnalysisId}
                analyses={analyses}
                selectedAnalysis={oldAnalysis}
                disabled={isAnalyzing}
                onChange={(value) => {
                  setOldAnalysisId(value);
                  setError("");
                }}
              />

              <AnalysisSelector
                label="Anàlisi recent"
                description="Escull el combat que vols comparar amb l’anterior."
                value={newAnalysisId}
                analyses={analyses}
                selectedAnalysis={newAnalysis}
                disabled={isAnalyzing}
                onChange={(value) => {
                  setNewAnalysisId(value);
                  setError("");
                }}
              />
            </div>

            {oldAnalysis &&
              newAnalysis &&
              oldAnalysisId !== newAnalysisId &&
              !hasValidChronology && (
                <div className="fighter-evolution-alert">
                  <strong>Ordre incorrecte</strong>
                  <span>
                    L’anàlisi antic ha de tenir una data anterior a l’anàlisi
                    recent.
                  </span>
                </div>
              )}

            {error && (
              <div className="fighter-evolution-alert">
                <strong>Error</strong>
                <span>{error}</span>
              </div>
            )}

            <button
              type="button"
              className="primary-button fighter-evolution-action"
              disabled={!canAnalyze}
              onClick={handleAnalyzeEvolution}
            >
              {isAnalyzing ? "Analitzant evolució..." : "Generar evolució"}
            </button>
          </section>

          {result && <EvolutionResults result={result} />}
        </>
      )}
    </section>
  );
}

function AnalysisSelector({
  label,
  description,
  value,
  analyses,
  selectedAnalysis,
  disabled,
  onChange,
}: {
  label: string;
  description: string;
  value: string;
  analyses: SavedAnalysis[];
  selectedAnalysis?: SavedAnalysis;
  disabled: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <article className="fighter-evolution-selector-card">
      <div>
        <h4>{label}</h4>
        <p>{description}</p>
      </div>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
      >
        <option value="">Selecciona un anàlisi</option>

        {analyses.map((analysis) => (
          <option key={analysis.id} value={analysis.id}>
            {analysis.title} · {formatDate(getAnalysisDate(analysis))}
          </option>
        ))}
      </select>

      {selectedAnalysis && (
        <div className="fighter-evolution-selected-analysis">
          <strong>{selectedAnalysis.title}</strong>
          <span>{formatDate(getAnalysisDate(selectedAnalysis))}</span>
        </div>
      )}
    </article>
  );
}

function EvolutionResults({ result }: { result: FighterEvolutionResponse }) {
  const recommendations = result.recomanacions_entrenament;

  return (
    <section className="fighter-evolution-results">
      <div className="fighter-evolution-result-hero">
        <span className="fighter-evolution-eyebrow">Informe generat</span>
        <h3>Resum de l’evolució</h3>
        <p>{result.resum_evolucio}</p>

        <div className="fighter-evolution-meta">
          <span>Canvi global: {result.magnitud_canvi_global}</span>
          <span>Confiança: {result.fighter_info.confianca_analisi}</span>
        </div>
      </div>

      <div className="fighter-evolution-result-grid">
        <ResultCard title="Millores detectades" items={result.millores} />

        <ResultCard
          title="Regressions o empitjoraments"
          items={result.regressions}
        />

        <ResultCard
          title="Fortaleses consolidades"
          items={result.patrons_estables.fortaleses_consolidades}
        />

        <ResultCard
          title="Debilitats persistents"
          items={result.patrons_estables.debilitats_persistents}
        />

        <ResultTextCard
          title="Evolució tècnica"
          text={[
            result.evolucio_tecnica.tecniques_millorades.length
              ? `Tècniques millorades:\n- ${result.evolucio_tecnica.tecniques_millorades.join("\n- ")}`
              : "",
            result.evolucio_tecnica.tecniques_empitjorades.length
              ? `Tècniques empitjorades:\n- ${result.evolucio_tecnica.tecniques_empitjorades.join("\n- ")}`
              : "",
            result.evolucio_tecnica.tecniques_noves.length
              ? `Tècniques noves:\n- ${result.evolucio_tecnica.tecniques_noves.join("\n- ")}`
              : "",
            result.evolucio_tecnica.tecniques_abandonades.length
              ? `Tècniques abandonades:\n- ${result.evolucio_tecnica.tecniques_abandonades.join("\n- ")}`
              : "",
          ]
            .filter(Boolean)
            .join("\n\n")}
          wide
        />

        <ResultTextCard
          title="Evolució tàctica"
          text={[
            `Model antic: ${result.evolucio_tactica.model_antic}`,
            `Model recent: ${result.evolucio_tactica.model_recent}`,
            `Canvi observat: ${result.evolucio_tactica.canvi_observat}`,
            `Interpretació: ${result.evolucio_tactica.interpretacio}`,
          ].join("\n\n")}
          wide
        />

        {recommendations && (
          <>
            <ResultCard
              title="Prioritat alta"
              items={recommendations.prioritat_alta}
            />

            <ResultCard
              title="Prioritat mitjana"
              items={recommendations.prioritat_mitjana}
            />

            <ResultCard
              title="Manteniment"
              items={recommendations.manteniment}
            />
          </>
        )}

        <ResultTextCard title="Conclusió" text={result.conclusio} wide />

        <ResultCard title="Incerteses" items={result.incerteses} wide />
      </div>
    </section>
  );
}

function ResultCard({
  title,
  items,
  wide = false,
}: {
  title: string;
  items: string[];
  wide?: boolean;
}) {
  return (
    <article
      className={`fighter-evolution-result-card ${
        wide ? "fighter-evolution-result-card-wide" : ""
      }`}
    >
      <h4>{title}</h4>

      {items.length > 0 ? (
        <ul>
          {items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>No hi ha dades suficients.</p>
      )}
    </article>
  );
}

function ResultTextCard({
  title,
  text,
  wide = false,
}: {
  title: string;
  text: string;
  wide?: boolean;
}) {
  return (
    <article
      className={`fighter-evolution-result-card ${
        wide ? "fighter-evolution-result-card-wide" : ""
      }`}
    >
      <h4>{title}</h4>
      <p style={{ whiteSpace: "pre-line" }}>
        {text || "No hi ha dades suficients."}
      </p>
    </article>
  );
}

export default LluitadorEvolutionScreen;