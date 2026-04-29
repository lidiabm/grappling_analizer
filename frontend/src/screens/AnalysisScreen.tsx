import { useState } from "react";
import type { AnalysisResponse, UserProfile } from "../types";
import UploadForm from "../components/UploadForm";
import AnalysisResult from "../components/AnalysisResult";

type Props = {
  profile: UserProfile;
  onBack: () => void;
};

function AnalysisScreen({ profile, onBack }: Props) {
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState("combat-sense-titol");
  
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
        <button type="button" className="back-button" onClick={onBack}>
          ← Tornar
        </button>
      </div>

      <div className="upload-panel">
        <UploadForm
          profile={profile}
          onStart={handleStart}
          onResult={handleResult}
          onFileSelected={setSelectedFileName}
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

        <AnalysisResult
          result={result}
          profile={profile}
          fightId={selectedFileName}
        />
      </div>
    </div>
  );
}

export default AnalysisScreen;