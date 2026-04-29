def build_prompt(
    profile: str,
    mode: str,
    athlete_identifier_type: str | None = None,
    athlete_identifier_value: str | None = None,
) -> str:
    profile = profile if profile in {"entrenador", "lluitador"} else "lluitador"

    if mode == "single_athlete":
        return (
            _base_rules()
            + _profile_rules(profile)
            + _single_athlete_rules(
                athlete_identifier_type,
                athlete_identifier_value,
            )
            + _single_athlete_schema(profile)
        )

    return (
        _base_rules()
        + _profile_rules(profile)
        + _full_fight_rules()
        + _full_fight_schema(profile)
    )


def _base_rules() -> str:
    return """
Analitza aquest vídeo d’un combat de grappling.

Resposta:
- Retorna exclusivament JSON vàlid.
- Escriu sempre en català.
- No afegeixis text fora del JSON.
- No facis servir Markdown.
- No incloguis blocs de codi ni l’etiqueta json.
- No afegeixis claus fora de l’esquema.
- No ometis cap camp obligatori.

Regles generals:
- Utilitza només informació observable al vídeo.
- No inventis noms, resultats, categories, normes o intencions.
- Si una dada no es pot confirmar visualment, fes servir "desconegut", "incert" o una llista buida.
- Afegeix qualsevol dubte rellevant a "incerteses".
- Mantén coherència entre combat_info, resum_partit, timeline, estadistiques_estimades, patrons_globals i l’anàlisi principal.

Identificació dels oponents:
- Cada oponent ha de tenir un id fix: "oponent_1" o "oponent_2".
- Cada oponent ha de tenir una "descripcio_visual" basada en elements visibles.
- Si apareix clarament un nom al vídeo o marcador, posa’l a "nom_visible".
- Si no es veu cap nom, posa "desconegut".

Valors permesos:

posició:
- dret
- guàrdia_tancada_superior
- guàrdia_tancada_inferior
- guàrdia_oberta_superior
- guàrdia_oberta_inferior
- mitja_guàrdia_superior
- mitja_guàrdia_inferior
- control_lateral_superior
- control_lateral_inferior
- muntada_superior
- muntada_inferior
- control_d’esquena_superior
- control_d’esquena_inferior
- tortuga_superior
- tortuga_inferior
- scramble
- altre

controlador:
- oponent_1
- oponent_2
- cap
- incert

tipus_event:
- inici_intercanvi
- control
- transicio
- intent_finalitzacio
- intent_enderroc
- guard_pull
- escap
- reversio
- scramble
- pausa
- finalitzacio
- altre

metode:
- submissio
- punts
- decisio
- desconegut

confianca:
- alta
- mitjana
- baixa

Regles del timeline:
- Segmenta el combat en trams consecutius i coherents.
- Cada tram ha de tenir "inici" i "fi" en format MM:SS.
- No pot haver-hi solapaments.
- Els trams han de cobrir tota la seqüència analitzada.
- Cada tram ha de tenir una sola posició principal.
- Si la fase és ambigua o transitòria, fes servir "scramble" o "altre".
- "rellevancia": enter entre 1 i 5.
- "confianca": alta, mitjana o baixa.

Límits de sortida:
- timeline: 5–20 trams.
- patrons_tactics: màxim 5.
- fortaleses_clau: màxim 5.
- debilitats_clau: màxim 5.
- errors_detallats: màxim 5.
- encerts_clau: màxim 5.
- sequencies_repetides: màxim 5.
- millores_recomanades: màxim 5.
- dinamiques_clau: màxim 5.
- moments_decisius: màxim 5.
- resum_comparable: màxim 5.

Important:
- Els valors de l’esquema indiquen el format esperat.
- Substitueix sempre els exemples pel valor real observat.
"""

def _profile_rules(profile: str) -> str:
    if profile == "entrenador":
        return """
Perfil de sortida: entrenador.

Enfocament:
- llenguatge tècnic i precís
- estructura clara
- patrons transferibles
- relacions causa-efecte
- lectura tàctica objectiva

Evita:
- parlar directament al lluitador
- to emocional
- recomanacions genèriques
"""

    return """
Perfil de sortida: lluitador.

Enfocament:
- llenguatge directe
- frases curtes
- accions concretes
- què repetir i què evitar
- decisions immediates
- ús de tècnica només quan sigui útil

Evita:
- explicacions massa abstractes
- to acadèmic
- recomanacions vagues
"""


