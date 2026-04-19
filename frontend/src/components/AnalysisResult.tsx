import type { AnalysisResponse, AnalisiOponent } from "../types";
import "./AnalysisResult.css";

type Props = {
  result: AnalysisResponse | null;
};

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

function renderOponent(title: string, op: AnalisiOponent) {
  return (
    <div className="opponent-card">
      <h4 className="opponent-title">{title}</h4>

      <div className="opponent-block">
        <span className="opponent-block-title">Tàctica</span>
        <p className="analysis-text">{op.tactica_general}</p>
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
        {op.errors_detallats?.length ? (
          <ul className="analysis-list">
            {op.errors_detallats.map((e, index) => (
              <li key={index}>
                {e.error} ({e.moment_aproximat}) → {e.impacte}
              </li>
            ))}
          </ul>
        ) : (
          <p className="analysis-empty">No s’han detectat errors destacables.</p>
        )}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Encerts</span>
        {op.encerts_clau?.length ? (
          <ul className="analysis-list">
            {op.encerts_clau.map((e, index) => (
              <li key={index}>
                {e.encert} ({e.moment_aproximat}) → {e.impacte}
              </li>
            ))}
          </ul>
        ) : (
          <p className="analysis-empty">No s’han detectat encerts destacables.</p>
        )}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Seqüències repetides</span>
        {renderStringList(op.sequencies_repetides)}
      </div>

      <div className="opponent-block">
        <span className="opponent-block-title">Millores</span>
        {op.millores_recomanades?.length ? (
          <ul className="analysis-list">
            {op.millores_recomanades.map((m, index) => (
              <li key={index}>
                {m.millora} → {m.benefici_esperat}
              </li>
            ))}
          </ul>
        ) : (
          <p className="analysis-empty">No hi ha millores recomanades.</p>
        )}
      </div>
    </div>
  );
}

export default function AnalysisResult({ result }: Props) {
  if (!result) return null;

  const oponent1Info = result.combat_info.oponents.find(
    (o) => o.id === "oponent_1"
  );
  const oponent2Info = result.combat_info.oponents.find(
    (o) => o.id === "oponent_2"
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

  return (
    <section className="analysis-container">
      <h2 className="analysis-main-title">Resultat de l’anàlisi</h2>

      <div className="analysis-card">
        <h3 className="analysis-card-title">Informació del combat</h3>
        <div className="analysis-info-grid">
          <p className="analysis-text">
            <strong>Durada estimada:</strong> {result.combat_info.durada_estimada}
          </p>
          <p className="analysis-text">
            <strong>Confiança global:</strong>{" "}
            {result.combat_info.nivell_confianca_global}
          </p>
        </div>
      </div>

      <div className="analysis-card">
        <h3 className="analysis-card-title">Resum del combat</h3>
        <p className="analysis-text">
          <strong>Guanyador:</strong> {result.resum_partit.guanyador.id} -{" "}
          {result.resum_partit.guanyador.descripcio}
        </p>
        <p className="analysis-text">
          <strong>Perdedor:</strong> {result.resum_partit.perdedor.id} -{" "}
          {result.resum_partit.perdedor.descripcio}
        </p>
        <p className="analysis-text">
          <strong>Mètode:</strong> {result.resum_partit.metode}
        </p>

        {result.resum_partit.metode === "submissio" &&
          result.resum_partit.tipus_submissio && (
            <p className="analysis-text">
              <strong>Tipus de submissió:</strong>{" "}
              {result.resum_partit.tipus_submissio}
            </p>
          )}

        <p className="analysis-text">{result.resum_partit.resum_breu}</p>
      </div>

      <div className="analysis-card">
        <h3 className="analysis-card-title">Timeline</h3>
        {result.timeline?.length ? (
          <ul className="timeline-list">
            {result.timeline.map((event, index) => (
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
        <h3 className="analysis-card-title">Anàlisi dels oponents</h3>
        <div className="opponents-grid">
          {renderOponent(oponent1Label, result.analisi_oponents.oponent_1)}
          {renderOponent(oponent2Label, result.analisi_oponents.oponent_2)}
        </div>
      </div>

      {result.estadistiques_estimades && (
        <div className="analysis-card">
          <h3 className="analysis-card-title">Estadístiques (calculades)</h3>

          {result.estadistiques_estimades.temps_per_posicio?.length ? (
            <ul className="analysis-list">
              {result.estadistiques_estimades.temps_per_posicio.map(
                (item, index) => (
                  <li key={index}>
                    {item.lluitador} - {item.posicio}: {item.segons}s
                    {item.dominant ? " (dominant)" : ""}
                  </li>
                )
              )}
            </ul>
          ) : (
            <p className="analysis-empty">No hi ha estadístiques disponibles.</p>
          )}

          <p className="analysis-text">
            <strong>Canvis de control:</strong>{" "}
            {result.estadistiques_estimades.canvis_control}
          </p>
        </div>
      )}

      <div className="analysis-card">
        <h3 className="analysis-card-title">Patrons globals</h3>

        <div className="analysis-subblock">
          <span className="opponent-block-title">Dinàmiques clau</span>
          {renderStringList(result.patrons_globals.dinamiques_clau)}
        </div>

        <div className="analysis-subblock">
          <span className="opponent-block-title">Moments decisius</span>
          {renderStringList(result.patrons_globals.moments_decisius)}
        </div>

        <div className="analysis-subblock">
          <span className="opponent-block-title">Resum comparable</span>
          {renderStringList(result.patrons_globals.resum_comparable)}
        </div>
      </div>

      {result.incerteses?.length > 0 && (
        <div className="analysis-card">
          <h3 className="analysis-card-title">Incerteses</h3>
          {renderStringList(result.incerteses)}
        </div>
      )}
    </section>
  );
}