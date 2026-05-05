import { useState } from "react";
import type { AnalysisResponse, UserProfile } from "../types";
import "./AnalysisResult.css";
import SaveAnalysisModal from "./SaveAnalysis";
import StatsCharts from "./StatsCharts";

type Props = {
  result: AnalysisResponse | null;
  profile: UserProfile;
  fightId: string;
  showSaveButton?: boolean;
  onDelete?: () => void;
};

type AnalysisType =
  | "auto_analisi"
  | "analisi_alumne"
  | "combat_lluitador"
  | "combat_entrenador";

function getAnalysisType(result: any, profile: UserProfile): AnalysisType {
  if (result.analysis_type) return result.analysis_type;

  if (profile === "lluitador" && result.mode === "single_athlete") {
    return "auto_analisi";
  }

  if (profile === "entrenador" && result.mode === "single_athlete") {
    return "analisi_alumne";
  }

  if (profile === "lluitador" && result.mode === "full_fight") {
    return "combat_lluitador";
  }

  return "combat_entrenador";
}

function renderStringList(items?: string[]) {
  if (!items || items.length === 0) {
    return <p className="analysis-empty">No hi ha informació disponible.</p>;
  }

  return (
    <ul className="analysis-list">
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}

function renderOpponentLabel(
  fallbackLabel: string,
  nomVisible?: string,
  descripcioVisual?: string
) {
  if (nomVisible && nomVisible !== "desconegut") {
    return `${fallbackLabel} (${nomVisible})`;
  }

  return `${fallbackLabel} (${descripcioVisual ?? "desconegut"})`;
}

function renderErrors(op: any) {
  const errors = op.errors_i_correccions ?? op.errors_principals ?? [];

  if (!errors.length) {
    return <p className="analysis-empty">No s’han detectat errors destacables.</p>;
  }

  return (
    <ul className="analysis-list">
      {errors.map((e: any, index: number) => (
        <li key={index}>
          {e.error} ({e.moment_aproximat})
          {e.fase ? ` [${e.fase}]` : ""} →{" "}
          {e.impacte ?? e.consequencia ?? "sense impacte especificat"}
          {e.correccio && <> — Correcció: {e.correccio}</>}
          {e.correccio_tecnica && <> — Correcció tècnica: {e.correccio_tecnica}</>}
          {e.causa_tecnica_observable && (
            <> — Causa observable: {e.causa_tecnica_observable}</>
          )}
        </li>
      ))}
    </ul>
  );
}

function renderEncerts(op: any) {
  if (!op.encerts_clau?.length) {
    return <p className="analysis-empty">No s’han detectat encerts destacables.</p>;
  }

  return (
    <ul className="analysis-list">
      {op.encerts_clau.map((e: any, index: number) => (
        <li key={index}>
          {e.encert} ({e.moment_aproximat})
          {e.fase ? ` [${e.fase}]` : ""} → {e.impacte}
          {e.principi_tecnic && <> — Principi tècnic: {e.principi_tecnic}</>}
        </li>
      ))}
    </ul>
  );
}

function renderMillores(op: any) {
  const millores = op.millores_recomanades ?? op.prioritats_de_treball ?? [];

  if (!millores.length) {
    return <p className="analysis-empty">No hi ha millores recomanades.</p>;
  }

  return (
    <ul className="analysis-list">
      {millores.map((m: any, index: number) => (
        <li key={index}>
          {m.prioritat && <strong>[{m.prioritat}] </strong>}
          {m.millora ?? m.area ?? "Millora"}{" "}
          {m.objectiu ? `→ ${m.objectiu}` : ""}
          {m.benefici_esperat ? ` (${m.benefici_esperat})` : ""}
          {m.problema_tecnic ? ` — ${m.problema_tecnic}` : ""}
        </li>
      ))}
    </ul>
  );
}

function renderOponent(title: string, op?: any) {
  if (!op) {
    return (
      <div className="opponent-card">
        <h4 className="opponent-title">{title}</h4>
        <p className="analysis-empty">
          No hi ha informació disponible per aquest lluitador.
        </p>
      </div>
    );
  }

  return (
    <div className="opponent-card">
      <h4 className="opponent-title">{title}</h4>

      {op.resum_personal && (
        <div className="opponent-block">
          <span className="opponent-block-title">Resum personal</span>
          <p className="analysis-text">{op.resum_personal}</p>
        </div>
      )}

      {op.resum_tecnic && (
        <div className="opponent-block">
          <span className="opponent-block-title">Resum tècnic</span>
          <p className="analysis-text">{op.resum_tecnic}</p>
        </div>
      )}

      {op.resum_rendiment && (
        <div className="opponent-block">
          <span className="opponent-block-title">Resum del rendiment</span>
          <p className="analysis-text">{op.resum_rendiment}</p>
        </div>
      )}

      {op.model_de_combat && (
        <div className="opponent-block">
          <span className="opponent-block-title">Model de combat</span>
          <p className="analysis-text">{op.model_de_combat}</p>
        </div>
      )}

      {op.lectura_posicional && (
        <div className="opponent-block">
          <span className="opponent-block-title">Lectura posicional</span>
          <p className="analysis-text">{op.lectura_posicional}</p>
        </div>
      )}

      <div className="opponent-block">
        <span className="opponent-block-title">Tàctica</span>
        <p className="analysis-text">
          {op.tactica_general || "No hi ha informació disponible."}
        </p>
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Patrons</span>
        {renderStringList(op.patrons_tactics)}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Fortaleses</span>
        {renderStringList(op.fortaleses_clau)}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Debilitats</span>
        {renderStringList(op.debilitats_clau)}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Errors</span>
        {renderErrors(op)}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Encerts</span>
        {renderEncerts(op)}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Millores / prioritats</span>
        {renderMillores(op)}
      </div>
    </div>
  );
}

function renderValue(value: any): string {
  if (value === null || value === undefined) return "desconegut";

  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, val]) => `${key}: ${val}`)
      .join(" · ");
  }

  return String(value);
}

