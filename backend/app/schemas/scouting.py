from typing import List, Literal
from pydantic import BaseModel

UnknownNumber = int | Literal["desconegut"]

class ScoutingRivalInfo(BaseModel):
    nom_visible: str
    descripcio_visual: str
    nivell_confianca_global: Literal["alta", "mitjana", "baixa", "insuficient"]


class InformeLluitadorScouting(BaseModel):
    amenaces_principals: List[str]
    debilitats_a_explotar: List[str]
    que_evitar: List[str]
    pla_combat: List[str]
    consells_clau: List[str]
    clau_tactica: str


class InformeEntrenadorScouting(BaseModel):
    model_de_combat: str
    patrons_ofensius: List[str]
    patrons_defensius: List[str]
    situacions_on_puntua: List[str]
    situacions_on_queda_exposat: List[str]
    pla_tactic_recomanat: List[str]
    focus_entrenament: List[str]
    exercicis_recomanats: List[str]
    riscos_principals: List[str]


class ScoutingPerVideoStats(BaseModel):
    video: int | str
    fitxer: str
    seguiment_rival: Literal["clar", "parcial", "incert"]
    atacs_iniciats: int | str
    atacs_efectius: int | str
    intents_passada_guardia: int | str
    passades_guardia_efectives: int | str
    raspades_intentades: int | str
    raspades_efectives: int | str
    submissions_intentades: int | str
    submissions_encaixades: int | str
    recuperacions_guardia: int | str
    perdues_posicio: int | str
    temps_dominant_aproximat: str
    situacions_mes_frequents: List[str]
    observacions: List[str]


class ScoutingGlobalStats(BaseModel):
    accions_mes_frequents: List[str]
    situacions_mes_repetides: List[str]
    zones_de_risc: List[str]
    tendencies_tactiques: List[str]
    patrons_amb_mes_evidencia: List[str]
    patrons_amb_poca_evidencia: List[str]


class ScoutingNumericProfile(BaseModel):
    pressio: int
    agressivitat: int
    control_posicional: int
    defensa: int
    perill_submissio: int
    explosivitat: int
    adaptabilitat: int


class ScoutingStats(BaseModel):
    nota: str
    nivell_fiabilitat_estadistica: Literal["alta", "mitjana", "baixa"]
    per_video: List[ScoutingPerVideoStats]
    resum_global: ScoutingGlobalStats
    perfil_numeric: ScoutingNumericProfile


class ScoutingChartDatum(BaseModel):
    label: str
    valor: int | float


class ScoutingChart(BaseModel):
    id: str
    tipus: str
    titol: str
    descripcio: str | None = None
    dades: List[ScoutingChartDatum]
    escala: str | None = None
    interpretacio: str | None = None


class ScoutingResponse(BaseModel):
    mode: Literal["scouting"]
    perfil: Literal["lluitador", "entrenador"]
    analysis_type: Literal["scouting_lluitador", "scouting_entrenador"]

    rival_info: ScoutingRivalInfo
    resum_rival: str
    patrons_recurrents: List[str]
    punts_forts: List[str]
    debilitats: List[str]

    informe_lluitador: InformeLluitadorScouting | None = None
    informe_entrenador: InformeEntrenadorScouting | None = None

    estadistiques: ScoutingStats | None = None
    grafics_suggerits: List[ScoutingChart] | None = None

    incerteses: List[str]