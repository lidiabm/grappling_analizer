import { useState } from "react";
import type { AnalysisResponse, UserProfile } from "../types";
import UploadForm from "../components/UploadForm";
import AnalysisResult from "../components/AnalysisResult";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";
import "./AnalysisScreen.css";

type Props = {
  profile: UserProfile;
  onBack: () => void;
};

function AnalysisScreen({ profile, onBack }: Props) {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState(
    "combat-sense-titol"
  );

  const isCoach = profile === "entrenador";

  function handleStart() {
    setIsAnalyzing(true);
    setResult(null);
  }

  function handleResult(newResult: AnalysisResponse) {
    setResult(newResult);
    setIsAnalyzing(false);
  }

  return (
    <section className="analysis-screen app-content">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeftIcon size={20} />
      </button>

      <header className="analysis-screen-header">
        <span className="analysis-screen-eyebrow">
          Anàlisi de combat
        </span>

        <h2 className="analysis-screen-title">
          {isCoach
            ? "Anàlisi per a entrenador"
            : "Anàlisi per a lluitador"}
        </h2>

        <p className="analysis-screen-subtitle">
          {isCoach
            ? "Analitza combats complets o centra’t en un esportista concret per detectar patrons, errors i oportunitats de millora."
            : "Analitza el teu combat per entendre millor el teu rendiment, les teves decisions i les situacions clau."}
        </p>
      </header>

      <div className="analysis-screen-grid">
        <section className="analysis-upload-card">
          <div className="analysis-card-header">
            <div>
              <span className="analysis-card-eyebrow">
                Entrada de vídeo
              </span>

              <h3>Pujar combat</h3>

              <p>
                Selecciona un vídeo i configura el tipus d’anàlisi que vols
                generar.
              </p>
            </div>
          </div>

          <UploadForm
            profile={profile}
            onStart={handleStart}
            onResult={handleResult}
            onFileSelected={setSelectedFileName}
          />
        </section>

        <section className="analysis-result-card">
          {isAnalyzing && !result && (
            <div className="analysis-placeholder">
              <div className="analysis-loading-spinner" />

              <div>
                <h3>Analitzant combat...</h3>

                <p>
                  La IA està processant el vídeo i generant l’informe tècnic.
                </p>
              </div>
            </div>
          )}

          {!isAnalyzing && !result && (
            <div className="analysis-placeholder">
              <div className="analysis-placeholder-icon">◎</div>

              <div>
                <h3>Encara no hi ha cap anàlisi</h3>

                <p>
                  Puja un combat per generar un informe detallat del rendiment.
                </p>
              </div>
            </div>
          )}

          {result && (
            <AnalysisResult
              result={result}
              profile={profile}
              fightId={selectedFileName}
            />
          )}
        </section>
      </div>
    </section>
  );
}

export default AnalysisScreen;