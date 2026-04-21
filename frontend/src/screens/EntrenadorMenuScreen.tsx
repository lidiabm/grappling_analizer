import type { UserProfile } from "../types";

type Props = {
  onSelectFeature: (
    feature:
      | "entrenador-analysis"
      | "entrenador-training_focus"
      | "entrenador-scouting"
      | "entrenador-athletes"
  ) => void;
  onSelectProfile: (profile: UserProfile) => void;
};

function EntrenadorMenuScreen({ onSelectFeature, onSelectProfile }: Props) {
  return (
    <>
      <div className="profile-switcher profile-switcher-centered">
        <button
          type="button"
          className="profile-big-button profile-tab"
          onClick={() => onSelectProfile("lluitador")}
        >
          Lluitador
        </button>

        <button
          type="button"
          className="profile-big-button profile-tab profile-tab-active"
        >
          Entrenador
        </button>
      </div>

      <div className="selection-panel">
        <h2 className="section-title">
          Funcionalitats per a:{" "}
          <span className="highlight-text">entrenador</span>
        </h2>

        <div className="button-grid button-grid-features">
          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("entrenador-analysis")}
          >
            Analitzar combat
          </button>

          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("entrenador-training_focus")}
          >
            Focus d’entrenament
          </button>

          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("entrenador-scouting")}
          >
            Scouting
          </button>

          <button
            type="button"
            className="selection-button"
            onClick={() => onSelectFeature("entrenador-athletes")}
          >
            Esportistes
          </button>
        </div>
      </div>
    </>
  );
}

export default EntrenadorMenuScreen;