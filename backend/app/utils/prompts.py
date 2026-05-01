def _analysis_type(profile: str, mode: str) -> str:
    mapping = {
        ("lluitador", "single_athlete"): "auto_analisi",
        ("lluitador", "full_fight"): "combat_lluitador",
        ("entrenador", "single_athlete"): "analisi_alumne",
        ("entrenador", "full_fight"): "combat_entrenador",
    }

    return mapping.get((profile, mode), "auto_analisi")


def build_prompt(
    profile: str,
    mode: str,
    athlete_identifier_type: str | None = None,
    athlete_identifier_value: str | None = None,
) -> str:
    profile = profile if profile in {"entrenador", "lluitador"} else "lluitador"
    mode = mode if mode in {"full_fight", "single_athlete"} else "single_athlete"

    analysis_type = _analysis_type(profile, mode)

    parts = [
        _base_rules(),
        _profile_rules(profile),
        _analysis_type_rules(analysis_type),
    ]

    if mode == "single_athlete":
        parts.extend(
            [
                _single_athlete_rules(
                    athlete_identifier_type,
                    athlete_identifier_value,
                ),
                _single_athlete_schema(profile),
            ]
        )
    else:
        parts.extend(
            [
                _full_fight_rules(),
                _full_fight_schema(profile),
            ]
        )

    return "\n".join(part.strip() for part in parts if part.strip())


def _base_rules() -> str:
    return """
Analitza aquest vídeo d’un combat de grappling.

Resposta:
- Retorna únicament un objecte JSON vàlid.
- Escriu tot el contingut textual en català.
- No incloguis cap text fora del JSON.
- No utilitzis Markdown ni blocs de codi.
- No afegeixis cap clau que no estigui definida a l’esquema.
- Inclou tots els camps obligatoris encara que el valor sigui "desconegut", "incert", "", 0, false o [].
- El JSON ha de ser parsejable sense errors.

Regles generals:
- Utilitza exclusivament informació observable al vídeo.
- No inventis noms, resultats, categories, normes, puntuacions ni intencions.
- No dedueixis emocions, nivell, experiència, lesió o cansament si no és visualment evident.
- Si una dada objectiva no es pot confirmar visualment, utilitza "desconegut".
- Si una interpretació és dubtosa, utilitza "incert".
- Si no hi ha evidència suficient per omplir una llista, utilitza [].
- Registra qualsevol dubte rellevant a "incerteses".
- Mantén coherència entre combat_info, resum_partit, timeline, estadistiques_estimades, patrons_globals i l’anàlisi principal.

Identificació dels oponents:
- Assigna sempre dos ids fixos: "oponent_1" i "oponent_2".
- Mantén el mateix id per al mateix lluitador durant tot el JSON.
- Cada oponent ha de tenir una "descripcio_visual" basada només en elements visibles.
- Si apareix clarament un nom al vídeo o marcador, posa’l a "nom_visible".
- Si no es veu cap nom, posa "desconegut".

Valors permesos per "posicio":
- standing
- closed_guard_top
- closed_guard_bottom
- open_guard_top
- open_guard_bottom
- half_guard_top
- half_guard_bottom
- side_control_top
- side_control_bottom
- mount_top
- mount_bottom
- back_control_top
- back_control_bottom
- turtle_top
- turtle_bottom
- scramble
- other

Valors permesos per "controlador":
- oponent_1
- oponent_2
- cap
- incert

Valors permesos per "tipus_event":
- inici_intercanvi
- control
- transicio
- intent_finalitzacio
- intent_enderroc
- guard_pull
- escape
- reversio
- scramble
- pausa
- finalitzacio
- altre

Valors permesos per "metode":
- submissio
- punts
- decisio
- avantatge
- desqualificacio
- desconegut

Valors permesos per "confianca":
- alta
- mitjana
- baixa

Definicions operatives:
- "control" implica estabilització clara d’una posició durant aproximadament 3 segons o més.
- "transicio" és un canvi de posició sense estabilització clara.
- "scramble" és una fase disputada o caòtica sense control definit.
- "intent_finalitzacio" exigeix una acció visible orientada a una submissió.
- "intent_enderroc" exigeix una acció clara per portar l’oponent a terra.
- "dominant" és true quan el lluitador controla activament la posició i false quan defensa, neutralitza o no hi ha control clar.

Regles del timeline:
- Segmenta el combat en trams consecutius i coherents.
- Cada tram ha de tenir "inici" i "fi" en format MM:SS.
- Els temps són relatius a l’inici del vídeo analitzat.
- No pot haver-hi solapaments.
- Els trams han de cobrir tota la seqüència analitzada.
- Cada tram ha de tenir una sola "posicio" principal.
- Si la fase és ambigua o transitòria, utilitza "scramble" o "other".
- "rellevancia" ha de ser un enter entre 1 i 5.
- "confianca" ha de ser "alta", "mitjana" o "baixa".
- Si hi ha tall de càmera, obstacle visual o pèrdua parcial de l’acció, marca confiança baixa o mitjana i explica-ho a "incerteses".

Límits de sortida:
- timeline: 5-20 trams.
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
"""


