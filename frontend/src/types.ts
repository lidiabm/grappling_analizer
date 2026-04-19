export type UserProfile = "lluitador" | "entrenador";

export type OponentId = "oponent_1" | "oponent_2" | "desconegut";
export type Confianca = "alta" | "mitjana" | "baixa";

export interface OponentInfo {
  id: "oponent_1" | "oponent_2";
  nom_visible: string;
  descripcio_visual: string;
}

export interface GuanyadorPerdedor {
  id: OponentId;
  descripcio: string;
}

export interface CombatInfo {
  oponents: OponentInfo[];
  durada_estimada: string;
  nivell_confianca_global: Confianca;
}

export interface ResumPartit {
  guanyador: GuanyadorPerdedor;
  perdedor: GuanyadorPerdedor;
  metode: string;
  tipus_submissio: string;
  resum_breu: string;
}

export interface TimelineEvent {
  inici: string;
  fi: string;
  posicio: string;
  controlador: string;
  tipus_event: string;
  descripcio: string;
  rellevancia: number;
  confianca: Confianca;
}

export interface ErrorDetallat {
  error: string;
  moment_aproximat: string;
  impacte: string;
}

export interface EncertClau {
  encert: string;
  moment_aproximat: string;
  impacte: string;
}

export interface MilloraRecomanada {
  millora: string;
  objectiu: string;
  benefici_esperat: string;
}

export interface AnalisiOponent {
  tactica_general: string;
  patrons_tactics: string[];
  fortaleses_clau: string[];
  debilitats_clau: string[];
  errors_detallats: ErrorDetallat[];
  encerts_clau: EncertClau[];
  sequencies_repetides: string[];
  millores_recomanades: MilloraRecomanada[];
}

export interface AnalisiOponents {
  oponent_1: AnalisiOponent;
  oponent_2: AnalisiOponent;
}

export interface TempsPerPosicio {
  lluitador: string;
  posicio: string;
  segons: number;
  dominant: boolean;
}

export interface EstadistiquesEstimades {
  temps_per_posicio: TempsPerPosicio[];
  canvis_control: number;
  intents_finalitzacio: number;
  intents_enderroc: number;
  guard_pulls: number;
}

export interface EstadistiquesDerivades {
  temps_per_posicio: TempsPerPosicio[];
  temps_dominant_per_lluitador: Record<string, number>;
  canvis_control_recalculats: number;
}

export interface PatronsGlobals {
  dinamiques_clau: string[];
  moments_decisius: string[];
  resum_comparable: string[];
}

export interface AnalysisResponse {
  combat_info: CombatInfo;
  resum_partit: ResumPartit;
  timeline: TimelineEvent[];
  analisi_oponents: AnalisiOponents;
  estadistiques_estimades: EstadistiquesEstimades;
  estadistiques_derivades?: EstadistiquesDerivades;
  patrons_globals: PatronsGlobals;
  incerteses: string[];
  perfil: UserProfile;
}