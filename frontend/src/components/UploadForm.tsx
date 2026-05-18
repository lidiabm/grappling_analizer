import { useRef, useState } from "react";
import type {
  AnalysisMode,
  AnalysisRequest,
  AnalysisResponse,
  AthleteIdentifierType,
  UserProfile,
} from "../types";
import { analyzeVideo } from "../api";
import "./UploadForm.css";

type Props = {
  profile: UserProfile;
  onStart: () => void;
  onResult: (result: AnalysisResponse) => void;
  onFileSelected: (fileName: string) => void;
};

const MAX_FILE_SIZE_MB = 100;

export default function UploadForm({
  profile,
  onStart,
  onResult,
  onFileSelected,
}: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [analysisMode, setAnalysisMode] =
    useState<AnalysisMode>("full_fight");

  const [identifierType, setIdentifierType] =
    useState<AthleteIdentifierType>("visual_description");

  const [athleteDescription, setAthleteDescription] = useState("");
  const [screenSide, setScreenSide] = useState("esquerra");
  const [corner, setCorner] = useState("vermella");

  const inputRef = useRef<HTMLInputElement | null>(null);

  function validateFile(selectedFile: File | null): string {
    if (!selectedFile) return "Selecciona un vídeo";

    if (!selectedFile.type.startsWith("video/")) {
      return "El fitxer seleccionat no és un vídeo vàlid";
    }

    if (selectedFile.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `El vídeo supera els ${MAX_FILE_SIZE_MB} MB`;
    }

    return "";
  }

  function validateAthleteTarget(): string {
    if (analysisMode !== "single_athlete") return "";

    if (
      identifierType === "visual_description" &&
      !athleteDescription.trim()
    ) {
      return "Descriu l’atleta que vols analitzar";
    }

    return "";
  }

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0] || null;
    setFile(selectedFile);

    if (selectedFile) {
      onFileSelected(selectedFile.name);
    }

    if (error) setError("");
  }

  function handleClearFile() {
    setFile(null);

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  function buildAnalysisRequest(): AnalysisRequest {
    if (analysisMode === "full_fight") {
      return {
        profile,
        mode: "full_fight",
      };
    }

    if (identifierType === "visual_description") {
      return {
        profile,
        mode: "single_athlete",
        athlete_identifier: {
          type: "visual_description",
          value: athleteDescription.trim(),
        },
      };
    }

    if (identifierType === "screen_side") {
      return {
        profile,
        mode: "single_athlete",
        athlete_identifier: {
          type: "screen_side",
          value: screenSide,
        },
      };
    }

    return {
      profile,
      mode: "single_athlete",
      athlete_identifier: {
        type: "corner",
        value: corner,
      },
    };
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    const fileError = validateFile(file);
    if (fileError) {
      setError(fileError);
      return;
    }

    const athleteError = validateAthleteTarget();
    if (athleteError) {
      setError(athleteError);
      return;
    }

    if (!file) {
      setError("Selecciona un vídeo");
      return;
    }

    try {
      setLoading(true);
      setError("");
      onStart();

      const request = buildAnalysisRequest();
      const result = await analyzeVideo(file, request);

      onResult(result);

      setFile(null);
      setAnalysisMode("full_fight");
      setIdentifierType("visual_description");
      setAthleteDescription("");
      setScreenSide("esquerra");
      setCorner("vermella");

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
      <div className="upload-form-group">
        <label htmlFor="video">Vídeo del combat</label>

        <label
          htmlFor="video"
          className={`upload-dropzone ${loading ? "upload-dropzone-disabled" : ""}`}
        >
          <span className="upload-dropzone-icon">＋</span>

          <span className="upload-dropzone-content">
            <strong>
              {file ? "Vídeo seleccionat" : "Selecciona un vídeo"}
            </strong>

            <small>
              {file
                ? file.name
                : `Format vídeo · màxim ${MAX_FILE_SIZE_MB} MB`}
            </small>
          </span>
        </label>

        <input
          ref={inputRef}
          id="video"
          type="file"
          accept="video/*"
          onChange={handleFileChange}
          disabled={loading}
          className="upload-hidden-input"
        />

        {file && (
          <div className="upload-file-preview">
            <div>
              <strong>{file.name}</strong>
              <span>{(file.size / 1024 / 1024).toFixed(1)} MB</span>
            </div>

            <button
              type="button"
              className="upload-file-clear"
              onClick={handleClearFile}
              disabled={loading}
            >
              Treure
            </button>
          </div>
        )}
      </div>

      <div className="upload-form-group">
        <label htmlFor="analysis-mode">Tipus d’anàlisi</label>

        <select
          id="analysis-mode"
          value={analysisMode}
          onChange={(event) =>
            setAnalysisMode(event.target.value as AnalysisMode)
          }
          disabled={loading}
        >
          <option value="full_fight">Combat complet</option>
          <option value="single_athlete">
            Anàlisi en profunditat d’un atleta
          </option>
        </select>
      </div>

      {analysisMode === "single_athlete" && (
        <div className="upload-target-box">
          <div className="upload-target-header">
            <span>Objectiu de l’anàlisi</span>
            <p>Indica quin atleta vols seguir durant el combat.</p>
          </div>

          <div className="upload-form-group">
            <label htmlFor="identifier-type">Com identificar l’atleta</label>

            <select
              id="identifier-type"
              value={identifierType}
              onChange={(event) =>
                setIdentifierType(event.target.value as AthleteIdentifierType)
              }
              disabled={loading}
            >
              <option value="visual_description">Descripció visual</option>
              <option value="screen_side">Costat de la pantalla</option>
              <option value="corner">Cantonada</option>
            </select>
          </div>

          {identifierType === "visual_description" && (
            <div className="upload-form-group">
              <label htmlFor="athlete-description">Descripció visual</label>

              <input
                id="athlete-description"
                type="text"
                value={athleteDescription}
                onChange={(event) => {
                  setAthleteDescription(event.target.value);
                  setError("");
                }}
                placeholder="Ex: pantaló vermell i samarreta negra"
                disabled={loading}
              />
            </div>
          )}

          {identifierType === "screen_side" && (
            <div className="upload-form-group">
              <label htmlFor="screen-side">Costat</label>

              <select
                id="screen-side"
                value={screenSide}
                onChange={(event) => setScreenSide(event.target.value)}
                disabled={loading}
              >
                <option value="esquerra">Esquerra</option>
                <option value="dreta">Dreta</option>
              </select>
            </div>
          )}

          {identifierType === "corner" && (
            <div className="upload-form-group">
              <label htmlFor="corner">Cantonada</label>

              <select
                id="corner"
                value={corner}
                onChange={(event) => setCorner(event.target.value)}
                disabled={loading}
              >
                <option value="vermella">Vermella</option>
                <option value="blava">Blava</option>
              </select>
            </div>
          )}
        </div>
      )}

      <button
        type="submit"
        className="primary-button upload-submit-button"
        disabled={loading || !file}
      >
        {loading
          ? "Analitzant..."
          : analysisMode === "single_athlete"
            ? "Analitzar atleta"
            : "Analitzar combat"}
      </button>

      {loading && (
        <div className="upload-info-box">
          <strong>Processant vídeo</strong>
          <p>
            Estem pujant el vídeo i generant l’anàlisi. Això pot tardar uns
            segons.
          </p>
        </div>
      )}

      {error && (
        <div className="upload-error-box" role="alert">
          <strong>No s’ha pogut completar l’anàlisi</strong>
          <p>{error}</p>
        </div>
      )}
    </form>
  );
}