def _profile_rules(profile: str) -> str:
    if profile == "entrenador":
        return """
Perfil de sortida: entrenador.

Enfocament:
- llenguatge tècnic, precís i objectiu.
- estructura clara.
- patrons transferibles a entrenament.
- relacions causa-efecte.
- lectura tàctica i posicional.
- recomanacions útils per planificar sessions.

Evita:
- parlar directament al lluitador.
- to emocional o motivacional.
- recomanacions genèriques.
"""

    return """
Perfil de sortida: lluitador.

Enfocament:
- llenguatge directe.
- frases curtes.
- accions concretes.
- què repetir i què evitar.
- decisions immediates.
- ús de tècnica només quan sigui útil.

Evita:
- explicacions massa abstractes.
- to acadèmic.
- recomanacions vagues.
"""


def _analysis_type_rules(analysis_type: str) -> str:
    if analysis_type == "auto_analisi":
        return """
Tipus d’anàlisi: auto_analisi.

Objectiu:
- Analitzar el rendiment del lluitador seleccionat com si fos la persona que rep l’informe.

Regles:
- Parla al lluitador en segona persona.
- Centra’t en què ha fet bé, què ha de corregir i què ha de repetir.
- Les millores han de ser directes, concretes i aplicables.
- Relaciona cada error important amb una conseqüència observable.
- Prioritza decisions, timing, control posicional i gestió del risc.

Evita:
- analitzar els dos lluitadors per igual.
- parlar de manera impersonal.
- fer recomanacions genèriques.
"""

    if analysis_type == "combat_lluitador":
        return """
Tipus d’anàlisi: combat_lluitador.

Objectiu:
- Analitzar el combat complet amb una lectura pràctica per a un lluitador.

Regles:
- Dona una visió global del combat.
- Prioritza decisions immediates, riscos, oportunitats i moments clau.
- Explica quines accions haurien estat útils en situacions concretes.
- Mantén l’anàlisi clara, directa i accionable.

Evita:
- anàlisi excessivament acadèmica.
- estadística sense aplicació pràctica.
- recomanacions pensades només per a entrenadors.
"""

    if analysis_type == "analisi_alumne":
        return """
Tipus d’anàlisi: analisi_alumne.

Objectiu:
- Analitzar el rendiment del lluitador seleccionat per a un entrenador.

Regles:
- Parla sobre el lluitador en tercera persona.
- Prioritza patrons tècnics i tàctics repetibles.
- Relaciona errors amb causes observables.
- Distingueix errors puntuals de patrons repetits.
- Dona recomanacions transferibles a sessions d’entrenament.

Evita:
- parlar directament al lluitador.
- to motivacional.
- correccions superficials.
"""

    return """
Tipus d’anàlisi: combat_entrenador.

Objectiu:
- Analitzar el combat complet de manera equilibrada i tècnica.

Regles:
- Analitza els dos lluitadors amb pes similar.
- Prioritza dinàmiques globals, fases del combat i moments decisius.
- Identifica patrons tàctics i posicionals de cada oponent.
- Les recomanacions han de derivar de patrons observables.

Evita:
- focalitzar l’informe en un únic lluitador.
- donar instruccions directes tipus coaching individual.
- sobreinterpretar intencions.
"""


