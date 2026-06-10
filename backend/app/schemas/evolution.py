from typing import Literal, Optional
from pydantic import BaseModel

class FighterEvolutionRequest(BaseModel):
    old_analysis: dict
    new_analysis: dict

class FighterInfo(BaseModel):
    nom_visible: str
    descripcio_visual: str
    confianca_analisi: Literal["alta", "mitjana", "baixa"]

class StablePatterns(BaseModel):
    fortaleses_consolidades: list[str]
    debilitats_persistents: list[str]

class TacticalEvolution(BaseModel):
    model_antic: str
    model_recent: str
    canvi_observat: str
    interpretacio: str

class TechnicalEvolution(BaseModel):
    tecniques_millorades: list[str]
    tecniques_empitjorades: list[str]
    tecniques_noves: list[str]
    tecniques_abandonades: list[str]

class NumericProfile(BaseModel):
    pressio: int = -1
    agressivitat: int = -1
    control_posicional: int = -1
    defensa: int = -1
    perill_submissio: int = -1
    explosivitat: int = -1
    adaptabilitat: int = -1

class NumericDeltas(BaseModel):
    nota: str = ""
    pressio: Optional[int] = None
    agressivitat: Optional[int] = None
    control_posicional: Optional[int] = None
    defensa: Optional[int] = None
    perill_submissio: Optional[int] = None
    explosivitat: Optional[int] = None
    adaptabilitat: Optional[int] = None

class NumericComparison(BaseModel):
    nota: str = ""
    disponible: bool = False
    perfil_antic: NumericProfile = NumericProfile()
    perfil_recent: NumericProfile = NumericProfile()
    deltes: NumericDeltas = NumericDeltas()

class ChartDataPoint(BaseModel):
    label: str
    valor: int

class ChartSerie(BaseModel):
    nom: str
    dades: list[ChartDataPoint]

class SuggestedChart(BaseModel):
    id: str
    tipus: str
    titol: str
    descripcio: str
    series: Optional[list[ChartSerie]] = None
    dades: Optional[list[ChartDataPoint]] = None
    escala: str
    interpretacio: str

class TrainingRecommendations(BaseModel):
    prioritat_alta: list[str]
    prioritat_mitjana: list[str]
    manteniment: list[str]

class FighterEvolutionResponse(BaseModel):
    mode: Literal["evolucio"]
    analysis_type: Literal["evolucio_lluitador"]
    fighter_info: FighterInfo
    resum_evolucio: str
    magnitud_canvi_global: Literal["alta", "mitjana", "baixa"]
    millores: list[str]
    regressions: list[str]
    patrons_estables: StablePatterns
    evolucio_tactica: TacticalEvolution
    evolucio_tecnica: TechnicalEvolution
    comparativa_numerica: NumericComparison
    grafics_suggerits: list[SuggestedChart]
    recomanacions_entrenament: TrainingRecommendations
    conclusio: str
    incerteses: list[str]