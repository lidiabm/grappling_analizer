import { useState } from "react";
import type { AnalysisResponse, UserProfile } from "./types";
import UploadForm from "./components/UploadForm";
import AnalysisResult from "./components/AnalysisResult";
import "./App.css";

type FeatureLluitador =
  | "analysis"
  | "scouting"
  | "history"
  | "evolution"
  | null;

type FeatureEntrenador =
  | "analysis"
  | "training_focus"
  | "scouting"
  | "athletes"
  | null;

function App() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedProfile, setSelectedProfile] = useState<UserProfile | null>(null);
  const [selectedFeatureLluitador, setSelectedFeatureLluitador] =
    useState<FeatureLluitador>(null);
  const [selectedFeatureEntrenador, setSelectedFeatureEntrenador] =
    useState<FeatureEntrenador>(null);

  function handleStart() {
    setIsAnalyzing(true);
    setResult(null);
  }

  function handleResult(newResult: AnalysisResponse) {
    setResult(newResult);
    setIsAnalyzing(false);
  }

  function handleProfileSelect(profile: UserProfile) {
    setSelectedProfile(profile);
    setSelectedFeatureLluitador(null);
    setSelectedFeatureEntrenador(null);
    setResult(null);
    setIsAnalyzing(false);
  }

  function handleFeatureSelectLluitador(feature: FeatureLluitador) {
    setSelectedFeatureLluitador(feature);
    setResult(null);
    setIsAnalyzing(false);
  }

  function handleFeatureSelectEntrenador(feature: FeatureEntrenador) {
    setSelectedFeatureEntrenador(feature);
    setResult(null);
    setIsAnalyzing(false);
  }

  function handleBackToProfiles() {
    setSelectedProfile(null);
    setSelectedFeatureLluitador(null);
    setSelectedFeatureEntrenador(null);
    setResult(null);
    setIsAnalyzing(false);
  }

  function handleBackToFeatures() {
    if (selectedProfile === "lluitador") {
      setSelectedFeatureLluitador(null);
    }

    if (selectedProfile === "entrenador") {
      setSelectedFeatureEntrenador(null);
    }

    setResult(null);
    setIsAnalyzing(false);
  }

  const currentFeature =
    selectedProfile === "lluitador"
      ? selectedFeatureLluitador
      : selectedFeatureEntrenador;

  return (
    <main className="app-shell">
      <section className="app-card">
        <div className="app-header">
          <h1 className="app-title">Analitzador de Grappling</h1>
          <p className="app-subtitle">
            Analitza combats de grappling segons el perfil i la funcionalitat seleccionada.
          </p>
        </div>

        {!selectedProfile && (
          <div className="selection-panel">
            <h2 className="section-title">Selecciona el teu perfil</h2>
            <p className="selection-text">Tria com vols utilitzar l’aplicació.</p>

            <div className="button-grid">
              <button
                type="button"
                className="selection-button"
                onClick={() => handleProfileSelect("lluitador")}
              >
                <span className="selection-button-title">Lluitador</span>
                <span className="selection-button-text">
                  Anàlisi orientada a millorar el teu rendiment i detectar errors.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleProfileSelect("entrenador")}
              >
                <span className="selection-button-title">Entrenador</span>
                <span className="selection-button-text">
                  Anàlisi pensada per estudiar patrons, tàctica i presa de decisions.
                </span>
              </button>
            </div>
          </div>
        )}

        {selectedProfile === "lluitador" && !selectedFeatureLluitador && (
          <div className="selection-panel">
            <button
              type="button"
              className="back-button"
              onClick={handleBackToProfiles}
            >
              ← Tornar a perfils
            </button>

            <h2 className="section-title">
              Funcionalitats per a:{" "}
              <span className="highlight-text">{selectedProfile}</span>
            </h2>

            <p className="selection-text">Escull què vols fer a continuació.</p>

            <div className="button-grid button-grid-features">
              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectLluitador("analysis")}
              >
                <span className="selection-button-title">Analitzar combat</span>
                <span className="selection-button-text">
                  Puja un vídeo i genera una anàlisi automàtica.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectLluitador("scouting")}
              >
                <span className="selection-button-title">Scouting d’oponent</span>
                <span className="selection-button-text">
                  Estudia un rival i detecta patrons, tendències i riscos.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectLluitador("evolution")}
              >
                <span className="selection-button-title">Veure evolució</span>
                <span className="selection-button-text">
                  Compara combats antics i recents per veure millores i aspectes pendents.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectLluitador("history")}
              >
                <span className="selection-button-title">Veure historial</span>
                <span className="selection-button-text">
                  Consulta els combats i anàlisis guardats.
                </span>
              </button>
            </div>
          </div>
        )}

        {selectedProfile === "entrenador" && !selectedFeatureEntrenador && (
          <div className="selection-panel">
            <button
              type="button"
              className="back-button"
              onClick={handleBackToProfiles}
            >
              ← Tornar a perfils
            </button>

            <h2 className="section-title">
              Funcionalitats per a:{" "}
              <span className="highlight-text">{selectedProfile}</span>
            </h2>

            <p className="selection-text">Escull què vols fer a continuació.</p>

            <div className="button-grid button-grid-features">
              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectEntrenador("analysis")}
              >
                <span className="selection-button-title">Analitzar combat</span>
                <span className="selection-button-text">
                  Puja un vídeo i genera una anàlisi automàtica orientada a entrenador.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectEntrenador("training_focus")}
              >
                <span className="selection-button-title">Focus d’entrenament</span>
                <span className="selection-button-text">
                  Detecta errors recurrents i identifica què cal entrenar més.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectEntrenador("scouting")}
              >
                <span className="selection-button-title">Scouting d’oponent</span>
                <span className="selection-button-text">
                  Analitza oponents per preparar estratègies específiques.
                </span>
              </button>

              <button
                type="button"
                className="selection-button"
                onClick={() => handleFeatureSelectEntrenador("athletes")}
              >
                <span className="selection-button-title">Esportistes</span>
                <span className="selection-button-text">
                  Consulta l’historial i els combats analitzats de cada atleta.
                </span>
              </button>
            </div>
          </div>
        )}

        {selectedProfile && currentFeature === "analysis" && (
          <div className="app-content">
            <div className="upload-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <div className="selected-profile-box">
                <span className="selected-profile-label">Perfil seleccionat</span>
                <span className="selected-profile-value">{selectedProfile}</span>
              </div>

              <UploadForm
                profile={selectedProfile}
                onStart={handleStart}
                onResult={handleResult}
              />
            </div>

            <div className="result-panel">
              {isAnalyzing && !result && (
                <div className="result-placeholder">
                  <h2>Analitzant combat...</h2>
                  <p>
                    El sistema està processant el vídeo i generant el resultat.
                  </p>
                </div>
              )}

              {!isAnalyzing && !result && (
                <div className="result-placeholder">
                  <h2>Encara no hi ha cap anàlisi</h2>
                  <p>Selecciona un vídeo i prem “Analitzar combat”.</p>
                </div>
              )}

              {result && <AnalysisResult result={result} />}
            </div>
          </div>
        )}

        {selectedProfile === "lluitador" &&
          selectedFeatureLluitador === "scouting" && (
            <div className="selection-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <h2 className="section-title">Scouting d’oponent</h2>
              <p className="selection-text">
                Aquesta funcionalitat encara no està implementada.
              </p>
            </div>
          )}

        {selectedProfile === "lluitador" &&
          selectedFeatureLluitador === "evolution" && (
            <div className="selection-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <h2 className="section-title">Evolució</h2>
              <p className="selection-text">
                Aquesta funcionalitat encara no està implementada.
              </p>
            </div>
          )}

        {selectedProfile === "lluitador" &&
          selectedFeatureLluitador === "history" && (
            <div className="selection-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <h2 className="section-title">Historial d’anàlisis</h2>
              <p className="selection-text">
                Aquesta funcionalitat encara no està implementada.
              </p>
            </div>
          )}

        {selectedProfile === "entrenador" &&
          selectedFeatureEntrenador === "training_focus" && (
            <div className="selection-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <h2 className="section-title">Focus d’entrenament</h2>
              <p className="selection-text">
                Aquesta funcionalitat encara no està implementada.
              </p>
            </div>
          )}

        {selectedProfile === "entrenador" &&
          selectedFeatureEntrenador === "scouting" && (
            <div className="selection-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <h2 className="section-title">Scouting d’oponent</h2>
              <p className="selection-text">
                Aquesta funcionalitat encara no està implementada.
              </p>
            </div>
          )}

        {selectedProfile === "entrenador" &&
          selectedFeatureEntrenador === "athletes" && (
            <div className="selection-panel">
              <button
                type="button"
                className="back-button"
                onClick={handleBackToFeatures}
              >
                ← Tornar a funcionalitats
              </button>

              <h2 className="section-title">Esportistes</h2>
              <p className="selection-text">
                Aquesta funcionalitat encara no està implementada.
              </p>
            </div>
          )}
      </section>
    </main>
  );
}

export default App;