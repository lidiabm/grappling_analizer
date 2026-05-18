import { useEffect, useMemo, useState } from "react";
import type { SavedAnalysis } from "../types";
import { getSavedAnalyses, deleteAnalysis } from "../storage/analysisStorage";
import AnalysisResult from "../components/AnalysisResult";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";
import "./HistoryScreen.css";

type Props = {
  onBack: () => void;
  profileFilter: "lluitador" | "entrenador";
  title?: string;
};

type AnalysisTypeFolder = "own" | "complete";

function getAnalysisTypeFolder(analysis: SavedAnalysis): AnalysisTypeFolder {
  return analysis.result.mode === "single_athlete" ? "own" : "complete";
}

function getAnalysisTypeLabel(type: AnalysisTypeFolder) {
  return type === "own" ? "Anàlisis propis" : "Anàlisis complets";
}

function formatDate(value?: string) {
  if (!value) return "Sense data";

  return new Date(value).toLocaleDateString("ca-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

export default function HistoryScreen({
  onBack,
  profileFilter,
  title = "Historial",
}: Props) {
  const [analyses, setAnalyses] = useState<SavedAnalysis[]>([]);
  const [selectedStudentFolder, setSelectedStudentFolder] =
    useState<string | null>(null);
  const [selectedTypeFolder, setSelectedTypeFolder] =
    useState<AnalysisTypeFolder | null>(null);
  const [selectedAnalysis, setSelectedAnalysis] =
    useState<SavedAnalysis | null>(null);

  const isCoach = profileFilter === "entrenador";

  useEffect(() => {
    const saved = getSavedAnalyses().filter(
      (analysis) => analysis.profileType === profileFilter
    );

    setAnalyses(saved);
  }, [profileFilter]);

  const coachGeneralAnalyses = useMemo(() => {
    return analyses.filter((analysis) => !analysis.studentFolder?.trim());
  }, [analyses]);

  const analysesByStudent = useMemo(() => {
    return analyses.reduce<Record<string, SavedAnalysis[]>>((acc, analysis) => {
      const folder = analysis.studentFolder?.trim();

      if (!folder) return acc;

      if (!acc[folder]) acc[folder] = [];
      acc[folder].push(analysis);

      return acc;
    }, {});
  }, [analyses]);

  const analysesByType = useMemo(() => {
    return analyses.reduce<Record<AnalysisTypeFolder, SavedAnalysis[]>>(
      (acc, analysis) => {
        const type = getAnalysisTypeFolder(analysis);
        acc[type].push(analysis);
        return acc;
      },
      { own: [], complete: [] }
    );
  }, [analyses]);

  function handleDeleteAnalysis(id: string) {
    const confirmDelete = window.confirm(
      "Segur que vols eliminar aquesta anàlisi?"
    );

    if (!confirmDelete) return;

    deleteAnalysis(id);

    setAnalyses((current) => current.filter((analysis) => analysis.id !== id));

    if (selectedAnalysis?.id === id) {
      setSelectedAnalysis(null);
    }
  }

  if (selectedAnalysis) {
    return (
      <section className="history-screen app-content">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedAnalysis(null)}
        >
          <ArrowLeftIcon />
        </button>

        <AnalysisResult
          result={selectedAnalysis.result}
          profile={selectedAnalysis.profileType}
          fightId={selectedAnalysis.fightId}
          showSaveButton={false}
          onDelete={() => handleDeleteAnalysis(selectedAnalysis.id)}
        />
      </section>
    );
  }

  if (selectedTypeFolder) {
    const selectedAnalyses = analysesByType[selectedTypeFolder];

    return (
      <section className="history-screen app-content">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedTypeFolder(null)}
        >
          <ArrowLeftIcon />
        </button>

        <HistoryHeader
          eyebrow="Carpeta"
          title={getAnalysisTypeLabel(selectedTypeFolder)}
          subtitle="Consulta les anàlisis guardades en aquesta carpeta."
        />

        <AnalysisList
          analyses={selectedAnalyses}
          onSelectAnalysis={setSelectedAnalysis}
          onDeleteAnalysis={handleDeleteAnalysis}
        />
      </section>
    );
  }

  if (isCoach && selectedStudentFolder) {
    const studentAnalyses = analysesByStudent[selectedStudentFolder] ?? [];

    return (
      <section className="history-screen app-content">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedStudentFolder(null)}
        >
          <ArrowLeftIcon />
        </button>

        <HistoryHeader
          eyebrow="Alumne"
          title={selectedStudentFolder}
          subtitle="Anàlisis guardades per aquest alumne."
        />

        <AnalysisList
          analyses={studentAnalyses}
          onSelectAnalysis={setSelectedAnalysis}
          onDeleteAnalysis={handleDeleteAnalysis}
        />
      </section>
    );
  }

  if (isCoach) {
    const studentFolders = Object.entries(analysesByStudent);

    return (
      <section className="history-screen app-content">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon />
        </button>

        <HistoryHeader
          eyebrow="Historial d’entrenador"
          title={title}
          subtitle="Selecciona una carpeta per consultar les anàlisis guardades."
        />

        {analyses.length === 0 ? (
          <HistoryEmpty text="No hi ha anàlisis guardades." />
        ) : (
          <FolderGrid
            folders={[
              {
                name: "Anàlisis complets",
                count: coachGeneralAnalyses.length,
                onClick: () => setSelectedTypeFolder("complete"),
              },
              ...studentFolders.map(([name, items]) => ({
                name,
                count: items.length,
                onClick: () => setSelectedStudentFolder(name),
              })),
            ]}
          />
        )}
      </section>
    );
  }

  return (
    <section className="history-screen app-content">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeftIcon />
      </button>

      <HistoryHeader
        eyebrow="Historial de lluitador"
        title={title}
        subtitle="Selecciona el tipus d’anàlisi que vols consultar."
      />

      {analyses.length === 0 ? (
        <HistoryEmpty text="No hi ha anàlisis guardades." />
      ) : (
        <FolderGrid
          folders={[
            {
              name: "Anàlisis propis",
              count: analysesByType.own.length,
              onClick: () => setSelectedTypeFolder("own"),
            },
            {
              name: "Anàlisis complets",
              count: analysesByType.complete.length,
              onClick: () => setSelectedTypeFolder("complete"),
            },
          ]}
        />
      )}
    </section>
  );
}

