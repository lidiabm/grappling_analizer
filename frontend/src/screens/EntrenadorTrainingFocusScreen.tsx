import { useEffect, useState } from "react";
import "./LluitadorEvolutionScreen.css";
import type { StudentFocus, TrainingFocusResponse } from "../types";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";
import { getSavedAnalyses } from "../storage/analysisStorage";
import EvolutionCharts from "../components/EvolutionCharts";
import { calculateTrainingFocus } from "../api";

type Props = {
  onBack: () => void;
};

function formatChange(value: number, suffix = "") {
  if (value > 0) return `+${value}${suffix}`;
  if (value < 0) return `${value}${suffix}`;
  return `0${suffix}`;
}

export default function EntrenadorTrainingFocusScreen({ onBack }: Props) {
  console.log("ENTRA EN EntrenadorTrainingFocusScreen");

  const [data, setData] = useState<TrainingFocusResponse | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<StudentFocus | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    console.log("USE EFFECT TRAINING FOCUS");

    const analyses = getSavedAnalyses();
    console.log("Analyses enviados:", analyses.length, analyses);

    calculateTrainingFocus(analyses)
      .then((response) => {
        console.log("Respuesta training focus:", response);
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
      <section className="analysis-container">
        <p className="analysis-empty">Calculant focus d’entrenament...</p>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section className="analysis-container">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon />
        </button>

        <div className="analysis-card">
          <h2 className="analysis-main-title">Focus d’entrenament</h2>
          <p className="analysis-empty">{error}</p>
        </div>
      </section>
    );
  }

  if (selectedStudent) {
    return (
      <section className="analysis-container">
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
      <section className="analysis-container">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon />
        </button>

        <div className="analysis-card">
          <h2 className="analysis-main-title">Focus d’entrenament</h2>
          <p className="analysis-empty">No hi ha dades d’alumnes encara.</p>
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
          <h2 className="analysis-main-title">Focus d’entrenament</h2>
          <p className="analysis-mode-label">
            Evolució de les últimes {data.chartWeeks} setmanes i focus basat en les últimes {data.focusWeeks}.
          </p>
        </div>
      </div>

      <GlobalFocusBlock data={data} />

      <div className="analysis-card">
        <h3 className="analysis-card-title">Evolució per alumne</h3>
        <p className="analysis-text">
          Selecciona un alumne per veure la seva evolució combat a combat.
        </p>

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
                  {student.analysesCount} anàlisi
                  {student.analysesCount !== 1 ? "s" : ""}
                </span>
              </div>

              <span className="history-folder-arrow">Veure evolució →</span>
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
      <div className="analysis-card">
        <h3 className="analysis-card-title">
          Focus global dels pròxims entrenos
        </h3>

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
            <span>Anàlisis usades pel focus</span>
            <strong>{data.recentCount}</strong>
          </div>
        </div>

        <div className="opponent-block">
          <span className="opponent-block-title">Prioritats recomanades</span>
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
  return (
    <>
      <div className="analysis-header">
        <div>
          <h2 className="analysis-main-title">{student.studentName}</h2>
          <p className="analysis-mode-label">
            Evolució combat a combat basada en dades objectives.
          </p>
        </div>
      </div>

      <div className="analysis-card">
        <div className="evolution-summary-grid">
          <div className="evolution-card">
            <span>Combats</span>
            <strong>{student.analysesCount}</strong>
          </div>

          <div className="evolution-card">
            <span>Canvi domini</span>
            <strong>{formatChange(student.summary.dominantChange, "s")}</strong>
          </div>

          <div className="evolution-card">
            <span>Canvi defensa</span>
            <strong>{formatChange(student.summary.defensiveChange, "s")}</strong>
          </div>

          <div className="evolution-card">
            <span>Canvi finalitzacions</span>
            <strong>{formatChange(student.summary.submissionChange)}</strong>
          </div>

          <div className="evolution-card evolution-card-wide">
            <span>Evolució</span>
            <strong>{student.summary.evolutionText}</strong>
          </div>

          <div className="evolution-card evolution-card-wide">
            <span>Focus</span>
            <strong>{student.summary.mainFocus}</strong>
          </div>
        </div>
      </div>

      <EvolutionCharts
        metrics={student.metrics}
        positionTotals={student.positionTotals}
      />
    </>
  );
}