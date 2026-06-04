import { useState } from "react";
import type { AnalysisResponse, UserProfile, SavedAnalysis } from "../types";
import { saveAnalysis, analysisTitleExists } from "../storage/analysisStorage";
import "./SaveAnalysisModal.css";

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

  function resetAndClose() {
    setTitle("");
    setFightDate("");
    setStudentFolder("");
    setSaved(false);
    setError("");
    onClose();
  }

  function handleSave() {
    const trimmedTitle = title.trim();
    const trimmedStudentFolder = studentFolder.trim();

    if (!trimmedTitle) {
      setError("Has d’afegir un títol per guardar l’anàlisi.");
      return;
    }

    if (!fightDate) {
      setError("Has d’indicar la data del combat.");
      return;
    }

    if (showStudentFolder && !trimmedStudentFolder) {
      setError("Has d’indicar la carpeta o el nom de l’alumne.");
      return;
    }

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
      studentFolder: showStudentFolder ? trimmedStudentFolder : undefined,
      fightDate: fightDate,
      result,
    };

    saveAnalysis(analysisToSave);
    setSaved(true);
    setError("");

    setTimeout(() => {
      resetAndClose();
    }, 800);
  }

  return (
    <div className="save-modal-overlay" role="presentation">
      <section
        className="save-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="save-analysis-title"
      >
        <header className="save-modal-header">
          <span className="save-modal-eyebrow">Guardar informe</span>

          <h2 id="save-analysis-title">Guardar anàlisi</h2>

          <p>
            Desa aquest resultat al teu historial per consultar-lo més endavant.
          </p>
        </header>

        <div className="save-modal-form">
          <label className="save-modal-field">
            <span>Títol de l’anàlisi</span>

            <input
              type="text"
              required
              placeholder="Ex: Combat contra Jiménez"
              value={title}
              onChange={(event) => {
                setTitle(event.target.value);
                setError("");
              }}
            />
          </label>

          <label className="save-modal-field">
            <span>Data del combat</span>

            <input
              className="save-modal-date-input"
              type="date"
              required
              value={fightDate}
              onChange={(event) => setFightDate(event.target.value)}
            />
          </label>

          {showStudentFolder && (
            <label className="save-modal-field">
              <span>Carpeta / alumne</span>

              <input
                type="text"
                placeholder="Ex: Marc, Pau, Laura..."
                value={studentFolder}
                onChange={(event) => {
                  setStudentFolder(event.target.value);
                  setError("");
                }}
              />
            </label>
          )}
        </div>

        {saved && (
          <div className="save-modal-success">
            Anàlisi guardada correctament.
          </div>
        )}

        {error && <div className="save-modal-error">{error}</div>}

        <footer className="save-modal-actions">
          <button
            type="button"
            onClick={resetAndClose}
            className="secondary-button"
          >
            Cancel·lar
          </button>

          <button
            type="button"
            onClick={handleSave}
            className="primary-button"
            disabled={
              !title.trim() ||
              !fightDate ||
              (showStudentFolder && !studentFolder.trim())
            }
          >
            Guardar
          </button>
        </footer>
      </section>
    </div>
  );
}