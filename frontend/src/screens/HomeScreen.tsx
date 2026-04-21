import type { UserProfile } from "../types";

type Props = {
  onSelectProfile: (profile: UserProfile) => void;
};

function HomeScreen({ onSelectProfile }: Props) {
  return (
    <div className="selection-panel selection-panel-centered">
      <h2 className="section-title">Selecciona el teu perfil</h2>
      <p className="selection-text">
        Tria un perfil al menú superior per començar.
      </p>

      <div className="profile-big-buttons">
        <button
          type="button"
          className="profile-big-button"
          onClick={() => onSelectProfile("lluitador")}
        >
          Lluitador
        </button>

        <button
          type="button"
          className="profile-big-button"
          onClick={() => onSelectProfile("entrenador")}
        >
          Entrenador
        </button>
      </div>
    </div>
  );
}

export default HomeScreen;