export type UserProfile = "lluitador" | "entrenador";

export interface AnalysisResponse {
  resum: string;
  moments_clau: string[];
  observacions_tecniques: string[];
  recomanacions: string[];
  perfil: UserProfile; 
}