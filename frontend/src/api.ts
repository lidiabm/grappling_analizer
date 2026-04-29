import type { AnalysisRequest, AnalysisResponse } from "./types";

const API_BASE_URL = "http://localhost:8000";

export async function analyzeVideo(
  file: File,
  request: AnalysisRequest
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("video", file);
  formData.append("profile", request.profile);
  formData.append("mode", request.mode);

  if (request.athlete_identifier) {
    formData.append(
      "athlete_identifier_type",
      request.athlete_identifier.type
    );
    formData.append(
      "athlete_identifier_value",
      request.athlete_identifier.value
    );
  }

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = `Error ${response.status}`;

    try {
      const errorData = await response.json();
      errorMessage =
        errorData?.detail ||
        errorData?.error ||
        errorData?.message ||
        errorMessage;
    } catch {
      try {
        const rawText = await response.text();
        if (rawText) {
          errorMessage = rawText;
        }
      } catch {
        // no-op
      }
    }

    throw new Error(errorMessage);
  }

  return response.json();
}