export type UserProfile = "lluitador" | "entrenador";
export type OponentId = "oponent_1" | "oponent_2" | "desconegut";
export type Confianca = "alta" | "mitjana" | "baixa" | "insuficient";

export type AnalysisMode = "full_fight" | "single_athlete";

/* REQUEST */
export type AthleteIdentifierType =
  | "visual_description"
  | "screen_side"
  | "corner";

export type AthleteIdentifier = {
  type: AthleteIdentifierType;
  value: string;
};

export interface AnalysisRequest {
  profile: UserProfile;
  mode: AnalysisMode;
  athlete_identifier?: AthleteIdentifier;
}

/* COMBAT STRUCTURE */
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

export interface DebugRequest {
  profile?: string | null;
  mode?: string | null;
  athlete_identifier_type?: string | null;
  athlete_identifier_value?: string | null;
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

/* ANALYSIS CONTENT */
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

/* STATS */
export type Posicio =
  | "standing"
  | "closed_guard"
  | "open_guard"
  | "half_guard"
  | "side_control"
  | "mount"
  | "back_control"
  | "turtle"
  | "scramble"
  | "other";

export type Controlador = "oponent_1" | "oponent_2" | "desconegut";

export type TipusEvent =
  | "inici_intercanvi"
  | "control"
  | "transicio"
  | "intent_finalitzacio"
  | "intent_enderroc"
  | "guard_pull"
  | "escape"
  | "reversio"
  | "scramble"
  | "pausa"
  | "finalitzacio"
  | "avantatge_posicional"
  | "altre";

export type AccioTipus =
  | "intent_finalitzacio"
  | "intent_enderroc"
  | "guard_pull"
  | "reversio"
  | "escapada";

export interface TempsPerPosicio {
  posicio: Posicio;
  controlador: Controlador;
  segons: number;
  percentatge: number;
}

export interface AccioClau {
  temps: string;
  lluitador: "oponent_1" | "oponent_2";
  tipus: AccioTipus;
  detall: string;
  confianca: Confianca;
}

export interface AttemptCount {
  intents: number;
  reeixits: number;
}

export interface FighterAttemptCounter {
  oponent_1: AttemptCount;
  oponent_2: AttemptCount;
}

export interface ResumAccions {
  intents_finalitzacio: FighterAttemptCounter;
  intents_enderroc: FighterAttemptCounter;
  guard_pulls: Record<string, number>;
  reversions: Record<string, number>;
  escapades: Record<string, number>;
  canvis_control: number;
}

export interface EstadistiquesEstimades {
  duracio_total_segons: number;
  temps_per_posicio: TempsPerPosicio[];
  temps_dominant_total: Record<string, number>;
  accions_clau: AccioClau[];
  resum_accions: ResumAccions;
}

export interface EstadistiquesDerivades {
  duracio_total_segons: number;
  temps_per_posicio: TempsPerPosicio[];
  temps_dominant_total: Record<string, number>;
  accions_clau: AccioClau[];
  resum_accions: ResumAccions;
}

/* RESPONSES */
export interface FullFightAnalysisResponse {
  mode: "full_fight";
  selected_oponent_id: "desconegut";
  combat_info: CombatInfo;
  resum_partit: ResumPartit;
  timeline: TimelineEvent[];
  analisi_oponents: AnalisiOponents;
  estadistiques_estimades: EstadistiquesEstimades;
  estadistiques_derivades?: EstadistiquesDerivades;
  incerteses: string[];
  perfil: UserProfile;
  debug_request?: DebugRequest;
}

export interface SingleAthleteAnalysisResponse {
  mode: "single_athlete";
  selected_oponent_id: OponentId;
  combat_info: CombatInfo;
  resum_partit: ResumPartit;
  timeline: TimelineEvent[];
  analisi_lluitador: AnalisiOponent;
  estadistiques_estimades: EstadistiquesEstimades;
  incerteses: string[];
  perfil: UserProfile;
  debug_request?: DebugRequest;
}

export type AnalysisResponse =
  | FullFightAnalysisResponse
  | SingleAthleteAnalysisResponse;

/* STORAGE */
export type SavedAnalysis = {
  id: string;
  title: string;
  createdAt: string;
  fightId: string;
  profileType: UserProfile;
  studentFolder?: string;
  fightDate?: string;
  result: AnalysisResponse;
};

/* EVOLUTION / TRAINING FOCUS */
export type EvolutionMetric = {
  fightId: string;
  label: string;

  dominantTime: number;
  controlledTime: number;
  neutralTime: number;
  totalFightTime: number;

  dominantPct: number;
  controlledPct: number;
  neutralPct: number;

  submissionAttempts: number;
  takedownAttempts: number;
  guardPulls: number;
  reversals: number;
  escapes: number;
};

export type PositionTotal = {
  name: string;
  segons: number;
};

export type StudentFocus = {
  studentName: string;
  analysesCount: number;
  metrics: EvolutionMetric[];
  positionTotals: PositionTotal[];
  summary: {
    dominantChange: number;
    controlledChange: number;
    defensiveChange: number;
    submissionChange: number;
    evolutionText: string;
    mainFocus: string;
  };
};

export type TrainingFocusResponse = {
  studentsCount: number;
  analysesCount: number;
  recentCount: number;
  chartWeeks: number;
  focusWeeks: number;
  globalMetrics: EvolutionMetric[];
  globalPositionTotals: PositionTotal[];
  globalFocus: string[];
  students: StudentFocus[];
};

/* SCOUTING */
export interface ScoutingRivalInfo {
  nom_visible: string;
  descripcio_visual: string;
  nivell_confianca_global: Confianca;
}

export type InformeLluitadorScouting = {
  amenaces_principals: string[];
  debilitats_a_explotar: string[];
  que_evitar: string[];
  pla_combat: string[];
  consells_clau: string[];
  clau_tactica: string;
}; 

export interface InformeEntrenadorScouting {
  model_de_combat: string;
  patrons_ofensius: string[];
  patrons_defensius: string[];
  situacions_on_puntua: string[];
  situacions_on_queda_exposat: string[];
  pla_tactic_recomanat: string[];
  focus_entrenament: string[];
  exercicis_recomanats: string[];
  riscos_principals: string[];
}

export type ScoutingSeguimentRival = "clar" | "parcial" | "incert";

export interface ScoutingPerVideoStats {
  video: number | string;
  fitxer: string;
  seguiment_rival: ScoutingSeguimentRival;
  atacs_iniciats: number | "desconegut";
  atacs_efectius: number | "desconegut";
  intents_passada_guardia: number | "desconegut";
  passades_guardia_efectives: number | "desconegut";
  raspades_intentades: number | "desconegut";
  raspades_efectives: number | "desconegut";
  submissions_intentades: number | "desconegut";
  submissions_encaixades: number | "desconegut";
  recuperacions_guardia: number | "desconegut";
  perdues_posicio: number | "desconegut";
  temps_dominant_aproximat: string;
  situacions_mes_frequents: string[];
  observacions: string[];
}

export interface ScoutingGlobalStats {
  accions_mes_frequents: string[];
  situacions_mes_repetides: string[];
  zones_de_risc: string[];
  tendencies_tactiques: string[];
  patrons_amb_mes_evidencia: string[];
  patrons_amb_poca_evidencia: string[];
}

export interface ScoutingNumericProfile {
  pressio: number;
  agressivitat: number;
  control_posicional: number;
  defensa: number;
  perill_submissio: number;
  explosivitat: number;
  adaptabilitat: number;
}

export interface ScoutingStats {
  nota: string;
  nivell_fiabilitat_estadistica: Confianca;
  per_video: ScoutingPerVideoStats[];
  resum_global: ScoutingGlobalStats;
  perfil_numeric: ScoutingNumericProfile;
}

export type ScoutingChartDatum = {
  label: string;
  valor: number;
};

export type ScoutingChart = {
  id: string;
  tipus: "barres" | "radar" | string;
  titol: string;
  descripcio?: string | null;
  dades: ScoutingChartDatum[];
  escala?: string | null;
  interpretacio?: string | null;
};

export interface BaseScoutingResponse {
  mode: "scouting";
  perfil: UserProfile;
  analysis_type: "scouting_lluitador" | "scouting_entrenador";
  rival_info: ScoutingRivalInfo;
  resum_rival: string;
  patrons_recurrents: string[];
  punts_forts: string[];
  debilitats: string[];
  incerteses: string[];
}

export interface LluitadorScoutingResponse extends BaseScoutingResponse {
  perfil: "lluitador";
  analysis_type: "scouting_lluitador";
  informe_lluitador: InformeLluitadorScouting;
  informe_entrenador?: null;
  estadistiques?: null;
  grafics_suggerits?: null;
}

export interface EntrenadorScoutingResponse extends BaseScoutingResponse {
  perfil: "entrenador";
  analysis_type: "scouting_entrenador";
  informe_lluitador?: null;
  informe_entrenador: InformeEntrenadorScouting;
  estadistiques: ScoutingStats;
  grafics_suggerits: ScoutingChart[];
}

export type ScoutingResponse =
  | LluitadorScoutingResponse
  | EntrenadorScoutingResponse;

export type ScoutingVideoInput = {
  file: File;
  rivalDescription: string;
};

/* FIGHTER EVOLUTION */
export type FighterEvolutionMagnitude = "alta" | "mitjana" | "baixa";

export type FighterEvolutionRequest = {
  old_analysis: unknown;
  new_analysis: unknown;
};

export type FighterEvolutionInfo = {
  nom_visible: string;
  descripcio_visual: string;
  confianca_analisi: FighterEvolutionMagnitude;
};

export type FighterEvolutionStablePatterns = {
  fortaleses_consolidades: string[];
  debilitats_persistents: string[];
};

export type FighterEvolutionTactical = {
  model_antic: string;
  model_recent: string;
  canvi_observat: string;
  interpretacio: string;
};

export type FighterEvolutionTechnical = {
  tecniques_millorades: string[];
  tecniques_empitjorades: string[];
  tecniques_noves: string[];
  tecniques_abandonades: string[];
};

export type FighterEvolutionResponse = {
  mode: "evolucio";
  analysis_type: "evolucio_lluitador";
  fighter_info: FighterEvolutionInfo;
  resum_evolucio: string;
  magnitud_canvi_global: FighterEvolutionMagnitude;
  millores: string[];
  regressions: string[];
  patrons_estables: FighterEvolutionStablePatterns;
  evolucio_tactica: FighterEvolutionTactical;
  evolucio_tecnica: FighterEvolutionTechnical;
  conclusio: string;
  incerteses: string[];

  comparativa_numerica?: unknown;
  grafics_suggerits?: unknown[];
  recomanacions_entrenament?: {
    prioritat_alta: string[];
    prioritat_mitjana: string[];
    manteniment: string[];
  };
};