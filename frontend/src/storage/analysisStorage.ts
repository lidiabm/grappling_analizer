import type { SavedAnalysis } from "../types";

const STORAGE_KEY = "savedAnalyses";

function formatStudentName(name: string) {
  return name
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatAnalysisTitle(title: string) {
  const trimmed = title.trim();

  if (!trimmed) return "";

  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}

function normalizeText(text: string) {
  return text.trim().toLowerCase();
}

export function analysisTitleExists(title: string) {
  const normalizedTitle = normalizeText(title);

  return getSavedAnalyses().some(
    (analysis) => normalizeText(analysis.title) === normalizedTitle
  );
}

export function saveAnalysis(analysis: SavedAnalysis) {
  const current = getSavedAnalyses();

  const normalizedAnalysis: SavedAnalysis = {
    ...analysis,
    title: formatAnalysisTitle(analysis.title),
    studentFolder: analysis.studentFolder
      ? formatStudentName(analysis.studentFolder)
      : undefined,
  };

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify([normalizedAnalysis, ...current])
  );
}

export function getSavedAnalyses(): SavedAnalysis[] {
  const raw = localStorage.getItem(STORAGE_KEY);

  if (!raw) return [];

  try {
    const analyses: SavedAnalysis[] = JSON.parse(raw);

    return analyses.sort((a, b) => {
      const dateA = a.fightDate || a.createdAt;
      const dateB = b.fightDate || b.createdAt;

      return new Date(dateB).getTime() - new Date(dateA).getTime();
    });
  } catch {
    return [];
  }
}

export function deleteAnalysis(id: string) {
  const current = getSavedAnalyses();
  const updated = current.filter((analysis) => analysis.id !== id);

  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}

export function clearSavedAnalyses() {
  localStorage.removeItem(STORAGE_KEY);
}