def _full_fight_rules() -> str:
    return """
Mode d’anàlisi: full_fight.

Regles:
- "mode" ha de ser "full_fight".
- "selected_oponent_id": "desconegut".
- Analitza els dos lluitadors de manera equilibrada.
- Dona una visió global del combat.
- Completa "analisi_oponents" amb els dos oponents.
- Reparteix fortaleses, debilitats, errors i encerts segons evidència visual.
- "resum_breu" ha de descriure el desenvolupament global.
- No incloguis "analisi_lluitador".
"""


def _single_athlete_rules(
    athlete_identifier_type: str | None,
    athlete_identifier_value: str | None,
) -> str:
    return f"""
Mode d’anàlisi: single_athlete.

Lluitador a analitzar:
- tipus_identificador: {athlete_identifier_type or "desconegut"}
- valor_identificador: {athlete_identifier_value or "desconegut"}

Regles:
- "mode" ha de ser "single_athlete".
- Identifica quin oponent correspon al lluitador indicat.
- "selected_oponent_id": oponent_1, oponent_2 o desconegut.
- L’anàlisi principal ha d’estar centrada en el lluitador seleccionat.
- No retornis "analisi_oponents".
- Retorna obligatòriament "analisi_lluitador".
- L’altre lluitador només s’esmenta quan calgui per entendre l’acció.
- Errors, encerts i millores han de ser del lluitador seleccionat.
- "resum_breu" ha de descriure sobretot el seu rendiment.
- "patrons_globals" ha de resumir patrons útils per futurs combats.
- A "temps_per_posicio", prioritza files del lluitador seleccionat.

Si no pots identificar-lo amb seguretat:
- posa "selected_oponent_id": "desconegut"
- omple igualment "analisi_lluitador" amb el candidat més probable
- marca confiança baixa quan calgui
- explica la incertesa a "incerteses"
"""


def _full_fight_schema(profile: str) -> str:
    return f"""
Format exacte de sortida:
{{
  "mode": "full_fight",
  "selected_oponent_id": "desconegut",
  "combat_info": {{
    "oponents": [
      {{
        "id": "oponent_1",
        "nom_visible": "string",
        "descripcio_visual": "string"
      }},
      {{
        "id": "oponent_2",
        "nom_visible": "string",
        "descripcio_visual": "string"
      }}
    ],
    "durada_estimada": "MM:SS",
    "nivell_confianca_global": "alta|mitjana|baixa"
  }},
  "resum_partit": {{
    "guanyador": {{
      "id": "oponent_1|oponent_2|desconegut",
      "descripcio": "string"
    }},
    "perdedor": {{
      "id": "oponent_1|oponent_2|desconegut",
      "descripcio": "string"
    }},
    "metode": "submissio|punts|decisio|desconegut",
    "tipus_submissio": "string|desconegut",
    "resum_breu": "string"
  }},
  "timeline": [
    {{
      "inici": "MM:SS",
      "fi": "MM:SS",
      "posicio": "standing",
      "controlador": "cap",
      "tipus_event": "inici_intercanvi",
      "descripcio": "string",
      "rellevancia": 1,
      "confianca": "alta|mitjana|baixa"
    }}
  ],
  "analisi_oponents": {{
    "oponent_1": {{
      "tactica_general": "string",
      "patrons_tactics": ["string"],
      "fortaleses_clau": ["string"],
      "debilitats_clau": ["string"],
      "errors_detallats": [
        {{
          "error": "string",
          "moment_aproximat": "MM:SS",
          "impacte": "string"
        }}
      ],
      "encerts_clau": [
        {{
          "encert": "string",
          "moment_aproximat": "MM:SS",
          "impacte": "string"
        }}
      ],
      "sequencies_repetides": ["string"],
      "millores_recomanades": [
        {{
          "millora": "string",
          "objectiu": "string",
          "benefici_esperat": "string"
        }}
      ]
    }},
    "oponent_2": {{
      "tactica_general": "string",
      "patrons_tactics": ["string"],
      "fortaleses_clau": ["string"],
      "debilitats_clau": ["string"],
      "errors_detallats": [
        {{
          "error": "string",
          "moment_aproximat": "MM:SS",
          "impacte": "string"
        }}
      ],
      "encerts_clau": [
        {{
          "encert": "string",
          "moment_aproximat": "MM:SS",
          "impacte": "string"
        }}
      ],
      "sequencies_repetides": ["string"],
      "millores_recomanades": [
        {{
          "millora": "string",
          "objectiu": "string",
          "benefici_esperat": "string"
        }}
      ]
    }}
  }},
  "estadistiques_estimades": {{
    "temps_per_posicio": [
      {{
        "lluitador": "oponent_1|oponent_2|desconegut",
        "posicio": "standing",
        "segons": 0,
        "dominant": false
      }}
    ],
    "canvis_control": 0,
    "intents_finalitzacio": 0,
    "intents_enderroc": 0,
    "guard_pulls": 0
  }},
  "patrons_globals": {{
    "dinamiques_clau": ["string"],
    "moments_decisius": ["string"],
    "resum_comparable": ["string"]
  }},
  "incerteses": ["string"],
  "perfil": "{profile}"
}}

Restriccions finals:
- No incloguis "analisi_lluitador".
- "perfil" ha de ser exactament "{profile}".
"""


