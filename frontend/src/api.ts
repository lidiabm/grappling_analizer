import type { AnalysisResponse, UserProfile } from "./types";

const API_URL = "http://localhost:8000";

export async function analyzeVideo(
  file: File,
  profile: UserProfile
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("video", file);
  formData.append("profile", profile);

  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.detail || "Error al analizar el vídeo");
  }

  return response.json();
}