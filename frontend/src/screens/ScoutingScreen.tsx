import { useRef, useState } from "react";
import { analyzeScoutingVideos } from "../api";
import type { ScoutingResponse, ScoutingVideoInput } from "../types";
import "./ScoutingScreen.css";
import ScoutingCharts from "../components/charts/ScoutingCharts";
import ArrowLeftIcon from "../icons/ArrowLeftIcon";

type Props = {
  profile: "entrenador" | "lluitador";
  onBack: () => void;
};

function ScoutingScreen({ profile, onBack }: Props) {
  const isCoach = profile === "entrenador";
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentDescription, setCurrentDescription] = useState("");
  const [videos, setVideos] = useState<ScoutingVideoInput[]>([]);

  const [result, setResult] = useState<ScoutingResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function getVideoKey(video: ScoutingVideoInput) {
    return `${video.file.name}-${video.file.size}-${video.file.lastModified}`;
  }

  function formatFileSize(size: number) {
    return `${(size / 1024 / 1024).toFixed(1)} MB`;
  }

  function handleAddVideoToList() {
    if (!selectedFile) {
      setError("Has de seleccionar un vídeo abans d’afegir-lo.");
      return;
    }

    if (!currentDescription.trim()) {
      setError("Has de descriure quin és el rival en aquest vídeo.");
      return;
    }

    const selectedKey = `${selectedFile.name}-${selectedFile.size}-${selectedFile.lastModified}`;
    const alreadyExists = videos.some(
      (video) => getVideoKey(video) === selectedKey
    );

    if (alreadyExists) {
      setError("Aquest vídeo ja està afegit a la llista.");
      return;
    }

    setVideos((currentVideos) => [
      ...currentVideos,
      {
        file: selectedFile,
        rivalDescription: currentDescription.trim(),
      },
    ]);

    setSelectedFile(null);
    setCurrentDescription("");
    setResult(null);
    setError(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function removeVideo(index: number) {
    setVideos((currentVideos) =>
      currentVideos.filter((_, currentIndex) => currentIndex !== index)
    );

    setResult(null);
    setError(null);
  }

  async function handleGenerateScouting() {
    if (videos.length === 0) {
      setError("Has d’afegir almenys un vídeo a la llista.");
      return;
    }

    try {
      setError(null);
      setResult(null);
      setIsAnalyzing(true);

      const scoutingResult = await analyzeScoutingVideos(videos, profile);

      setResult(scoutingResult);
      setVideos([]);
      setSelectedFile(null);
      setCurrentDescription("");

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error inesperat generant el scouting."
      );
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <section className="scouting-page">
      <button
        type="button"
        className="scouting-back-button"
        onClick={onBack}
      >
        <ArrowLeftIcon size={18} />
      </button>

      <header className="scouting-hero">
        <div>
          <span className="scouting-kicker">Scouting d’oponent</span>

          <h2>
            Informe tàctic per a{" "}
            <span>{isCoach ? "entrenador" : "lluitador"}</span>
          </h2>

          <p>
            {isCoach
              ? "Afegeix combats d’un rival per detectar patrons, punts forts i debilitats, i generar recomanacions tàctiques i exercicis per preparar els teus alumnes."
              : "Afegeix vídeos del teu rival per identificar patrons repetits, amenaces principals i oportunitats concretes per construir el teu pla de combat."}
          </p>
        </div>

        <div className="scouting-hero-badge">
          <strong>{videos.length}</strong>
          <small>vídeos afegits</small>
        </div>
      </header>

      <div className="scouting-grid">
        <section className="scouting-card scouting-card-main">
          <div className="scouting-card-header">
            <div>
              <h3>Afegir vídeo</h3>
              <p>Selecciona un vídeo, descriu el rival i afegeix-lo a la llista.</p>
            </div>

          </div>

          <label className="scouting-upload">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              hidden
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                setSelectedFile(file);
                setResult(null);
                setError(null);
              }}
            />

            <span className="scouting-upload-icon">＋</span>

            <span>
              <strong>Seleccionar vídeo</strong>
              <small>Format vídeo · un combat cada vegada</small>
            </span>
          </label>

          {selectedFile && (
            <div className="scouting-selected-file">
              <div>
                <strong>{selectedFile.name}</strong>
                <span>{formatFileSize(selectedFile.size)}</span>
              </div>

              <button
                type="button"
                onClick={() => {
                  setSelectedFile(null);

                  if (fileInputRef.current) {
                    fileInputRef.current.value = "";
                  }
                }}
              >
                Canviar
              </button>
            </div>
          )}

          <label className="scouting-label" htmlFor="rival-description">
            Descripció del rival en aquest vídeo
          </label>

          <textarea
            id="rival-description"
            className="scouting-textarea"
            placeholder="Ex: és el lluitador amb rashguard negre, comença a l’esquerra, porta cinturó blau..."
            value={currentDescription}
            rows={4}
            onChange={(event) => {
              setCurrentDescription(event.target.value);
              setError(null);
            }}
          />

          <button
            type="button"
            className="scouting-secondary-button"
            onClick={handleAddVideoToList}
            disabled={isAnalyzing}
          >
            Afegir vídeo a la llista
          </button>
        </section>

        <aside className="scouting-card scouting-info-card">
          <div className="scouting-card-header">
            <div>
              <h3>Què analitzarà?</h3>
              <p>
                {isCoach
                  ? "La IA generarà informació útil per planificar la preparació dels teus esportistes."
                  : "La IA generarà informació pràctica per ajudar-te a competir contra aquest rival."}
              </p>
            </div>
          </div>

          <ul className="scouting-check-list">
            {isCoach ? (
              <>
                <li>Patrons ofensius i defensius del rival.</li>
                <li>Situacions on el rival genera més perill.</li>
                <li>Debilitats explotables pels teus alumnes.</li>
                <li>Pla tàctic, focus d’entrenament i exercicis recomanats.</li>
              </>
            ) : (
              <>
                <li>Punts forts i amenaces principals del rival.</li>
                <li>Accions que repeteix amb més freqüència.</li>
                <li>Errors o moments on es pot atacar.</li>
                <li>Pla de combat resumit amb què fer i què evitar.</li>
              </>
            )}
          </ul>
        </aside>
      </div>

      {videos.length > 0 && (
        <section className="scouting-card">
          <div className="scouting-card-header">
            <div>
              <h3>Vídeos afegits al scouting</h3>
            </div>
          </div>

          <div className="scouting-video-list">
            {videos.map((video, index) => (
              <article key={getVideoKey(video)} className="scouting-video-item">
                <div className="scouting-video-number">{index + 1}</div>

                <div className="scouting-video-content">
                  <strong>{video.file.name}</strong>
                  <span>{formatFileSize(video.file.size)}</span>
                  <p>{video.rivalDescription}</p>
                </div>

                <button
                  type="button"
                  className="scouting-remove-button"
                  onClick={() => removeVideo(index)}
                  disabled={isAnalyzing}
                >
                  Eliminar
                </button>
              </article>
            ))}
          </div>
        </section>
      )}

      {error && (
        <div className="scouting-alert">
          <strong>Error</strong>
          <span>{error}</span>
        </div>
      )}

      <button
        type="button"
        className="scouting-primary-button"
        onClick={handleGenerateScouting}
        disabled={isAnalyzing}
      >
        {isAnalyzing ? "Generant scouting..." : "Generar scouting"}
      </button>

      {result && (
        <section className="scouting-result">
          <div className="scouting-result-header">
            <span>Informe generat</span>
            <h3>Scouting del rival</h3>
            <p>{result.resum_rival}</p>
          </div>

          <div className="scouting-result-grid scouting-result-grid-main">
            <ResultBlock
              title="Patrons recurrents"
              items={result.patrons_recurrents}
              wide
            />

            <ResultBlock title="Punts forts" items={result.punts_forts} />

            <ResultBlock title="Debilitats" items={result.debilitats} />
          </div>

          {result.perfil === "entrenador" && (
            <>
              <div className="scouting-result-grid scouting-result-grid-coach">
                <ResultBlock
                  title="Pla tàctic recomanat"
                  items={result.informe_entrenador.pla_tactic_recomanat}
                  wide
                />

                <ResultBlock
                  title="Focus d’entrenament"
                  items={result.informe_entrenador.focus_entrenament}
                />

                <ResultBlock
                  title="Exercicis recomanats"
                  items={result.informe_entrenador.exercicis_recomanats}
                />
              </div>

              <ScoutingCharts grafics={result.grafics_suggerits} />
            </>
          )}

          {result.perfil === "lluitador" && (
            <div className="scouting-result-grid scouting-result-grid-fighter">
              <ResultBlock
                title="Amenaces principals"
                items={result.informe_lluitador.amenaces_principals}
              />

              <ResultBlock
                title="Què evitar"
                items={result.informe_lluitador.que_evitar}
              />

              <ResultBlock
                title="Pla de combat"
                items={result.informe_lluitador.pla_combat}
                wide
              />

              {result.informe_lluitador.missatge_final && (
                <div className="scouting-result-block scouting-result-block-wide">
                  <h4>Missatge final</h4>
                  <p>{result.informe_lluitador.missatge_final}</p>
                </div>
              )}
            </div>
          )}

          {result.incerteses.length > 0 && (
            <div className="scouting-result-incerteses">
              <ResultBlock
                title="Incerteses"
                items={result.incerteses}
                warning
                wide
              />
            </div>
          )}
        </section>
      )}
    </section>
  );
}

function ResultBlock({
  title,
  items,
  warning = false,
  wide = false,
}: {
  title: string;
  items: string[];
  warning?: boolean;
  wide?: boolean;
}) {
  const className = [
    "scouting-result-block",
    warning ? "scouting-result-block-warning" : "",
    wide ? "scouting-result-block-wide" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={className}>
      <h4>{title}</h4>

      {items.length > 0 ? (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>No hi ha dades suficients.</p>
      )}
    </div>
  );
}

export default ScoutingScreen;