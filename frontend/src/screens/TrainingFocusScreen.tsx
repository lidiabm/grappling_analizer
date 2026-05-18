import { useEffect, useMemo, useState } from "react";
import type {
  SavedAnalysis,
  StudentFocus,
  TrainingFocusResponse,
} from "../types";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";
import { getSavedAnalyses } from "../storage/analysisStorage";
import EvolutionCharts from "../components/charts/EvolutionCharts";
import { calculateTrainingFocus } from "../api";
import "./TrainingFocusScreen.css";

type Props = {
  onBack: () => void;
};

const CHART_WEEKS = 10;
const FOCUS_WEEKS = 3;

function getDateWeeksAgo(weeks: number) {
  const date = new Date();
  date.setDate(date.getDate() - weeks * 7);
  date.setHours(0, 0, 0, 0);
  return date;
}

function isAnalysisInLastWeeks(analysis: SavedAnalysis, weeks: number) {
  if (!analysis.fightDate) return false;

  const fightDate = new Date(analysis.fightDate);
  const limitDate = getDateWeeksAgo(weeks);

  if (Number.isNaN(fightDate.getTime())) return false;

  return fightDate >= limitDate;
}

function formatChange(value: number, suffix = "") {
  if (value > 0) return `+${value}${suffix}`;
  if (value < 0) return `${value}${suffix}`;
  return `0${suffix}`;
}

function getTrendText(value: number, positiveIsGood = true) {
  if (value === 0) return "Estable";

  const isPositive = value > 0;
  const isGood = positiveIsGood ? isPositive : !isPositive;

  return isGood ? "Millora" : "Empitjora";
}

function getTrendClass(value: number, positiveIsGood = true) {
  if (value === 0) return "neutral";

  const isPositive = value > 0;
  const isGood = positiveIsGood ? isPositive : !isPositive;

  return isGood ? "positive" : "negative";
}

function getStudentAlerts(student: StudentFocus) {
  const alerts: string[] = [];
  const lastMetric = student.metrics.at(-1);

  if (!lastMetric) return alerts;

  if (lastMetric.defensivePct >= 40) {
    alerts.push("Passa massa temps en situacions defensives.");
  }

  if (lastMetric.dominantPct < 25) {
    alerts.push("Té poc temps de control dominant.");
  }

  if (lastMetric.escapes === 0 && lastMetric.defensiveTime > 60) {
    alerts.push("Necessita treballar sortides i recuperació de posició.");
  }

  if (lastMetric.submissionAttempts === 0 && lastMetric.dominantTime > 60) {
    alerts.push("Arriba a posicions bones, però genera poques finalitzacions.");
  }

  if (lastMetric.guardPulls > lastMetric.takedownAttempts) {
    alerts.push("Depèn més del guard pull que dels enderrocs.");
  }

  return alerts;
}

function getRatePerMinute(total: number, seconds: number) {
  if (seconds <= 0) return 0;
  return Number((total / (seconds / 60)).toFixed(2));
}

function getStudentRates(student: StudentFocus) {
  const totals = student.metrics.reduce(
    (acc, item) => {
      const totalSeconds =
        item.dominantTime + item.defensiveTime + item.neutralTime;

      acc.seconds += totalSeconds;
      acc.submissions += item.submissionAttempts;
      acc.takedowns += item.takedownAttempts;
      acc.escapes += item.escapes;

      return acc;
    },
    {
      seconds: 0,
      submissions: 0,
      takedowns: 0,
      escapes: 0,
    }
  );

  return {
    submissionsPerMinute: getRatePerMinute(totals.submissions, totals.seconds),
    takedownsPerMinute: getRatePerMinute(totals.takedowns, totals.seconds),
    escapesPerMinute: getRatePerMinute(totals.escapes, totals.seconds),
  };
}

