from pathlib import Path
from typing import Annotated
import traceback

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas.analysis import AnalysisResponse
from app.services.gemini_service import analyze_video

# Creació de l'aplicació FastAPI 
app = FastAPI(title="Grappling Analyzer API")

# Configuració de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Assegura que el directori de pujada de fitxers existeixi 
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

@app.get("/")
def root():
    return {"message": "Grappling Analyzer API funcionando"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    video: Annotated[UploadFile, File(...)],
    profile: Annotated[str, Form(...)],
):
    if profile not in {"lluitador", "entrenador"}:
        raise HTTPException(status_code=400, detail="profile ha de ser 'lluitador' o 'entrenador'")

    if not video.filename:
        raise HTTPException(status_code=400, detail="No s'ha rebut cap fitxer")

    # Construcció del path on es guardarà el vídeo 
    file_path = Path(settings.upload_dir) / video.filename

    try:
        # Llegir el contingut del fitxer i escriure'l al disc 
        content = await video.read()
        file_path.write_bytes(content)

        # Cridar el servei de Gemini i retornar el resultat
        result = analyze_video(str(file_path), profile)
        return result

    except Exception as e:
        print("ERROR A /analyze:")
        traceback.print_exc()

        message = str(e)

        if "503" in message or "UNAVAILABLE" in message:
            raise HTTPException(
                status_code=503,
                detail="El servei de Gemini està saturat en aquest moment. Torna-ho a provar d’aquí uns segons."
            )

        raise HTTPException(status_code=500, detail=f"Error analitzant vídeo: {message}")