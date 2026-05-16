import type { UserProfile } from "../types";

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
      text: "Puja un vídeo i analitza el combat complet o centra’t en un lluitador concret.",
    },
    {
      feature: "entrenador-training-focus",
      title: "Focus d’entrenament",
      text: "Detecta l’evolució real dels teus alumnes a partir de les seves dades.",
    },
    {
      feature: "entrenador-scouting",
      title: "Scouting d’oponent",
      text: "Puja diversos vídeos d’un rival i genera un informe tàctic per preparar el combat dels teus alumnes.",
    },
    {
      feature: "entrenador-athletes",
      title: "Historial esportistes",
      text: "Gestiona els anàlisis guardats, tant de combats generals com dels teus alumnes.",
    },
  ],
  lluitador: [
    {
      feature: "lluitador-analysis",
      title: "Analitzar combat",
      text: "Puja un vídeo i analitza el combat complet o centra’t en el teu propi rendiment.",
    },
    {
      feature: "lluitador-scouting",
      title: "Scouting d’oponent",
      text: "Puja vídeos del teu proper rival i rep una anàlisi clara dels seus punts forts, febleses i pla de combat recomanat.",
    },
    {
      feature: "lluitador-evolution",
      title: "Evolució",
      text: "Consulta la teva progressió a partir dels combats guardats: domini, defensa, accions clau, patrons recurrents i prioritats de millora.",
    },
    {
      feature: "lluitador-history",
      title: "Historial",
      text: "Consulta els teus anàlisis guardats i revisa combats anteriors amb detall.",
    },
  ],
} as const;

export default function MenuScreen({
  profile,
  onSelectFeature,
  onSelectProfile,
}: Props) {
  const otherProfile: UserProfile =
    profile === "lluitador" ? "entrenador" : "lluitador";

  return (
    <>
      <div className="profile-switcher profile-switcher-centered">
        <button
          type="button"
          className={`profile-big-button profile-tab ${
            profile === "lluitador" ? "profile-tab-active" : ""
          }`}
          onClick={() => onSelectProfile("lluitador")}
        >
          Lluitador
        </button>

        <button
          type="button"
          className={`profile-big-button profile-tab ${
            profile === "entrenador" ? "profile-tab-active" : ""
          }`}
          onClick={() => onSelectProfile("entrenador")}
        >
          Entrenador
        </button>
      </div>

      <div className="selection-panel">
        <h2 className="section-title">
          Funcionalitats per a:{" "}
          <span className="highlight-text">{profile}</span>
        </h2>

        {profile === "lluitador" && (
          <p className="selection-text">Escull què vols fer a continuació.</p>
        )}

        <div className="button-grid button-grid-features">
          {MENU_OPTIONS[profile].map((option) => (
            <button
              key={option.feature}
              type="button"
              className="selection-button"
              onClick={() => onSelectFeature(option.feature)}
            >
              <span className="selection-button-title">{option.title}</span>
              <span className="selection-button-text">{option.text}</span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
}