def _full_fight_rules() -> str:
    return """
Mode d’anàlisi: full_fight.

Regles:
- "mode" ha de ser "full_fight".
- "selected_oponent_id" ha de ser "desconegut".
- Analitza els dos lluitadors de manera equilibrada.
- Completa "analisi_oponents" amb els dos oponents.
- Reparteix fortaleses, debilitats, errors i encerts segons evidència visual.
- "resum_breu" ha de descriure el desenvolupament global del combat.
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
- "selected_oponent_id" ha de ser "oponent_1", "oponent_2" o "desconegut".
- L’anàlisi principal ha d’estar centrada en el lluitador seleccionat.
- Retorna obligatòriament "analisi_lluitador".
- No retornis "analisi_oponents".
- L’altre lluitador només s’ha d’esmentar quan sigui necessari per entendre l’acció.
- Errors, encerts, fortaleses, debilitats i millores han de correspondre al lluitador seleccionat.
- "resum_breu" ha de descriure sobretot el rendiment del lluitador seleccionat.
- "patrons_globals" ha de resumir patrons útils per futurs combats.
- A "temps_per_posicio", prioritza files del lluitador seleccionat.

Si no pots identificar-lo amb seguretat:
- posa "selected_oponent_id": "desconegut".
- omple igualment "analisi_lluitador" amb el candidat més probable.
- marca confiança baixa quan calgui.
- explica la incertesa a "incerteses".
"""


def _analysis_block_schema() -> str:
    return """
{
  "tactica_general": "string",
  "patrons_tactics": ["string"],
  "fortaleses_clau": ["string"],
  "debilitats_clau": ["string"],
  "errors_detallats": [
    {
      "error": "string",
      "moment_aproximat": "MM:SS",
      "impacte": "string"
    }
  ],
  "encerts_clau": [
    {
      "encert": "string",
      "moment_aproximat": "MM:SS",
      "impacte": "string"
    }
  ],
  "sequencies_repetides": ["string"],
  "millores_recomanades": [
    {
      "millora": "string",
      "objectiu": "string",
      "benefici_esperat": "string"
    }
  ]
}
""".strip()


def _common_schema_start(mode: str) -> str:
    selected = "desconegut" if mode == "full_fight" else "oponent_1|oponent_2|desconegut"

    return f"""
{{
  "mode": "{mode}",
  "selected_oponent_id": "{selected}",
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
    "metode": "submissio|punts|decisio|avantatge|desqualificacio|desconegut",
    "tipus_submissio": "string|desconegut",
    "resum_breu": "string"
  }},
  "timeline": [
    {{
      "inici": "MM:SS",
      "fi": "MM:SS",
      "posicio": "standing",
      "controlador": "oponent_1|oponent_2|cap|incert",
      "tipus_event": "inici_intercanvi|control|transicio|intent_finalitzacio|intent_enderroc|guard_pull|escape|reversio|scramble|pausa|finalitzacio|altre",
      "descripcio": "string",
      "rellevancia": 1,
      "confianca": "alta|mitjana|baixa"
    }}
  ],
"""


def _common_schema_end(profile: str) -> str:
    return f"""
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
"""


def _full_fight_schema(profile: str) -> str:
    block = _analysis_block_schema()

    return f"""
Format exacte de sortida:
{_common_schema_start("full_fight")}
  "analisi_oponents": {{
    "oponent_1": {block},
    "oponent_2": {block}
  }},
{_common_schema_end(profile)}

Restriccions finals:
- No incloguis "analisi_lluitador".
- Inclou obligatòriament "analisi_oponents".
- "mode" ha de ser exactament "full_fight".
- "selected_oponent_id" ha de ser exactament "desconegut".
- "perfil" ha de ser exactament "{profile}".
"""


def _single_athlete_schema(profile: str) -> str:
    block = _analysis_block_schema()

    return f"""
Format exacte de sortida:
{_common_schema_start("single_athlete")}
  "analisi_lluitador": {block},
{_common_schema_end(profile)}

Restriccions finals:
- No incloguis "analisi_oponents".
- Inclou obligatòriament "analisi_lluitador".
- "mode" ha de ser exactament "single_athlete".
- "selected_oponent_id" ha de ser "oponent_1", "oponent_2" o "desconegut".
- "perfil" ha de ser exactament "{profile}".
"""