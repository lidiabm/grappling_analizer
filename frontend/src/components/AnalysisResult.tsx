import { useState, type ReactNode } from "react";
import type { AnalysisResponse, UserProfile } from "../types";
import SaveAnalysisModal from "./SaveAnalysisModal";
import StatsCharts from "./charts/StatsCharts";
import "./AnalysisResult.css";

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

function getAnalysisTypeLabel(type: AnalysisType) {
  const labels: Record<AnalysisType, string> = {
    auto_analisi: "Autoanàlisi",
    analisi_alumne: "Anàlisi d’alumne",
    combat_lluitador: "Combat complet",
    combat_entrenador: "Combat d’entrenador",
  };

  return labels[type];
}

function formatSubmissionType(value?: string | null) {
  const labels: Record<string, string> = {
    estrangulacio: "Estrangulació",
    armbar: "Clau de braç",
    triangle: "Triangle",
    kimura: "Kimura",
    americana: "Americana",
    leg_lock: "Clau de cama",
    ankle_lock: "Clau de turmell",
    heel_hook: "Heel hook",
    kneebar: "Kneebar",
    toe_hold: "Toe hold",
    guillotine: "Guillotina",
    rear_naked_choke: "Mata-lleó",
    omoplata: "Omoplata",
    altra: "Altra",
    desconegut: "Desconegut",
  };

  if (!value) return "Desconegut";
  return labels[value] ?? value;
}

function renderStringList(items?: string[]) {
  if (!items || items.length === 0) {
    return <p className="analysis-result-empty">No hi ha informació disponible.</p>;
  }

  return (
    <ul className="analysis-result-list">
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
    return `${fallbackLabel} · ${nomVisible}`;
  }

  return `${fallbackLabel} · ${descripcioVisual ?? "desconegut"}`;
}

