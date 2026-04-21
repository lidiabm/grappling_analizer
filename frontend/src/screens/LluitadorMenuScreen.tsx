import type { UserProfile } from "../types";

type Props = {
  onSelectFeature: (
    feature:
      | "lluitador-analysis"
      | "lluitador-scouting"
      | "lluitador-evolution"
      | "lluitador-history"
  ) => void;
  onSelectProfile: (profile: UserProfile) => void;
};

function LluitadorMenuScreen({ onSelectFeature, onSelectProfile }: Props) {
  return (
    <>
      <div className="profile-switcher profile-switcher-centered">
        <button
          type="button"
          className="profile-big-button profile-tab profile-tab-active"
        >
          Lluitador
        </button>

        <button
          type="button"
          className="profile-big-button profile-tab"
          onClick={() => onSelectProfile("entrenador")}
        >
          Entrenador
        </button>
      </div>

      <div className="selection-panel">
        <h2 className="section-title">
          Funcionalitats per a:{" "}
          <span className="highlight-text">lluitador</span>
        </h2>

        <p className="selection-text">Escull què vols fer a continuació.</p>

        <div className="button-grid button-grid-features">
          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("lluitador-analysis")}
          >
            <span className="selection-button-title">Analitzar combat</span>
            <span className="selection-button-text">
              Puja un vídeo i genera una anàlisi automàtica.
            </span>
          </button>

          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("lluitador-scouting")}
          >
            <span className="selection-button-title">Scouting d’oponent</span>
          </button>

          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("lluitador-evolution")}
          >
            <span className="selection-button-title">Evolució</span>
          </button>

          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("lluitador-history")}
          >
            <span className="selection-button-title">Historial</span>
          </button>
        </div>
      </div>
    </>
  );
}

export default LluitadorMenuScreen;