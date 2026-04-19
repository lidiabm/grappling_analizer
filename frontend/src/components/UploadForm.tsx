import { useRef, useState } from "react";
import type { AnalysisResponse, UserProfile } from "../types";
import { analyzeVideo } from "../api";
import "./UploadForm.css";

type Props = {
  profile: UserProfile;
  onStart: () => void;
  onResult: (result: AnalysisResponse) => void;
};

const MAX_FILE_SIZE_MB = 100;

export default function UploadForm({ profile, onStart, onResult }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);

  function validateFile(selectedFile: File | null): string {
    if (!selectedFile) {
      return "Selecciona un vídeo";
    }

    if (!selectedFile.type.startsWith("video/")) {
      return "El fitxer seleccionat no és un vídeo vàlid";
    }

    if (selectedFile.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `El vídeo supera els ${MAX_FILE_SIZE_MB} MB`;
    }

    return "";
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const selectedFile = e.target.files?.[0] || null;
    setFile(selectedFile);

    if (error) {
      setError("");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setLoading(true);
      setError("");
      onStart();

      const result = await analyzeVideo(file as File, profile);
      onResult(result);

      setFile(null);

      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperat");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <div className="form-group">
        <label htmlFor="video">Vídeo del combat</label>
        <input
          ref={inputRef}
          id="video"
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          disabled={loading}
        />
        {file && <span className="file-name">{file.name}</span>}
      </div>

      <button type="submit" disabled={loading || !file}>
        {loading ? "Analitzant..." : "Analitzar combat"}
      </button>

      {loading && (
        <div className="info-box">
          <p className="info-text">
            Estem pujant el vídeo i generant l’anàlisi. Això pot tardar uns segons.
          </p>
        </div>
      )}

      {error && (
        <div className="error-box" role="alert">
          <strong>No s’ha pogut completar l’anàlisi</strong>
          <p className="error-text">{error}</p>
        </div>
      )}
    </form>
  );
}