function HistoryHeader({
  eyebrow,
  title,
  subtitle,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
}) {
  return (
    <header className="history-header">
      <span className="history-eyebrow">{eyebrow}</span>
      <h2 className="history-title">{title}</h2>
      <p className="history-subtitle">{subtitle}</p>
    </header>
  );
}

function HistoryEmpty({ text }: { text: string }) {
  return (
    <div className="history-empty">
      <span className="history-eyebrow">Sense dades</span>
      <h3>Encara no hi ha contingut</h3>
      <p>{text}</p>
    </div>
  );
}

function FolderGrid({
  folders,
}: {
  folders: {
    name: string;
    count: number;
    onClick: () => void;
  }[];
}) {
  return (
    <div className="history-folder-grid">
      {folders.map((folder) => (
        <button
          key={folder.name}
          type="button"
          className="history-folder"
          onClick={folder.onClick}
          disabled={folder.count === 0}
        >
          <div>
            <strong className="history-folder-title">{folder.name}</strong>

            <span className="history-folder-count">
              {folder.count} anàlisi{folder.count !== 1 ? "s" : ""}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}

function AnalysisList({
  analyses,
  onSelectAnalysis,
  onDeleteAnalysis,
}: {
  analyses: SavedAnalysis[];
  onSelectAnalysis: (analysis: SavedAnalysis) => void;
  onDeleteAnalysis: (id: string) => void;
}) {
  if (analyses.length === 0) {
    return (
      <HistoryEmpty text="No hi ha anàlisis guardades en aquesta carpeta." />
    );
  }

  return (
    <div className="history-list">
      {analyses.map((analysis) => (
        <article key={analysis.id} className="history-item">
          <button
            type="button"
            onClick={() => onSelectAnalysis(analysis)}
            className="history-item-content"
          >
            <div>
              <strong className="history-item-title">{analysis.title}</strong>

              <span className="history-item-meta">
                {getAnalysisTypeLabel(getAnalysisTypeFolder(analysis))}
              </span>
            </div>

            <span className="history-item-date">
              {formatDate(analysis.fightDate)}
            </span>
          </button>

          <button
            type="button"
            className="history-delete-button"
            onClick={(event) => {
              event.stopPropagation();
              onDeleteAnalysis(analysis.id);
            }}
            aria-label="Eliminar anàlisi"
          >
            ✕
          </button>
        </article>
      ))}
    </div>
  );
}