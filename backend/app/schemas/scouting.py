from typing import Any, List, Literal
from pydantic import BaseModel


class ScoutingRivalInfo(BaseModel):
    nom_visible: str
    descripcio_visual: str
    nivell_confianca_global: Literal["alta", "mitjana", "baixa"]


class InformeLluitadorScouting(BaseModel):
    amenaces_principals: List[str]
    debilitats_a_explotar: List[str]
    que_evitar: List[str]
    pla_combat: List[str]
    consells_clau: List[str]
    missatge_final: str


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


class ScoutingChartDatum(BaseModel):
    label: str
    valor: int | float | str


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
    incerteses: List[str]

    informe_lluitador: InformeLluitadorScouting | None = None
    informe_entrenador: InformeEntrenadorScouting | None = None

    estadistiques: Any | None = None
    grafics_suggerits: List[ScoutingChart] | None = None