import { useState } from "react";
import type { AnalysisResponse, UserProfile } from "../types";
import { analyzeVideo } from "../api";

type Props = {
  onResult: (result: AnalysisResponse) => void;
};

export default function UploadForm({ onResult }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState<UserProfile>("lluitador");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Selecciona un vídeo");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const result = await analyzeVideo(file, profile);
      onResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
    } finally {
      setLoading(false);
    }
  }

  return (
  <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
    <div>
      <label>Vídeo del combat</label>
      <input
        type="file"
        accept="video/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
    </div>

    <div>
      <label>Perfil</label>
      <select
        value={profile}
        onChange={(e) => setProfile(e.target.value as UserProfile)}
      >
        <option value="lluitador">Lluitador</option>
        <option value="entrenador">Entrenador</option>
      </select>
    </div>

    <button type="submit" disabled={loading}>
      {loading ? "Analitzant..." : "Analitzar combat"}
    </button>

    {error && <p style={{ color: "crimson" }}>{error}</p>}
  </form>
);
}