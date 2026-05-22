import type { UserProfile } from "../types";
import "./HomeScreen.css";

type Props = {
  onSelectProfile: (profile: UserProfile) => void;
};

function HomeScreen({ onSelectProfile }: Props) {
  return (
    <section className="home-screen">
      <div className="home-hero">
        <span className="home-eyebrow">Grappling Analyzer</span>

        <h1 className="home-title">
          Analitza. Entén. Evoluciona.
        </h1>

        <p className="home-subtitle">
          Plataforma d’anàlisi de combats i scouting orientada a la millora tècnica i tàctica en grappling.
        </p>
      </div>

      <div className="home-profile-grid">
        <button
          type="button"
          className="home-profile-card"
          onClick={() => onSelectProfile("lluitador")}
        >
          <div className="home-profile-content">
            <span className="home-profile-label">Perfil</span>

            <h2>Lluitador</h2>

            <p>
              Analitza els teus combats, estudia la teva evolució i prepara millor cada rival.
            </p>
          </div>
        </button>

        <button
          type="button"
          className="home-profile-card"
          onClick={() => onSelectProfile("entrenador")}
        >
          <div className="home-profile-content">
            <span className="home-profile-label">Perfil</span>

            <h2>Entrenador</h2>

            <p>
              Analitza els combats i el rendiment dels teus alumnes, detecta focus d’entrenament i genera scouting tàctic dels rivals.
            </p>
          </div>
        </button>
      </div>
    </section>
  );
}

export default HomeScreen;