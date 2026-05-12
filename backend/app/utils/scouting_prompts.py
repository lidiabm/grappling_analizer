from typing import Any


def build_scouting_prompt(
    profile: str,
    video_descriptions: list[dict[str, Any]],
) -> str:
    profile = profile if profile in {"entrenador", "lluitador"} else "lluitador"

    video_context = _build_video_context(video_descriptions)

    if profile == "entrenador":
        return _coach_prompt(video_context)

    return _fighter_prompt(video_context)


def _build_video_context(video_descriptions: list[dict[str, Any]]) -> str:
    lines = []

    for item in video_descriptions:
        index = item.get("index", "?")
        filename = item.get("filename", "desconegut")
        rival_description = item.get("rival_description", "desconegut")

        try:
            video_number = int(index) + 1
        except Exception:
            video_number = index

        lines.append(
            f"- Vídeo {video_number}: fitxer '{filename}'. "
            f"Rival a analitzar: {rival_description}"
        )

    if not lines:
        return "- No s'han proporcionat descripcions dels vídeos."

    return "\n".join(lines)


def _base_rules(video_context: str) -> str:
    return f"""
Analitza diversos vídeos del mateix rival en un context de grappling.

Rival a analitzar en cada vídeo:
{video_context}

Resposta:
- Retorna únicament un objecte JSON vàlid.
- Escriu tot el contingut textual en català.
- No incloguis cap text fora del JSON.
- No utilitzis Markdown ni blocs de codi.
- El JSON ha de ser parsejable sense errors.

Objectiu:
- Analitzar només el rival indicat en cada vídeo.
- Detectar patrons recurrents entre vídeos.
- Diferenciar accions puntuals de patrons reals.
- Identificar punts forts, debilitats i riscos.
- Detectar hàbits tàctics repetits.
- Detectar situacions on el rival funciona millor.
- Detectar situacions on el rival queda exposat.

Regles:
- Utilitza només informació observable als vídeos.
- No inventis informació.
- Si no pots identificar clarament el rival descrit en un vídeo, indica-ho a "incerteses".
- Si un vídeo no permet seguir el rival amb seguretat, redueix la confiança global.
- Si alguna conclusió no és clara, posa-la a "incerteses".
- Si no hi ha evidència suficient per omplir un camp, utilitza [] o "desconegut".
"""


def _fighter_prompt(video_context: str) -> str:
    return (
        _base_rules(video_context)
        + """
Perfil de sortida: lluitador.

Objectiu:
- Generar un scouting pràctic i fàcil d’aplicar abans del combat.
- Parlar de manera clara i directa.
- Prioritzar decisions útils per competir.

Format exacte de sortida:

{
  "mode": "scouting",
  "perfil": "lluitador",
  "analysis_type": "scouting_lluitador",

  "rival_info": {
    "nom_visible": "string|desconegut",
    "descripcio_visual": "string|desconegut",
    "nivell_confianca_global": "alta|mitjana|baixa"
  },

  "resum_rival": "string",

  "patrons_recurrents": ["string"],

  "punts_forts": ["string"],

  "debilitats": ["string"],

  "informe_lluitador": {
    "amenaces_principals": ["string"],
    "debilitats_a_explotar": ["string"],
    "que_evitar": ["string"],
    "pla_combat": ["string"],
    "consells_clau": ["string"],
    "missatge_final": "string"
  },

  "incerteses": ["string"]
}
"""
    )


def _coach_prompt(video_context: str) -> str:
    return (
        _base_rules(video_context)
        + """
Perfil de sortida: entrenador.

Objectiu:
- Generar un informe tàctic útil per preparar un esportista.
- Utilitzar llenguatge tècnic i estructurat.
- Detectar patrons transferibles a entrenament.

Format exacte de sortida:

{
  "mode": "scouting",
  "perfil": "entrenador",
  "analysis_type": "scouting_entrenador",

  "rival_info": {
    "nom_visible": "string|desconegut",
    "descripcio_visual": "string|desconegut",
    "nivell_confianca_global": "alta|mitjana|baixa"
  },

  "resum_rival": "string",

  "patrons_recurrents": ["string"],

  "punts_forts": ["string"],

  "debilitats": ["string"],

  "informe_entrenador": {
    "model_de_combat": "string",
    "patrons_ofensius": ["string"],
    "patrons_defensius": ["string"],
    "situacions_on_puntua": ["string"],
    "situacions_on_queda_exposat": ["string"],
    "pla_tactic_recomanat": ["string"],
    "focus_entrenament": ["string"],
    "exercicis_recomanats": ["string"],
    "riscos_principals": ["string"]
  },

  "incerteses": ["string"]
}
"""
    )