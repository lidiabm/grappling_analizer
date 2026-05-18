import type { UserProfile } from "../types";
import "./MenuScreen.css";

type Feature =
  | "entrenador-analysis"
  | "entrenador-training-focus"
  | "entrenador-scouting"
  | "entrenador-athletes"
  | "lluitador-analysis"
  | "lluitador-scouting"
  | "lluitador-evolution"
  | "lluitador-history";

type Props = {
  profile: UserProfile;
  onSelectFeature: (feature: Feature) => void;
  onSelectProfile: (profile: UserProfile) => void;
};

const MENU_OPTIONS = {
  entrenador: [
    {
      feature: "entrenador-analysis",
      title: "Analitzar combat",
      text: "Analitza un combat complet o centra’t en el rendiment d’un alumne concret.",
    },
    {
      feature: "entrenador-training-focus",
      title: "Focus d’entrenament",
      text: "Detecta patrons d’evolució i prioritats tècniques per planificar millor les sessions.",
    },
    {
      feature: "entrenador-scouting",
      title: "Scouting d’oponent",
      text: "Genera un informe tàctic del rival a partir de diversos vídeos de combat.",
    },
    {
      feature: "entrenador-athletes",
      title: "Historial esportistes",
      text: "Consulta i gestiona els anàlisis guardats dels teus alumnes.",
    },
  ],
  lluitador: [
    {
      feature: "lluitador-analysis",
      title: "Analitzar combat",
      text: "Analitza el teu combat i identifica punts forts, errors i accions de millora.",
    },
    {
      feature: "lluitador-scouting",
      title: "Scouting d’oponent",
      text: "Estudia el teu proper rival i prepara un pla de combat més precís.",
    },
    {
      feature: "lluitador-evolution",
      title: "Evolució",
      text: "Revisa la teva progressió en domini, defensa, accions clau i patrons recurrents.",
    },
    {
      feature: "lluitador-history",
      title: "Historial",
      text: "Consulta els teus anàlisis guardats i revisa combats anteriors.",
    },
  ],
} as const;

export default function MenuScreen({
  profile,
  onSelectFeature,
  onSelectProfile,
}: Props) {
  const isFighter = profile === "lluitador";

  return (
    <section className="menu-screen app-content">
        <header className="menu-header">
            <span className="menu-eyebrow">Grappling Analyzer</span>
        </header>

        <div className="menu-profile-switcher">
            <button
            type="button"
            className={`menu-profile-tab ${
                profile === "lluitador" ? "menu-profile-tab-active" : ""
            }`}
            onClick={() => onSelectProfile("lluitador")}
            >
            <span>Lluitador</span>
            <small>Rendiment personal</small>
            </button>

            <button
            type="button"
            className={`menu-profile-tab ${
                profile === "entrenador" ? "menu-profile-tab-active" : ""
            }`}
            onClick={() => onSelectProfile("entrenador")}
            >
            <span>Entrenador</span>
            <small>Gestió d’alumnes</small>
            </button>
        </div>

        <div className="menu-description">
            <p className="menu-subtitle">
            {isFighter
                ? "Analitza el teu rendiment, estudia rivals i revisa la teva evolució tècnica."
                : "Gestiona anàlisis, prepara entrenaments i obtén informació tàctica dels teus esportistes."}
            </p>
        </div>

        <div className="menu-feature-grid">
            {MENU_OPTIONS[profile].map((option) => (
            <button
                key={option.feature}
                type="button"
                className="menu-feature-card"
                onClick={() => onSelectFeature(option.feature)}
            >
                <span className="menu-feature-title">{option.title}</span>
                <span className="menu-feature-text">{option.text}</span>
                <span className="menu-feature-link">Obrir →</span>
            </button>
            ))}
        </div>
        </section>
  );
}