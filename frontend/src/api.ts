import type {
  AnalysisRequest,
  AnalysisResponse,
  SavedAnalysis,
  TrainingFocusResponse,
  UserProfile,
  ScoutingResponse,
  ScoutingVideoInput,
  FighterEvolutionRequest,
  FighterEvolutionResponse,
} from "./types";

const API_BASE_URL = "http://localhost:8000";

type TrainingFocusOptions = {
  chartWeeks: number;
  focusWeeks: number;
};

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

export async function analyzeScoutingVideos(
  videos: ScoutingVideoInput[],
  profile: UserProfile
): Promise<ScoutingResponse> {
  const formData = new FormData();

  formData.append("profile", profile);

  videos.forEach((video) => {
    formData.append("videos", video.file);
  });

  formData.append(
    "video_descriptions",
    JSON.stringify(
      videos.map((video, index) => ({
        index,
        filename: video.file.name,
        rival_description: video.rivalDescription,
      }))
    )
  );

  const response = await fetch(`${API_BASE_URL}/scouting`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}

export async function calculateTrainingFocus(
  analyses: SavedAnalysis[],
  options: TrainingFocusOptions
): Promise<TrainingFocusResponse> {
  const response = await fetch(`${API_BASE_URL}/training-focus`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      analyses,
      chartWeeks: options.chartWeeks,
      focusWeeks: options.focusWeeks,
    }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}

export async function analyzeFighterEvolution(
  payload: FighterEvolutionRequest
): Promise<FighterEvolutionResponse> {
  const response = await fetch(`${API_BASE_URL}/fighter-evolution`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json();
}