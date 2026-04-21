import { useState } from "react";
import type { AnalysisResponse, UserProfile } from "./types";
import UploadForm from "./components/UploadForm";
import AnalysisResult from "./components/AnalysisResult";
import "./App.css";
import Header from "./components/Header";

type FeatureLluitador = | "analysis" | "scouting" | "history" | "evolution" | null;
type FeatureEntrenador = | "analysis" | "training_focus" | "scouting" | "athletes" | null;

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

  return (
    <>
      <Header onGoHome={handleBackToProfiles} />

      <main className="app-shell">
        <section className="app-card">

          {/* MENU DE PERFIL */}
          {selectedProfile && (
            <div className="profile-switcher profile-switcher-centered">
              <button
                type="button"
                className={`profile-big-button profile-tab ${
                  selectedProfile === "lluitador" ? "profile-tab-active" : ""
                }`}
                onClick={() => handleProfileSelect("lluitador")}
              >
                Lluitador
              </button>

              <button
                type="button"
                className={`profile-big-button profile-tab ${
                  selectedProfile === "entrenador" ? "profile-tab-active" : ""
                }`}
                onClick={() => handleProfileSelect("entrenador")}
              >
                Entrenador
              </button>
            </div>
          )}

          {/* SENSE PERFIL */}
          {!selectedProfile && (
            <div className="selection-panel selection-panel-centered">
              <h2 className="section-title">Selecciona el teu perfil</h2>
              <p className="selection-text">
                Tria un perfil al menú superior per començar.
              </p>

              <div className="profile-big-buttons">
                <button
                  type="button"
                  className="profile-big-button"
                  onClick={() => handleProfileSelect("lluitador")}
                >
                  Lluitador
                </button>

                <button
                  type="button"
                  className="profile-big-button"
                  onClick={() => handleProfileSelect("entrenador")}
                >
                  Entrenador
                </button>
              </div>
            </div>
          )}

          {/* LLUITADOR */}
          {selectedProfile === "lluitador" && (
            <>
              <div className="selection-panel">
                <h2 className="section-title">
                  Funcionalitats per a:{" "}
                  <span className="highlight-text">lluitador</span>
                </h2>

                <p className="selection-text">
                  Escull què vols fer a continuació.
                </p>

                <div className="button-grid button-grid-features">
                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureLluitador === "analysis"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectLluitador("analysis")
                    }
                  >
                    <span className="selection-button-title">
                      Analitzar combat
                    </span>
                    <span className="selection-button-text">
                      Puja un vídeo i genera una anàlisi automàtica.
                    </span>
                  </button>

                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureLluitador === "scouting"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectLluitador("scouting")
                    }
                  >
                    <span className="selection-button-title">
                      Scouting d’oponent
                    </span>
                  </button>

                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureLluitador === "evolution"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectLluitador("evolution")
                    }
                  >
                    <span className="selection-button-title">
                      Evolució
                    </span>
                  </button>

                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureLluitador === "history"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectLluitador("history")
                    }
                  >
                    <span className="selection-button-title">
                      Historial
                    </span>
                  </button>
                </div>
              </div>

              {/* CONTENIDO LLUITADOR */}
              {selectedFeatureLluitador === "analysis" && (
                <div className="app-content">
                  <div className="upload-panel">
                    <UploadForm
                      profile="lluitador"
                      onStart={handleStart}
                      onResult={handleResult}
                    />
                  </div>

                  <div className="result-panel">
                    {isAnalyzing && !result && (
                      <div className="result-placeholder">
                        <h2>Analitzant combat...</h2>
                      </div>
                    )}

                    {!isAnalyzing && !result && (
                      <div className="result-placeholder">
                        <h2>Encara no hi ha cap anàlisi</h2>
                      </div>
                    )}

                    {result && <AnalysisResult result={result} />}
                  </div>
                </div>
              )}

              {selectedFeatureLluitador !== "analysis" &&
                selectedFeatureLluitador && (
                  <div className="selection-panel">
                    <h2 className="section-title">
                      Funcionalitat en desenvolupament
                    </h2>
                  </div>
                )}
            </>
          )}

          {/* ENTRENADOR */}
          {selectedProfile === "entrenador" && (
            <>
              <div className="selection-panel">
                <h2 className="section-title">
                  Funcionalitats per a:{" "}
                  <span className="highlight-text">entrenador</span>
                </h2>

                <div className="button-grid button-grid-features">
                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureEntrenador === "analysis"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectEntrenador("analysis")
                    }
                  >
                    Analitzar combat
                  </button>

                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureEntrenador === "training_focus"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectEntrenador("training_focus")
                    }
                  >
                    Focus d’entrenament
                  </button>

                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureEntrenador === "scouting"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectEntrenador("scouting")
                    }
                  >
                    Scouting
                  </button>

                  <button
                    type="button"
                    className={`selection-button ${
                      selectedFeatureEntrenador === "athletes"
                        ? "selection-button-active"
                        : ""
                    }`}
                    onClick={() =>
                      handleFeatureSelectEntrenador("athletes")
                    }
                  >
                    Esportistes
                  </button>
                </div>
              </div>

              {/* CONTENIDO ENTRENADOR */}
              {selectedFeatureEntrenador === "analysis" && (
                <div className="app-content">
                  <UploadForm
                    profile="entrenador"
                    onStart={handleStart}
                    onResult={handleResult}
                  />
                </div>
              )}

              {selectedFeatureEntrenador &&
                selectedFeatureEntrenador !== "analysis" && (
                  <div className="selection-panel">
                    <h2 className="section-title">
                      Funcionalitat en desenvolupament
                    </h2>
                  </div>
                )}
            </>
          )}

        </section>
      </main>
    </>
  );
}

export default App;