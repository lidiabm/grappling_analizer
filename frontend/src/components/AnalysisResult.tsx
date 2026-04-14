import type { AnalysisResponse } from "../types";

type Props = {
  result: AnalysisResponse | null;
};

export default function AnalysisResult({ result }: Props) {
  if (!result) return null;

  return (
    <section style={{ marginTop: 24, textAlign: "left" }}>
      <h2>Resultat de l’anàlisi</h2>

      <div>
        <h3>Resum</h3>
        <p>{result.resum}</p>
      </div>

      <div>
        <h3>Moments clau</h3>
        <ul>
          {result.moments_clau.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3>Observacions tècniques</h3>
        <ul>
          {result.observacions_tecniques.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>

      <div>
        <h3>Recomanacions</h3>
        <ul>
          {result.recomanacions.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}