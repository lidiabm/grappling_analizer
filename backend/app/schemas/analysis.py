from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional


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
    nivell_confianca_global: Literal["alta", "mitjana", "baixa"]


class ResumPartit(BaseModel):
    guanyador: GuanyadorPerdedor
    perdedor: GuanyadorPerdedor
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
    confianca: Literal["alta", "mitjana", "baixa"]


class ErrorDetallat(BaseModel):
    error: str
    moment_aproximat: str
    impacte: str


class EncertClau(BaseModel):
    encert: str
    moment_aproximat: str
    impacte: str


class MilloraRecomanada(BaseModel):
    millora: str
    objectiu: str
    benefici_esperat: str


class AnalisiOponent(BaseModel):
    tactica_general: str
    patrons_tactics: List[str]
    fortaleses_clau: List[str]
    debilitats_clau: List[str]
    errors_detallats: List[ErrorDetallat]
    encerts_clau: List[EncertClau]
    sequencies_repetides: List[str]
    millores_recomanades: List[MilloraRecomanada]


class AnalisiOponents(BaseModel):
    oponent_1: AnalisiOponent
    oponent_2: AnalisiOponent


class TempsPosicio(BaseModel):
    lluitador: str
    posicio: str
    segons: int
    dominant: bool


class EstadistiquesEstimades(BaseModel):
    temps_per_posicio: List[TempsPosicio]
    canvis_control: int
    intents_finalitzacio: int
    intents_enderroc: int
    guard_pulls: int


class EstadistiquesDerivades(BaseModel):
    temps_per_posicio: List[TempsPosicio]
    temps_dominant_per_lluitador: Dict[str, int]
    canvis_control_recalculats: int


class PatronsGlobals(BaseModel):
    dinamiques_clau: List[str]
    moments_decisius: List[str]
    resum_comparable: List[str]


class AnalysisResponse(BaseModel):
    combat_info: CombatInfo
    resum_partit: ResumPartit
    timeline: List[TimelineEvent]
    analisi_oponents: AnalisiOponents
    estadistiques_estimades: EstadistiquesEstimades
    estadistiques_derivades: Optional[EstadistiquesDerivades] = None
    patrons_globals: PatronsGlobals
    incerteses: List[str]
    perfil: str