function renderErrors(op: any) {
  const errors = op.errors_i_correccions ?? op.errors_principals ?? [];

  if (!errors.length) {
    return <p className="analysis-result-empty">No s’han detectat errors destacables.</p>;
  }

  return (
    <ul className="analysis-result-list">
      {errors.map((e: any, index: number) => (
        <li key={index}>
          {e.error} {e.moment_aproximat ? `(${e.moment_aproximat})` : ""}
          {e.fase ? ` · ${e.fase}` : ""} →{" "}
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
    return <p className="analysis-result-empty">No s’han detectat encerts destacables.</p>;
  }

  return (
    <ul className="analysis-result-list">
      {op.encerts_clau.map((e: any, index: number) => (
        <li key={index}>
          {e.encert} {e.moment_aproximat ? `(${e.moment_aproximat})` : ""}
          {e.fase ? ` · ${e.fase}` : ""} → {e.impacte}
          {e.principi_tecnic && <> — Principi tècnic: {e.principi_tecnic}</>}
        </li>
      ))}
    </ul>
  );
}

function renderMillores(op: any) {
  const milloresRecomanades = Array.isArray(op.millores_recomanades)
    ? op.millores_recomanades
    : [];

  const prioritatsTreball = Array.isArray(op.prioritats_de_treball)
    ? op.prioritats_de_treball
    : [];

  const millores =
    milloresRecomanades.length > 0 ? milloresRecomanades : prioritatsTreball;

  if (!millores.length) {
    return <p className="analysis-result-empty">No hi ha millores recomanades.</p>;
  }

  return (
    <ul className="analysis-result-list">
      {millores.map((m: any, index: number) => (
        <li key={index}>
          {m.prioritat && <strong>[{m.prioritat}] </strong>}
          {m.millora ?? m.area ?? "Millora"}
          {m.objectiu ? ` → ${m.objectiu}` : ""}
          {m.benefici_esperat ? ` (${m.benefici_esperat})` : ""}
          {m.problema_tecnic ? ` — ${m.problema_tecnic}` : ""}
        </li>
      ))}
    </ul>
  );
}

function ResultBlock({
  title,
  children,
  wide = false,
}: {
  title: string;
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <article
      className={`analysis-result-block ${
        wide ? "analysis-result-block-wide" : ""
      }`}
    >
      <h4>{title}</h4>
      {children}
    </article>
  );
}

function renderOponent(title: string, op?: any) {
  if (!op) {
    return (
      <section className="analysis-opponent-card">
        <header className="analysis-opponent-header">
          <span className="analysis-result-eyebrow">Lluitador</span>
          <h3>{title}</h3>
        </header>

        <p className="analysis-result-empty">
          No hi ha informació disponible per aquest lluitador.
        </p>
      </section>
    );
  }

  return (
    <section className="analysis-opponent-card">
      <header className="analysis-opponent-header">
        <span className="analysis-result-eyebrow">Lluitador</span>
        <h3>{title}</h3>
      </header>

      <div className="analysis-result-block-grid">
        {op.resum_personal && (
          <ResultBlock title="Resum personal" wide>
            <p>{op.resum_personal}</p>
          </ResultBlock>
        )}

        {op.resum_tecnic && (
          <ResultBlock title="Resum tècnic" wide>
            <p>{op.resum_tecnic}</p>
          </ResultBlock>
        )}

        {op.resum_rendiment && (
          <ResultBlock title="Resum del rendiment" wide>
            <p>{op.resum_rendiment}</p>
          </ResultBlock>
        )}

        {op.model_de_combat && (
          <ResultBlock title="Model de combat" wide>
            <p>{op.model_de_combat}</p>
          </ResultBlock>
        )}

        {op.lectura_posicional && (
          <ResultBlock title="Lectura posicional" wide>
            <p>{op.lectura_posicional}</p>
          </ResultBlock>
        )}

        <ResultBlock title="Tàctica" wide>
          <p>{op.tactica_general || "No hi ha informació disponible."}</p>
        </ResultBlock>

        <ResultBlock title="Patrons">
          {renderStringList(op.patrons_tactics)}
        </ResultBlock>

        <ResultBlock title="Fortaleses">
          {renderStringList(op.fortaleses_clau)}
        </ResultBlock>

        <ResultBlock title="Debilitats" wide>
          {renderStringList(op.debilitats_clau)}
        </ResultBlock>

        <ResultBlock title="Errors" wide>
          {renderErrors(op)}
        </ResultBlock>

        <ResultBlock title="Encerts" wide>
          {renderEncerts(op)}
        </ResultBlock>

        <ResultBlock title="Millores / prioritats" wide>
          {renderMillores(op)}
        </ResultBlock>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="analysis-stat-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function renderLecturaGlobal(lectura?: any) {
  if (!lectura) return null;

  return (
    <section className="analysis-result-card">
      <div className="analysis-result-section-heading">
        <span className="analysis-result-eyebrow">Lectura</span>
        <h3>Lectura global</h3>
      </div>

      <div className="analysis-result-block-grid">
        {lectura.dinamica_general && (
          <ResultBlock title="Dinàmica general" wide>
            <p>{lectura.dinamica_general}</p>
          </ResultBlock>
        )}

        {lectura.moments_decisius && (
          <ResultBlock title="Moments decisius">
            {renderStringList(lectura.moments_decisius)}
          </ResultBlock>
        )}

        {lectura.lliçons_practiques && (
          <ResultBlock title="Lliçons pràctiques">
            {renderStringList(lectura.lliçons_practiques)}
          </ResultBlock>
        )}

        {lectura.claus_tactiques && (
          <ResultBlock title="Claus tàctiques">
            {renderStringList(lectura.claus_tactiques)}
          </ResultBlock>
        )}
      </div>
    </section>
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
      : `Lluitador seleccionat · ${selectedOponentId}`;

  return (
    <section className="analysis-result-container">
      <header className="analysis-result-header">
        <div>
          <span className="analysis-result-eyebrow">Informe generat</span>

          <h2 className="analysis-result-title">Resultat de l’anàlisi</h2>

          <div className="analysis-result-meta-row">
            <span>{getAnalysisTypeLabel(analysisType)}</span>

            {isSingleAthlete && (
              <span>
                Anàlisi individual · {selectedOponentId}
                {data.debug_request?.athlete_identifier_value
                  ? ` · ${data.debug_request.athlete_identifier_value}`
                  : ""}
              </span>
            )}
          </div>
        </div>

        <div className="analysis-result-actions">
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
                className="analysis-result-delete-button"
                onClick={onDelete}
              >
                Eliminar anàlisi
              </button>
            )
          )}
        </div>
      </header>

      {showSaveButton && (
        <SaveAnalysisModal
          open={saveModalOpen}
          onClose={() => setSaveModalOpen(false)}
          result={result}
          fightId={fightId}
          profile={profile}
        />
      )}

      <section className="analysis-result-card analysis-result-summary-card">
        <div className="analysis-result-section-heading">
          <span className="analysis-result-eyebrow">Combat</span>
          <h3>Informació general</h3>
        </div>

        <div className="analysis-stat-grid">
          <Stat
            label="Durada estimada"
            value={data.combat_info?.durada_estimada ?? "desconegut"}
          />
          <Stat
            label="Confiança global"
            value={data.combat_info?.nivell_confianca_global ?? "desconegut"}
          />
          <Stat
            label="Mètode"
            value={data.resum_partit?.metode ?? "desconegut"}
          />
          {data.resum_partit?.metode === "submissio" && (
            <Stat
              label="Submissió"
              value={formatSubmissionType(data.resum_partit.tipus_submissio)}
            />
          )}
        </div>

        {data.resum_partit?.guanyador && (
          <p className="analysis-result-text">
            <strong>Guanyador:</strong>{" "}
            {data.resum_partit.guanyador.id ?? "desconegut"} ·{" "}
            {data.resum_partit.guanyador.descripcio ?? "desconegut"}
          </p>
        )}

        {data.resum_partit?.resum_breu && (
          <p className="analysis-result-text">{data.resum_partit.resum_breu}</p>
        )}
      </section>

      <section className="analysis-result-card">
        <div className="analysis-result-section-heading">
          <span className="analysis-result-eyebrow">Seqüència</span>
          <h3>Timeline</h3>
        </div>

        {data.timeline?.length ? (
          <ul className="analysis-timeline-list">
            {data.timeline.map((event: any, index: number) => (
              <li key={index} className="analysis-timeline-item">
                <span className="analysis-timeline-time">
                  {event.inici} - {event.fi}
                </span>

                <p>{event.descripcio}</p>

                <div className="analysis-timeline-meta">
                  <span>{event.posicio}</span>
                  <span>Controlador: {event.controlador}</span>
                  <span>Rellevància: {event.rellevancia}</span>
                  <span>Confiança: {event.confianca}</span>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="analysis-result-empty">No hi ha esdeveniments disponibles.</p>
        )}
      </section>

      <section className="analysis-result-card">
        <div className="analysis-result-section-heading">
          <span className="analysis-result-eyebrow">Rendiment</span>
          <h3>{isFullFight ? "Anàlisi dels oponents" : "Anàlisi del lluitador"}</h3>
        </div>

        <div className="analysis-opponents-grid">
          {isFullFight ? (
            <>
              {renderOponent(oponent1Label, data.analisi_oponents?.oponent_1)}
              {renderOponent(oponent2Label, data.analisi_oponents?.oponent_2)}
            </>
          ) : (
            renderOponent(singleAthleteTitle, data.analisi_lluitador)
          )}
        </div>
      </section>

      {renderLecturaGlobal(data.lectura_global)}

      {showStats && data.estadistiques_estimades && (
        <section className="analysis-result-card">
          <div className="analysis-result-section-heading">
            <span className="analysis-result-eyebrow">Dades</span>
            <h3>Estadístiques</h3>
          </div>

          <StatsCharts
            stats={data.estadistiques_derivades ?? data.estadistiques_estimades}
          />
        </section>
      )}

      {data.incerteses?.length > 0 && (
        <section className="analysis-result-card analysis-review-card">
          <div className="analysis-result-section-heading">
            <span className="analysis-result-eyebrow">Revisió</span>
            <h3>Incerteses</h3>
          </div>

          <div className="analysis-review-list">
            {data.incerteses.map((item: string, index: number) => (
              <article key={index} className="analysis-review-item">
                <span>{index + 1}</span>
                <p>{item}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </section>
  );
}