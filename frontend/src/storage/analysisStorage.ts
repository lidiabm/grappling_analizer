import type { SavedAnalysis } from "../types";

const STORAGE_KEY = "savedAnalyses";

export function saveAnalysis(analysis: SavedAnalysis) {
  const current = getSavedAnalyses();

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify([analysis, ...current])
  );
}

export function getSavedAnalyses(): SavedAnalysis[] {
  const raw = localStorage.getItem(STORAGE_KEY);

  if (!raw) return [];

  try {
    return JSON.parse(raw);
  } catch {
    return [];
  }
}