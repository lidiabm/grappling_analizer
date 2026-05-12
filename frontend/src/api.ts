import type {
  AnalysisRequest,
  AnalysisResponse,
  SavedAnalysis,
  TrainingFocusResponse,
} from "./types";

const API_BASE_URL = "http://localhost:8000";

async function getErrorMessage(response: Response) {
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

  return errorMessage;
}

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
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}

export async function calculateTrainingFocus(
  analyses: SavedAnalysis[]
): Promise<TrainingFocusResponse> {
  const response = await fetch(`${API_BASE_URL}/training-focus`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      analyses,
    }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}