def _single_athlete_schema(profile: str) -> str:
    return f"""
Format exacte de sortida:
{{
  "mode": "single_athlete",
  "selected_oponent_id": "oponent_1|oponent_2|desconegut",
  "combat_info": {{
    "oponents": [
      {{
        "id": "oponent_1",
        "nom_visible": "string",
        "descripcio_visual": "string"
      }},
      {{
        "id": "oponent_2",
        "nom_visible": "string",
        "descripcio_visual": "string"
      }}
    ],
    "durada_estimada": "MM:SS",
    "nivell_confianca_global": "alta|mitjana|baixa"
  }},
  "resum_partit": {{
    "guanyador": {{
      "id": "oponent_1|oponent_2|desconegut",
      "descripcio": "string"
    }},
    "perdedor": {{
      "id": "oponent_1|oponent_2|desconegut",
      "descripcio": "string"
    }},
    "metode": "submissio|punts|decisio|desconegut",
    "tipus_submissio": "string|desconegut",
    "resum_breu": "string"
  }},
  "timeline": [
    {{
      "inici": "MM:SS",
      "fi": "MM:SS",
      "posicio": "standing",
      "controlador": "cap",
      "tipus_event": "inici_intercanvi",
      "descripcio": "string",
      "rellevancia": 1,
      "confianca": "alta|mitjana|baixa"
    }}
  ],
  "analisi_lluitador": {{
    "tactica_general": "string",
    "patrons_tactics": ["string"],
    "fortaleses_clau": ["string"],
    "debilitats_clau": ["string"],
    "errors_detallats": [
      {{
        "error": "string",
        "moment_aproximat": "MM:SS",
        "impacte": "string"
      }}
    ],
    "encerts_clau": [
      {{
        "encert": "string",
        "moment_aproximat": "MM:SS",
        "impacte": "string"
      }}
    ],
    "sequencies_repetides": ["string"],
    "millores_recomanades": [
      {{
        "millora": "string",
        "objectiu": "string",
        "benefici_esperat": "string"
      }}
    ]
  }},
  "estadistiques_estimades": {{
    "temps_per_posicio": [
      {{
        "lluitador": "oponent_1|oponent_2|desconegut",
        "posicio": "standing",
        "segons": 0,
        "dominant": false
      }}
    ],
    "canvis_control": 0,
    "intents_finalitzacio": 0,
    "intents_enderroc": 0,
    "guard_pulls": 0
  }},
  "patrons_globals": {{
    "dinamiques_clau": ["string"],
    "moments_decisius": ["string"],
    "resum_comparable": ["string"]
  }},
  "incerteses": ["string"],
  "perfil": "{profile}"
}}

Restriccions finals:
- No incloguis "analisi_oponents".
- El camp principal d’anàlisi ha de ser només "analisi_lluitador".
- "perfil" ha de ser exactament "{profile}".
"""