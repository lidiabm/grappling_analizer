import { useState } from "react";
import Header from "./components/Header";

import HomeScreen from "./screens/HomeScreen";
import LluitadorMenuScreen from "./screens/LluitadorMenuScreen";
import EntrenadorMenuScreen from "./screens/EntrenadorMenuScreen";
import AnalysisScreen from "./screens/AnalysisScreen";
import PlaceholderScreen from "./screens/PlaceholderScreen";
import HistoryScreen from "./screens/HistoryScreen";
import EntrenadorTrainingFocusScreen from "./screens/EntrenadorTrainingFocusScreen";
import ScoutingScreen from "./screens/ScoutingScreen";

type Screen =
  | "home"
  | "lluitador-menu"
  | "entrenador-menu"
  | "lluitador-analysis"
  | "lluitador-scouting"
  | "lluitador-evolution"
  | "lluitador-history"
  | "entrenador-analysis"
  | "entrenador-training-focus"
  | "entrenador-scouting"
  | "entrenador-athletes";

function App() {
  const [screen, setScreen] = useState<Screen>("home");

  console.log("SCREEN ACTUAL:", screen);

  function handleGoHome() {
    setScreen("home");
  }

  function renderScreen() {
    switch (screen) {
      case "home":
        return (
          <HomeScreen
            onSelectProfile={(profile) =>
              setScreen(
                profile === "lluitador" ? "lluitador-menu" : "entrenador-menu"
              )
            }
          />
        );

      case "lluitador-menu":
        return (
          <LluitadorMenuScreen
            onSelectFeature={(feature) => setScreen(feature)}
            onSelectProfile={(profile) =>
              setScreen(
                profile === "lluitador" ? "lluitador-menu" : "entrenador-menu"
              )
            }
          />
        );

      case "entrenador-menu":
        return (
          <EntrenadorMenuScreen
            onSelectFeature={(feature) => setScreen(feature)}
            onSelectProfile={(profile) =>
              setScreen(
                profile === "lluitador" ? "lluitador-menu" : "entrenador-menu"
              )
            }
          />
        );

      case "lluitador-analysis":
        return (
          <AnalysisScreen
            profile="lluitador"
            onBack={() => setScreen("lluitador-menu")}
          />
        );

      case "entrenador-analysis":
        return (
          <AnalysisScreen
            profile="entrenador"
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      case "lluitador-scouting":
        return (
          <ScoutingScreen
            profile="lluitador"
            onBack={() => setScreen("lluitador-menu")}
          />
        );

      case "lluitador-evolution":
        return (
          <PlaceholderScreen
            title="Evolució"
            onBack={() => setScreen("lluitador-menu")}
          />
        );

      case "lluitador-history":
        return (
          <HistoryScreen
            profileFilter="lluitador"
            title="Historial"
            onBack={() => setScreen("lluitador-menu")}
          />
        );

      case "entrenador-training-focus":
        return (
          <EntrenadorTrainingFocusScreen
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      case "entrenador-scouting":
        return (
          <ScoutingScreen
            profile="entrenador"
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      case "entrenador-athletes":
        return (
          <HistoryScreen
            profileFilter="entrenador"
            title="Esportistes"
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      default:
        return (
          <div className="analysis-card">
            <h2>Pantalla no trobada</h2>
            <p>{screen}</p>
          </div>
        );
    }
  }

  return (
    <>
      <Header onGoHome={handleGoHome} />

      <main className="app-shell">
        <section className="app-card">{renderScreen()}</section>
      </main>
    </>
  );
}

export default App;