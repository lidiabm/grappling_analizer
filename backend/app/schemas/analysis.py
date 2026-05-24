#analysis.py

from typing import Any, Dict, List, Literal, Optional
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

Posicio = Literal[
    "standing",
    "closed_guard",
    "open_guard",
    "half_guard",
    "side_control",
    "mount",
    "back_control",
    "turtle",
    "scramble",
    "other",
]

Controlador = Literal["oponent_1", "oponent_2", "desconegut"]

TipusEvent = Literal[
    "inici_intercanvi",
    "control",
    "transicio",
    "intent_finalitzacio",
    "intent_enderroc",
    "guard_pull",
    "escape",
    "reversio",
    "scramble",
    "pausa",
    "finalitzacio",
    "avantatge_posicional",
    "altre",
]

AccioTipus = Literal[
    "intent_finalitzacio",
    "intent_enderroc",
    "guard_pull",
    "reversio",
    "escapada",
]


class AthleteIdentifier(BaseModel):
    type: Literal["visual_description", "screen_side", "corner"]
    value: str


class AnalysisRequest(BaseModel):
    profile: UserProfile
    mode: AnalysisMode
    athlete_identifier: Optional[AthleteIdentifier] = None


class GuanyadorPerdedor(BaseModel):
    id: OponentId
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
    posicio: Posicio
    controlador: Controlador
    tipus_event: TipusEvent
    descripcio: str
    rellevancia: int = Field(ge=1, le=5)
    confianca: Confianca


class TempsPosicio(BaseModel):
    posicio: Posicio
    controlador: Controlador
    segons: int = 0
    percentatge: float = 0.0


class AccioClau(BaseModel):
    temps: str
    lluitador: Literal["oponent_1", "oponent_2"]
    tipus: AccioTipus
    detall: str = ""
    confianca: Confianca


class ResumAccions(BaseModel):
    intents_finalitzacio: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    intents_enderroc: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    guard_pulls: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    reversions: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    escapades: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    canvis_control: int = 0


class EstadistiquesEstimades(BaseModel):
    duracio_total_segons: int = 0
    temps_per_posicio: List[TempsPosicio] = Field(default_factory=list)
    temps_dominant_total: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    accions_clau: List[AccioClau] = Field(default_factory=list)
    resum_accions: ResumAccions = Field(default_factory=ResumAccions)


class EstadistiquesDerivades(BaseModel):
    duracio_total_segons: int = 0
    temps_per_posicio: List[TempsPosicio] = Field(default_factory=list)
    temps_dominant_total: Dict[str, int] = Field(
        default_factory=lambda: {"oponent_1": 0, "oponent_2": 0}
    )
    accions_clau: List[AccioClau] = Field(default_factory=list)
    resum_accions: ResumAccions = Field(default_factory=ResumAccions)


class AnalisiLluitador(BaseModel):
    resum_personal: Optional[str] = None
    resum_tecnic: Optional[str] = None
    tactica_general: Optional[str] = None
    model_de_combat: Optional[str] = None
    lectura_posicional: Optional[str] = None

    patrons_tactics: List[str] = Field(default_factory=list)
    fortaleses_clau: List[str] = Field(default_factory=list)
    debilitats_clau: List[str] = Field(default_factory=list)

    errors_i_correccions: List[Any] = Field(default_factory=list)
    encerts_clau: List[Any] = Field(default_factory=list)
    millores_recomanades: List[Any] = Field(default_factory=list)
    prioritats_de_treball: List[Any] = Field(default_factory=list)


class AnalisiOponent(BaseModel):
    tactica_general: str = ""
    model_de_combat: Optional[str] = None
    lectura_posicional: Optional[str] = None

    patrons_tactics: List[str] = Field(default_factory=list)
    fortaleses_clau: List[str] = Field(default_factory=list)
    debilitats_clau: List[str] = Field(default_factory=list)

    errors_principals: List[Any] = Field(default_factory=list)
    encerts_clau: List[Any] = Field(default_factory=list)

    resum_rendiment: Optional[str] = None


class AnalisiOponents(BaseModel):
    oponent_1: AnalisiOponent
    oponent_2: AnalisiOponent


class LecturaGlobal(BaseModel):
    dinamica_general: str = ""
    moments_decisius: List[str] = Field(default_factory=list)
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
    incerteses: List[str] = Field(default_factory=list)


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