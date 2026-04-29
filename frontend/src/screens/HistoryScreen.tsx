import { useEffect, useMemo, useState } from "react";
import type { SavedAnalysis } from "../types";
import { getSavedAnalyses } from "../storage/analysisStorage";
import AnalysisResult from "../components/AnalysisResult";
import "./HistoryScreen.css";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";

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

  if (selectedAnalysis) {
    return (
      <div className="history-detail">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedAnalysis(null)}
        >
          <ArrowLeftIcon size={20} />
        </button>

        <AnalysisResult
          result={selectedAnalysis.result}
          profile={selectedAnalysis.profileType}
          fightId={selectedAnalysis.fightId}
          showSaveButton={false}
        />
      </div>
    );
  }

  if (selectedTypeFolder) {
    const selectedAnalyses = analysesByType[selectedTypeFolder];

    return (
      <div className="history-screen">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedTypeFolder(null)}
        >
          <ArrowLeftIcon size={20} />
        </button>

        <div className="history-header">
          <h1 className="history-title">
            {getAnalysisTypeLabel(selectedTypeFolder)}
          </h1>
        </div>

        <AnalysisList
          analyses={selectedAnalyses}
          onSelectAnalysis={setSelectedAnalysis}
        />
      </div>
    );
  }

  if (isCoach && selectedStudentFolder) {
    const studentAnalyses = analysesByStudent[selectedStudentFolder] ?? [];

    return (
      <div className="history-screen">
        <button
          type="button"
          className="back-button"
          onClick={() => setSelectedStudentFolder(null)}
        >
          <ArrowLeftIcon size={20} />
        </button>

        <div className="history-header">
          <h1 className="history-title">{selectedStudentFolder}</h1>
          <p className="history-subtitle">
            Anàlisis guardades per aquest alumne.
          </p>
        </div>

        <AnalysisList
          analyses={studentAnalyses}
          onSelectAnalysis={setSelectedAnalysis}
        />
      </div>
    );
  }

  if (isCoach) {
    const studentFolders = Object.entries(analysesByStudent);

    return (
      <div className="history-screen">
        <button type="button" className="back-button" onClick={onBack}>
          <ArrowLeftIcon size={20} />
        </button>

        <div className="history-header">
          <h1 className="history-title">{title}</h1>
          <p className="history-subtitle">
            Selecciona una carpeta per veure les anàlisis guardades.
          </p>
        </div>

        {analyses.length === 0 ? (
          <div className="history-empty">No hi ha anàlisis guardades.</div>
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
      </div>
    );
  }

  return (
    <div className="history-screen">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeftIcon size={20} />
      </button>

      <div className="history-header">
        <h1 className="history-title">{title}</h1>
        <p className="history-subtitle">
          Selecciona el tipus d’anàlisi que vols consultar.
        </p>
      </div>

      {analyses.length === 0 ? (
        <div className="history-empty">No hi ha anàlisis guardades.</div>
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
    </div>
  );
}

// ---------------- COMPONENTES AUX ----------------

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

          <span className="history-folder-arrow">Obrir →</span>
        </button>
      ))}
    </div>
  );
}

function AnalysisList({
  analyses,
  onSelectAnalysis,
}: {
  analyses: SavedAnalysis[];
  onSelectAnalysis: (analysis: SavedAnalysis) => void;
}) {
  if (analyses.length === 0) {
    return (
      <div className="history-empty">
        No hi ha anàlisis guardades en aquesta carpeta.
      </div>
    );
  }

  return (
    <div className="history-list">
      {analyses.map((analysis) => (
        <button
          key={analysis.id}
          type="button"
          onClick={() => onSelectAnalysis(analysis)}
          className="history-item"
        >
          <div className="history-item-top">
            <strong className="history-item-title">{analysis.title}</strong>

            <span className="history-item-date">
              {new Date(analysis.createdAt).toLocaleString("ca-ES")}
            </span>
          </div>
        </button>
      ))}
    </div>
  );
}