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
      title: "Anàlisi de combat",
      text: "Analitza un combat complet o centra’t en el rendiment d’un alumne concret.",
    },
    {
      feature: "entrenador-training-focus",
      title: "Focus d’entrenament",
      text: "Visualitza mètriques i patrons d’evolució per detectar prioritats tècniques d’entrenament.",
    },
    {
      feature: "entrenador-scouting",
      title: "Scouting d’oponent",
      text: "Estudia diversos vídeos d’un oponent i genera informació tàctica per preparar el combat.",
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
      title: "Anàlisi de combat",
      text: "Analitza combats complets o els teus propis combats amb detall tècnic i tàctic. ",
    },
    {
      feature: "lluitador-scouting",
      title: "Scouting d’oponent",
      text: "Carrega diversos vídeos del teu rival i prepara una estratègia de combat més precisa.",
    },
    {
      feature: "lluitador-evolution",
      title: "Evolució",
      text: "Compara dos combats guardats i identifica la teva progressió i els canvis en el teu rendiment tècnic i tàctic.",
    },
    {
      feature: "lluitador-history",
      title: "Historial",
      text: "Consulta els teus anàlisis guardats i recupera combats anteriors quan ho necessitis.",
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
            </button>

            <button
            type="button"
            className={`menu-profile-tab ${
                profile === "entrenador" ? "menu-profile-tab-active" : ""
            }`}
            onClick={() => onSelectProfile("entrenador")}
            >
            <span>Entrenador</span>
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