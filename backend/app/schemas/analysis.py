from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


UserProfile = Literal["lluitador", "entrenador"]
AnalysisMode = Literal["full_fight", "single_athlete"]
OponentId = Literal["oponent_1", "oponent_2", "desconegut"]
Confianca = Literal["alta", "mitjana", "baixa"]
AnalysisType = Literal[
    "auto_analisi",
    "analisi_alumne",
    "combat_lluitador",
    "combat_entrenador",
]


class AthleteIdentifier(BaseModel):
    type: Literal["visual_description", "screen_side", "corner"]
    value: str


class AnalysisRequest(BaseModel):
    profile: UserProfile
    mode: AnalysisMode
    athlete_identifier: Optional[AthleteIdentifier] = None


class GuanyadorPerdedor(BaseModel):
    id: str
    descripcio: str


class OponentInfo(BaseModel):
    id: Literal["oponent_1", "oponent_2"]
    nom_visible: str
    descripcio_visual: str


class CombatInfo(BaseModel):
    oponents: List[OponentInfo]
    durada_estimada: str
    nivell_confianca_global: Confianca


class ResumPartit(BaseModel):
    guanyador: GuanyadorPerdedor
    perdedor: Optional[GuanyadorPerdedor] = None
    metode: str
    tipus_submissio: str
    resum_breu: str


class TimelineEvent(BaseModel):
    inici: str
    fi: str
    posicio: str
    controlador: str
    tipus_event: str
    descripcio: str
    rellevancia: int = Field(ge=1, le=5)
    confianca: Confianca


class TempsPosicio(BaseModel):
    lluitador: str
    posicio: str
    segons: int
    dominant: bool


class EstadistiquesEstimades(BaseModel):
    temps_per_posicio: List[TempsPosicio]

    temps_dominant_total: Optional[Union[int, Dict[str, int]]] = None
    temps_defensiu_total: Optional[Union[int, Dict[str, int]]] = None
    temps_neutral_total: Optional[int] = None

    canvis_control: int = 0
    intents_finalitzacio: Union[int, Dict[str, int]] = 0
    intents_enderroc: Union[int, Dict[str, int]] = 0
    guard_pulls: Union[int, Dict[str, int]] = 0
    reversions: Optional[Union[int, Dict[str, int]]] = None
    escapades: Optional[Union[int, Dict[str, int]]] = None


class EstadistiquesDerivades(BaseModel):
    temps_per_posicio: List[TempsPosicio]
    temps_dominant_per_lluitador: Dict[str, int]
    canvis_control_recalculats: int


class AnalisiLluitador(BaseModel):
    resum_personal: Optional[str] = None
    resum_tecnic: Optional[str] = None
    tactica_general: Optional[str] = None
    model_de_combat: Optional[str] = None
    lectura_posicional: Optional[str] = None

    patrons_tactics: List[str] = []
    fortaleses_clau: List[str] = []
    debilitats_clau: List[str] = []

    errors_i_correccions: List[Any] = []
    encerts_clau: List[Any] = []
    millores_recomanades: List[Any] = []
    prioritats_de_treball: List[Any] = []


class AnalisiOponent(BaseModel):
    tactica_general: str = ""
    model_de_combat: Optional[str] = None
    lectura_posicional: Optional[str] = None

    patrons_tactics: List[str] = []
    fortaleses_clau: List[str] = []
    debilitats_clau: List[str] = []

    errors_principals: List[Any] = []
    encerts_clau: List[Any] = []

    resum_rendiment: Optional[str] = None


class AnalisiOponents(BaseModel):
    oponent_1: AnalisiOponent
    oponent_2: AnalisiOponent


class LecturaGlobal(BaseModel):
    dinamica_general: str = ""
    moments_decisius: List[str] = []
    lliçons_practiques: Optional[List[str]] = None
    claus_tactiques: Optional[List[str]] = None


class AnalysisBaseResponse(BaseModel):
    mode: AnalysisMode
    perfil: UserProfile
    analysis_type: AnalysisType
    selected_oponent_id: OponentId

    combat_info: CombatInfo
    resum_partit: ResumPartit
    timeline: List[TimelineEvent]
    incerteses: List[str]


class AnalysisResponse(AnalysisBaseResponse):
    mode: Literal["full_fight"]
    selected_oponent_id: Literal["desconegut"]

    analisi_oponents: Optional[AnalisiOponents] = None
    lectura_global: Optional[LecturaGlobal] = None

    estadistiques_estimades: Optional[EstadistiquesEstimades] = None
    estadistiques_derivades: Optional[EstadistiquesDerivades] = None


class SingleAthleteAnalysisResponse(AnalysisBaseResponse):
    mode: Literal["single_athlete"]

    analisi_lluitador: AnalisiLluitador
    estadistiques_estimades: Optional[EstadistiquesEstimades] = None