export default function EntrenadorTrainingFocusScreen({ onBack }: Props) {
  const [data, setData] = useState<TrainingFocusResponse | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<StudentFocus | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const analyses = getSavedAnalyses();

    const chartAnalyses = analyses.filter((analysis) =>
      isAnalysisInLastWeeks(analysis, CHART_WEEKS)
    );

    calculateTrainingFocus(chartAnalyses, {
      chartWeeks: CHART_WEEKS,
      focusWeeks: FOCUS_WEEKS,
    })
      .then((response) => {
        setData(response);
      })
      .catch((err) => {
        console.error("Error training focus:", err);
        setError(err instanceof Error ? err.message : "Error desconegut");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="training-focus-screen app-content">
        <p className="training-focus-empty">Calculant focus d’entrenament...</p>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section className="training-focus-screen app-content">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon />
        </button>

        <div className="training-focus-card">
          <span className="training-focus-eyebrow">Entrenador</span>
          <h2 className="training-focus-title">Focus d’entrenament</h2>
          <p className="training-focus-empty">
            {error || "No s’han pogut carregar les dades."}
          </p>
        </div>
      </section>
    );
  }

  if (selectedStudent) {
    return (
      <section className="training-focus-screen app-content">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedStudent(null)}
        >
          <ArrowLeftIcon />
        </button>

        <StudentBlock student={selectedStudent} />
      </section>
    );
  }

  if (!data.students.length) {
    return (
      <section className="training-focus-screen app-content">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon />
        </button>

        <div className="training-focus-card">
          <span className="training-focus-eyebrow">Entrenador</span>
          <h2 className="training-focus-title">Focus d’entrenament</h2>
          <p className="training-focus-empty">
            No hi ha combats amb data dins de les últimes {CHART_WEEKS} setmanes.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="training-focus-screen app-content">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeftIcon />
      </button>

      <header className="training-focus-header">
        <span className="training-focus-eyebrow">Panell de rendiment</span>
        <h2 className="training-focus-title">Focus d’entrenament</h2>
        <p className="training-focus-subtitle">
          Evolució de les últimes {data.chartWeeks} setmanes i recomanacions
          basades en les últimes {data.focusWeeks} setmanes.
        </p>
      </header>

      <GlobalFocusBlock data={data} />

      <div className="training-focus-card">
        <div className="training-focus-section-heading">
          <span className="training-focus-eyebrow">Alumnes</span>
          <h3 className="training-focus-card-title">Evolució individual</h3>
          <p className="training-focus-text">
            Selecciona un alumne per veure su evolución combat a combat.
          </p>
        </div>

        <div className="history-folder-grid">
          {data.students.map((student) => (
            <button
              key={student.studentName}
              type="button"
              className="history-folder"
              onClick={() => setSelectedStudent(student)}
            >
              <div>
                <strong className="history-folder-title">
                  {student.studentName}
                </strong>

                <span className="history-folder-count">
                  {student.analysesCount} combat
                  {student.analysesCount !== 1 ? "s" : ""}
                </span>
              </div>

              <span className="history-folder-arrow">Veure →</span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function GlobalFocusBlock({ data }: { data: TrainingFocusResponse }) {
  return (
    <>
      <div className="training-focus-card">
        <div className="training-focus-section-heading">
          <span className="training-focus-eyebrow">Resum global</span>
          <h3 className="training-focus-card-title">
            Estat general del grup
          </h3>
        </div>

        <div className="evolution-summary-grid">
          <div className="evolution-card">
            <span>Alumnes</span>
            <strong>{data.studentsCount}</strong>
          </div>

          <div className="evolution-card">
            <span>Anàlisis totals</span>
            <strong>{data.analysesCount}</strong>
          </div>

          <div className="evolution-card">
            <span>Anàlisis recents</span>
            <strong>{data.recentCount}</strong>
          </div>
        </div>

        <div className="opponent-block">
          <span className="opponent-block-title">
            Prioritats recomanades
          </span>

          <p className="opponent-block-subtitle">
            Basades en les últimes {data.focusWeeks} setmanes.
          </p>

          <ul className="analysis-list">
            {data.globalFocus.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      <EvolutionCharts
        metrics={data.globalMetrics}
        positionTotals={data.globalPositionTotals}
      />
    </>
  );
}

function StudentBlock({ student }: { student: StudentFocus }) {
  const alerts = useMemo(() => getStudentAlerts(student), [student]);
  const rates = useMemo(() => getStudentRates(student), [student]);

  return (
    <>
      <header className="training-focus-header">
        <span className="training-focus-eyebrow">Evolució individual</span>
        <h2 className="training-focus-title">{student.studentName}</h2>
        <p className="training-focus-subtitle">
          Evolució combat a combat basada en les últimes {CHART_WEEKS} setmanes.
        </p>
      </header>

      <div className="training-focus-card">
        <div className="training-focus-section-heading">
          <span className="training-focus-eyebrow">Rendiment</span>
          <h3 className="training-focus-card-title">Resum tècnic</h3>
        </div>

        <div className="evolution-summary-grid">
          <div className="evolution-card">
            <span>Combats</span>
            <strong>{student.analysesCount}</strong>
          </div>

          <div
            className={`evolution-card ${getTrendClass(
              student.summary.dominantChange,
              true
            )}`}
          >
            <span>Domini</span>
            <strong>{formatChange(student.summary.dominantChange, "s")}</strong>
            <small>{getTrendText(student.summary.dominantChange, true)}</small>
          </div>

          <div
            className={`evolution-card ${getTrendClass(
              student.summary.defensiveChange,
              false
            )}`}
          >
            <span>Defensa</span>
            <strong>{formatChange(student.summary.defensiveChange, "s")}</strong>
            <small>{getTrendText(student.summary.defensiveChange, false)}</small>
          </div>

          <div
            className={`evolution-card ${getTrendClass(
              student.summary.submissionChange,
              true
            )}`}
          >
            <span>Finalitzacions</span>
            <strong>{formatChange(student.summary.submissionChange)}</strong>
            <small>{getTrendText(student.summary.submissionChange, true)}</small>
          </div>

          <div className="evolution-card">
            <span>Finalitzacions/min</span>
            <strong>{rates.submissionsPerMinute}</strong>
          </div>

          <div className="evolution-card">
            <span>Enderrocs/min</span>
            <strong>{rates.takedownsPerMinute}</strong>
          </div>

          <div className="evolution-card">
            <span>Escapades/min</span>
            <strong>{rates.escapesPerMinute}</strong>
          </div>

          <div className="evolution-card evolution-card-wide">
            <span>Evolució general</span>
            <strong>{student.summary.evolutionText}</strong>
          </div>

          <div className="evolution-card evolution-card-wide">
            <span>Focus principal</span>
            <strong>{student.summary.mainFocus}</strong>
          </div>
        </div>
      </div>

      {alerts.length > 0 && (
        <div className="training-focus-card">
          <div className="training-focus-section-heading">
            <span className="training-focus-eyebrow">Alertes</span>
            <h3 className="training-focus-card-title">Alertes tècniques</h3>
          </div>

          <ul className="analysis-list">
            {alerts.map((alert, index) => (
              <li key={index}>{alert}</li>
            ))}
          </ul>
        </div>
      )}

      <EvolutionCharts
        metrics={student.metrics}
        positionTotals={student.positionTotals}
      />
    </>
  );
}