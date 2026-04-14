import { useState } from "react";
import type { AnalysisResponse } from "./types";
import UploadForm from "./components/UploadForm";
import AnalysisResult from "./components/AnalysisResult";

function App() {
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Grappling Analyzer</h1>
      <p>
        Puja un vídeo i rep una anàlisi orientada a lluitador o entrenador.
      </p>

      <UploadForm onResult={setResult} />
      <AnalysisResult result={result} />
    </main>
  );
}

export default App;