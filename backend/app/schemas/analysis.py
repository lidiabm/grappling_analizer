from pydantic import BaseModel
from typing import List

class AnalysisResponse(BaseModel):
    resum: str
    moments_clau: List[str]
    observacions_tecniques: List[str]
    recomanacions: List[str]
    perfil: str