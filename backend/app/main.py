from pathlib import Path
from typing import Annotated, Literal, Optional, Union
import traceback
import json

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
# from app.schemas.analysis import AnalysisResponse, SingleAthleteAnalysisResponse
from app.services.gemini_service import analyze_video
from app.services.training_focus_service import build_training_focus_response
from app.services.scouting_service import analyze_scouting_videos

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
    # response_model=Union[AnalysisResponse, SingleAthleteAnalysisResponse],
    response_model=None,
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
            result.pop("analisi_lluitador", None)

        if mode == "single_athlete":
            result.setdefault("selected_oponent_id", "desconegut")
            result.pop("analisi_oponents", None)
            result.pop("lectura_global", None)

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
    
@app.post("/training-focus")
async def training_focus(payload: dict):
    print("ENTRA EN /training-focus")
    print("Payload keys:", payload.keys())

    analyses = payload.get("analyses")
    print("Num analyses:", len(analyses) if isinstance(analyses, list) else "NO LIST")

    if not isinstance(analyses, list):
        raise HTTPException(
            status_code=400,
            detail="El camp 'analyses' ha de ser una llista.",
        )

    return build_training_focus_response(analyses)

@app.post(
    "/scouting",
    response_model=None,
)
async def scouting(
    videos: Annotated[list[UploadFile], File(...)],
    profile: Annotated[Literal["lluitador", "entrenador"], Form(...)],
    video_descriptions: Annotated[str, Form(...)],
):
    if not videos:
        raise HTTPException(
            status_code=400,
            detail="No s'ha rebut cap vídeo per fer scouting",
        )

    try:
        descriptions = json.loads(video_descriptions)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Les descripcions dels vídeos no són JSON vàlid.",
        )

    if not isinstance(descriptions, list) or len(descriptions) != len(videos):
        raise HTTPException(
            status_code=400,
            detail="Cada vídeo ha de tenir una descripció del rival.",
        )

    file_paths: list[str] = []

    try:
        for video in videos:
            if not video.filename:
                raise HTTPException(
                    status_code=400,
                    detail="Un dels vídeos no té nom de fitxer",
                )

            file_path = Path(settings.upload_dir) / video.filename

            content = await video.read()
            file_path.write_bytes(content)

            file_paths.append(str(file_path))

        result = analyze_scouting_videos(
            file_paths=file_paths,
            profile=profile,
            video_descriptions=descriptions,
        )

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail="La resposta del servei de scouting no és un JSON vàlid.",
            )

        result["mode"] = "scouting"
        result["perfil"] = profile

        return result

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR A /scouting:")
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
            detail=f"Error fent scouting: {message}",
        )