function renderStats(stats?: any) {
  if (!stats) return null;

  return (
    <div className="analysis-card">
      <h3 className="analysis-card-title">Estadístiques</h3>

      {stats.temps_per_posicio?.length ? (
        <ul className="analysis-list">
          {stats.temps_per_posicio.map((item: any, index: number) => (
            <li key={index}>
              {item.lluitador ? `${item.lluitador} - ` : ""}
              {item.posicio}: {item.segons}s
              {typeof item.percentatge === "number"
                ? ` (${item.percentatge}%)`
                : ""}
              {item.dominant ? " · dominant" : ""}
            </li>
          ))}
        </ul>
      ) : (
        <p className="analysis-empty">No hi ha estadístiques disponibles.</p>
      )}

      <p className="analysis-text">
        <strong>Temps dominant:</strong>{" "}
        {renderValue(stats.temps_dominant_total)}
      </p>

      <p className="analysis-text">
        <strong>Temps defensiu:</strong>{" "}
        {renderValue(stats.temps_defensiu_total)}
      </p>

      <p className="analysis-text">
        <strong>Temps neutral:</strong>{" "}
        {renderValue(stats.temps_neutral_total)}
      </p>

      <p className="analysis-text">
        <strong>Canvis de control:</strong>{" "}
        {renderValue(stats.canvis_control)}
      </p>

      <p className="analysis-text">
        <strong>Intents de finalització:</strong>{" "}
        {renderValue(stats.intents_finalitzacio)}
      </p>

      <p className="analysis-text">
        <strong>Intents d’enderroc:</strong>{" "}
        {renderValue(stats.intents_enderroc)}
      </p>

      <p className="analysis-text">
        <strong>Guard pulls:</strong> {renderValue(stats.guard_pulls)}
      </p>

      <p className="analysis-text">
        <strong>Reversions:</strong> {renderValue(stats.reversions)}
      </p>

      <p className="analysis-text">
        <strong>Escapades:</strong> {renderValue(stats.escapades)}
      </p>
    </div>
  );
}

function renderLecturaGlobal(lectura?: any) {
  if (!lectura) return null;

  return (
    <div className="analysis-card">
      <h3 className="analysis-card-title">Lectura global</h3>

      {lectura.dinamica_general && (
        <div className="analysis-subblock">
          <span className="opponent-block-title">Dinàmica general</span>
          <p className="analysis-text">{lectura.dinamica_general}</p>
        </div>
      )}

      {lectura.moments_decisius && (
        <div className="analysis-subblock">
          <span className="opponent-block-title">Moments decisius</span>
          {renderStringList(lectura.moments_decisius)}
        </div>
      )}

      {lectura.lliçons_practiques && (
        <div className="analysis-subblock">
          <span className="opponent-block-title">Lliçons pràctiques</span>
          {renderStringList(lectura.lliçons_practiques)}
        </div>
      )}

      {lectura.claus_tactiques && (
        <div className="analysis-subblock">
          <span className="opponent-block-title">Claus tàctiques</span>
          {renderStringList(lectura.claus_tactiques)}
        </div>
      )}
    </div>
  );
}

