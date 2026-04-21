import { useState } from "react";
import type { AnalysisResponse } from "../types";
import UploadForm from "../components/UploadForm";
import AnalysisResult from "../components/AnalysisResult";

type Props = {
  onBack: () => void;
};

function LluitadorAnalysisScreen({ onBack }: Props) {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  function handleStart() {
    setIsAnalyzing(true);
    setResult(null);
  }

  function handleResult(newResult: AnalysisResponse) {
    setResult(newResult);
    setIsAnalyzing(false);
  }

  return (
    <div className="app-content">
      <div className="selection-panel">
        <button type="button" className="selection-button" onClick={onBack}>
          ← Tornar
        </button>
      </div>

      <div className="upload-panel">
        <UploadForm
          profile="lluitador"
          onStart={handleStart}
          onResult={handleResult}
        />
      </div>

      <div className="result-panel">
        {isAnalyzing && !result && (
          <div className="result-placeholder">
            <h2>Analitzant combat...</h2>
          </div>
        )}

        {!isAnalyzing && !result && (
          <div className="result-placeholder">
            <h2>Encara no hi ha cap anàlisi</h2>
          </div>
        )}

        {result && <AnalysisResult result={result} />}
      </div>
    </div>
  );
}

export default LluitadorAnalysisScreen;
