import { useState } from "react";
import type { AnalysisResponse, UserProfile, SavedAnalysis } from "../types";
import { saveAnalysis, analysisTitleExists } from "../storage/analysisStorage";
import "./SaveAnalysis.css";

type Props = {
  open: boolean;
  onClose: () => void;
  result: AnalysisResponse;
  fightId: string;
  profile: UserProfile;
};

export default function SaveAnalysisModal({
  open,
  onClose,
  result,
  fightId,
  profile,
}: Props) {
  const [title, setTitle] = useState("");
  const [fightDate, setFightDate] = useState("");
  const [studentFolder, setStudentFolder] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  if (!open) return null;

  const isCoach = profile === "entrenador";
  const isSingleAthleteAnalysis = result.mode === "single_athlete";
  const showStudentFolder = isCoach && isSingleAthleteAnalysis;

  const handleSave = () => {
    const trimmedTitle = title.trim();

    if (!trimmedTitle) return;

    if (showStudentFolder && !studentFolder.trim()) return;

    if (analysisTitleExists(trimmedTitle)) {
      setError("Ja existeix una anàlisi amb aquest títol.");
      return;
    }

    const analysisToSave: SavedAnalysis = {
      id: crypto.randomUUID(),
      title: trimmedTitle,
      createdAt: new Date().toISOString(),
      fightId,
      profileType: profile,
      studentFolder: showStudentFolder ? studentFolder.trim() : undefined,
      fightDate: fightDate || undefined,
      result,
    };

    saveAnalysis(analysisToSave);
    setSaved(true);
    setError("");

    setTimeout(() => {
      setTitle("");
      setFightDate("");
      setStudentFolder("");
      setSaved(false);
      setError("");
      onClose();
    }, 800);
  };

  return (
    <div className="save-modal-overlay">
      <div className="save-modal">
        <h2>Guardar anàlisi</h2>

        <label>
          Títol de l’anàlisi
          <input
            type="text"
            placeholder="Ex: Combat contra Jiménez"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setError("");
            }}
          />
        </label>

        <label>
          Data del combat
          <input
            type="date"
            value={fightDate}
            onChange={(e) => setFightDate(e.target.value)}
          />
        </label>

        {showStudentFolder && (
          <label>
            Carpeta / alumne
            <input
              type="text"
              placeholder="Ex: Marc, Pau, Laura..."
              value={studentFolder}
              onChange={(e) => setStudentFolder(e.target.value)}
            />
          </label>
        )}

        {saved && <p className="save-success">Anàlisi guardada correctament.</p>}

        {error && <p className="save-error">{error}</p>}

        <div className="save-modal-actions">
          <button type="button" onClick={onClose} className="secondary-button">
            Cancel·lar
          </button>

          <button
            type="button"
            onClick={handleSave}
            className="primary-button"
            disabled={
              !title.trim() || (showStudentFolder && !studentFolder.trim())
            }
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
}