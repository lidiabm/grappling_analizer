import { useState } from "react";
import "./App.css";
import Header from "./components/Header";

import HomeScreen from "./screens/HomeScreen";
import LluitadorMenuScreen from "./screens/LluitadorMenuScreen";
import EntrenadorMenuScreen from "./screens/EntrenadorMenuScreen";
import LluitadorAnalysisScreen from "./screens/LluitadorAnalysisScreen";
import EntrenadorAnalysisScreen from "./screens/EntrenadorAnalysisScreen";
import PlaceholderScreen from "./screens/PlaceholderScreen";

type Screen =
  | "home"
  | "lluitador-menu"
  | "entrenador-menu"
  | "lluitador-analysis"
  | "lluitador-scouting"
  | "lluitador-evolution"
  | "lluitador-history"
  | "entrenador-analysis"
  | "entrenador-training_focus"
  | "entrenador-scouting"
  | "entrenador-athletes";

function App() {
  const [screen, setScreen] = useState<Screen>("home");

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
          <LluitadorAnalysisScreen
            onBack={() => setScreen("lluitador-menu")}
          />
        );

      case "entrenador-analysis":
        return (
          <EntrenadorAnalysisScreen
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      case "lluitador-scouting":
        return (
          <PlaceholderScreen
            title="Scouting d’oponent"
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
          <PlaceholderScreen
            title="Historial"
            onBack={() => setScreen("lluitador-menu")}
          />
        );

      case "entrenador-training_focus":
        return (
          <PlaceholderScreen
            title="Focus d’entrenament"
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      case "entrenador-scouting":
        return (
          <PlaceholderScreen
            title="Scouting"
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      case "entrenador-athletes":
        return (
          <PlaceholderScreen
            title="Esportistes"
            onBack={() => setScreen("entrenador-menu")}
          />
        );

      default:
        return null;
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