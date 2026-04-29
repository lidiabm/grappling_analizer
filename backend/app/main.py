from pathlib import Path
from typing import Annotated, Literal, Optional, Union
import traceback

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas.analysis import AnalysisResponse, SingleAthleteAnalysisResponse
from app.services.gemini_service import analyze_video

app = FastAPI(title="Grappling Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Grappling Analyzer API funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/analyze",
    response_model=Union[AnalysisResponse, SingleAthleteAnalysisResponse],
)
async def analyze(
    video: Annotated[UploadFile, File(...)],
    profile: Annotated[Literal["lluitador", "entrenador"], Form(...)],
    mode: Annotated[Literal["full_fight", "single_athlete"], Form(...)],
    athlete_identifier_type: Annotated[
        Optional[Literal["visual_description", "screen_side", "corner"]],
        Form(),
    ] = None,
    athlete_identifier_value: Annotated[Optional[str], Form()] = None,
):
    if not video.filename:
        raise HTTPException(status_code=400, detail="No s'ha rebut cap fitxer")

    if mode == "single_athlete":
        if not athlete_identifier_type or not athlete_identifier_value:
            raise HTTPException(
                status_code=400,
                detail="Falten dades per identificar l’atleta",
            )

    file_path = Path(settings.upload_dir) / video.filename

    try:
        content = await video.read()
        file_path.write_bytes(content)

        result = analyze_video(
            file_path=str(file_path),
            profile=profile,
            mode=mode,
            athlete_identifier_type=athlete_identifier_type,
            athlete_identifier_value=athlete_identifier_value,
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="La resposta del servei d’anàlisi no és un JSON vàlid.",
            )

        result["mode"] = mode
        result["perfil"] = profile

        if mode == "full_fight":
            result["selected_oponent_id"] = "desconegut"

            if "analisi_oponents" not in result:
                raise HTTPException(
                    status_code=500,
                    detail="Gemini no ha retornat el camp analisi_oponents en mode full_fight.",
                )

            result.pop("analisi_lluitador", None)

        if mode == "single_athlete":
            result.setdefault("selected_oponent_id", "desconegut")

            if "analisi_lluitador" not in result:
                raise HTTPException(
                    status_code=500,
                    detail="Gemini no ha retornat el camp analisi_lluitador en mode single_athlete.",
                )

            result.pop("analisi_oponents", None)

        return result

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR A /analyze:")
        traceback.print_exc()

        message = str(e)

        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            raise HTTPException(
                status_code=429,
                detail="S'ha superat la quota de Gemini. Torna-ho a provar més tard.",
            )

        if "503" in message or "UNAVAILABLE" in message:
            raise HTTPException(
                status_code=503,
                detail="El servei de Gemini està saturat en aquest moment. Torna-ho a provar d’aquí uns segons.",
            )

        raise HTTPException(
            status_code=500,
            detail=f"Error analitzant vídeo: {message}",
        )