export default function AnalysisResult({
  result,
  profile,
  fightId,
  showSaveButton = true,
  onDelete,
}: Props) {
  const [saveModalOpen, setSaveModalOpen] = useState(false);

  if (!result) return null;

  const data: any = result;
  const analysisType = getAnalysisType(data, profile);

  const isSingleAthlete = data.mode === "single_athlete";
  const isFullFight = data.mode === "full_fight";
  const showStats =
    analysisType === "analisi_alumne" ||
    analysisType === "combat_entrenador";

  const selectedOponentId = data.selected_oponent_id ?? "desconegut";

  const oponent1Info = data.combat_info?.oponents?.find(
    (o: any) => o.id === "oponent_1"
  );

  const oponent2Info = data.combat_info?.oponents?.find(
    (o: any) => o.id === "oponent_2"
  );

  const oponent1Label = renderOpponentLabel(
    "Oponent 1",
    oponent1Info?.nom_visible,
    oponent1Info?.descripcio_visual
  );

  const oponent2Label = renderOpponentLabel(
    "Oponent 2",
    oponent2Info?.nom_visible,
    oponent2Info?.descripcio_visual
  );

  const singleAthleteTitle =
    selectedOponentId === "desconegut"
      ? "Lluitador seleccionat"
      : `Lluitador seleccionat (${selectedOponentId})`;

  return (
    <section className="analysis-container">
      <div className="analysis-header">
        <div>
          <h2 className="analysis-main-title">Resultat de l’anàlisi</h2>

          <p className="analysis-mode-label">
            Tipus d’anàlisi: {analysisType}
          </p>

          {isSingleAthlete && (
            <p className="analysis-mode-label">
              Anàlisi individual: {selectedOponentId}
            </p>
          )}
        </div>

        <div className="analysis-header-actions">
          {showSaveButton ? (
            <button
              type="button"
              className="primary-button"
              onClick={() => setSaveModalOpen(true)}
            >
              Guardar anàlisi
            </button>
          ) : (
            onDelete && (
              <button
                type="button"
                className="analysis-delete-button"
                onClick={onDelete}
                aria-label="Eliminar anàlisi"
              >
                Eliminar anàlisi
              </button>
            )
          )}
        </div>
      </div>

      {showSaveButton && (
        <SaveAnalysisModal
          open={saveModalOpen}
          onClose={() => setSaveModalOpen(false)}
          result={result}
          fightId={fightId}
          profile={profile}
        />
      )}

      <div className="analysis-card">
        <h3 className="analysis-card-title">Informació del combat</h3>

        <p className="analysis-text">
          <strong>Durada estimada:</strong>{" "}
          {data.combat_info?.durada_estimada ?? "desconegut"}
        </p>

        <p className="analysis-text">
          <strong>Confiança global:</strong>{" "}
          {data.combat_info?.nivell_confianca_global ?? "desconegut"}
        </p>
      </div>

      <div className="analysis-card">
        <h3 className="analysis-card-title">
          {isSingleAthlete ? "Resum del rendiment" : "Resum del combat"}
        </h3>

        {data.resum_partit?.guanyador && (
          <p className="analysis-text">
            <strong>Guanyador:</strong>{" "}
            {data.resum_partit.guanyador.id ?? "desconegut"} -{" "}
            {data.resum_partit.guanyador.descripcio ?? "desconegut"}
          </p>
        )}

        <p className="analysis-text">
          <strong>Mètode:</strong>{" "}
          {data.resum_partit?.metode ?? "desconegut"}
        </p>

        {data.resum_partit?.metode === "submissio" &&
          data.resum_partit?.tipus_submissio && (
            <p className="analysis-text">
              <strong>Tipus de submissió:</strong>{" "}
              {data.resum_partit.tipus_submissio}
            </p>
          )}

        <p className="analysis-text">
          {data.resum_partit?.resum_breu ?? ""}
        </p>
      </div>

      <div className="analysis-card">
        <h3 className="analysis-card-title">Timeline</h3>

        {data.timeline?.length ? (
          <ul className="timeline-list">
            {data.timeline.map((event: any, index: number) => (
              <li key={index} className="timeline-item">
                <span className="timeline-time">
                  {event.inici} - {event.fi}
                </span>

                <p className="analysis-text">{event.descripcio}</p>

                <div className="timeline-meta">
                  <span>Posició: {event.posicio}</span>
                  <span>Controlador: {event.controlador}</span>
                  <span>Rellevància: {event.rellevancia}</span>
                  <span>Confiança: {event.confianca}</span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="analysis-empty">No hi ha esdeveniments disponibles.</p>
        )}
      </div>

      <div className="analysis-card">
        <h3 className="analysis-card-title">
          {isFullFight ? "Anàlisi dels oponents" : "Anàlisi del lluitador"}
        </h3>

        <div className="opponents-grid">
          {isFullFight ? (
            <>
              {renderOponent(
                oponent1Label,
                data.analisi_oponents?.oponent_1
              )}
              {renderOponent(
                oponent2Label,
                data.analisi_oponents?.oponent_2
              )}
            </>
          ) : (
            renderOponent(singleAthleteTitle, data.analisi_lluitador)
          )}
        </div>
      </div>

      {renderLecturaGlobal(data.lectura_global)}

      {showStats && <StatsCharts stats={data.estadistiques_estimades} />}
      {data.incerteses?.length > 0 && (
        <div className="analysis-card">
          <h3 className="analysis-card-title">Incerteses</h3>
          {renderStringList(data.incerteses)}
        </div>
      )}
    </section>
  );
}