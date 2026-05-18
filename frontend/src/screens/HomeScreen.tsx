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
          Analitza combats.
          <br />
          Millora decisions.
        </h1>

        <p className="home-subtitle">
          Plataforma d’anàlisi de combats i scouting orientada a lluitadors i
          entrenadors de grappling.
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
              Analitza el teu rendiment, estudia rivals i revisa la teva
              evolució tècnica.
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
              Gestiona esportistes, prepara combats i genera informes tàctics.
            </p>
          </div>
        </button>
      </div>
    </section>
  );
}

export default HomeScreen;