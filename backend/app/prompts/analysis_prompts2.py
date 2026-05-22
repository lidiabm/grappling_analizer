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

    if analysis_type == "auto_analisi":
        parts = [
            _base_rules(),
            _profile_rules(profile),
            _auto_analisi_rules(athlete_identifier_type, athlete_identifier_value),
            _single_athlete_schema(profile),
        ]

    elif analysis_type == "analisi_alumne":
        parts = [
            _base_rules(),
            _profile_rules(profile),
            _alumne_analisi_rules(athlete_identifier_type, athlete_identifier_value),
            _stats_invariants(),
            _single_athlete_schema(profile),
        ]

    elif analysis_type == "combat_lluitador":
        parts = [
            _base_rules(),
            _profile_rules(profile),
            _combat_lluitador_rules(),
            _full_fight_schema(profile),
        ]

    elif analysis_type == "combat_entrenador":
        parts = [
            _base_rules(),
            _profile_rules(profile),
            _combat_entrenador_rules(),
            _stats_invariants(),
            _full_fight_schema(profile),
        ]

    else:
        raise ValueError(f"Tipus d'anàlisi no implementat: {analysis_type}")

    return "\n".join(part.strip() for part in parts if part.strip())


# ─────────────────────────────────────────────
# BASE
# ─────────────────────────────────────────────

def _base_rules() -> str:
    return """
Analitza aquest vídeo d'un combat de grappling.

Resposta:
- Retorna únicament un objecte JSON vàlid.
- Escriu tot el contingut textual en català.
- No incloguis cap text fora del JSON.
- No utilitzis Markdown ni blocs de codi.
- No afegeixis cap clau que no estigui definida a l'esquema.
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
- Mantén coherència entre tot el JSON.
- Si una acció no és visible completament, no assumeixis el resultat.
- Si la càmera talla una transició, no dedueixis estabilització.
- No interpretis grips parcials com control consolidat.

Identificació dels oponents:
- Assigna sempre dos ids fixos: "oponent_1" i "oponent_2".
- Mantén el mateix id per al mateix lluitador durant tot el JSON.
- Cada oponent ha de tenir una "descripcio_visual" basada només en elements visibles.
- Si apareix clarament un nom al vídeo o marcador, posa'l a "nom_visible".
- Si no es veu cap nom, posa "desconegut".

Valors permesos per "posicio":
- standing
- closed_guard
- open_guard
- half_guard
- side_control
- mount
- back_control
- turtle
- scramble
- other

Valors permesos per "controlador":
- oponent_1
- oponent_2
- desconegut

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
- avantatge_posicional
- altre

Prioritat de classificació de "tipus_event":
1. finalitzacio
2. intent_finalitzacio
3. intent_enderroc
4. reversio
5. escape
6. guard_pull
7. control
8. transicio
9. scramble
10. avantatge_posicional
11. inici_intercanvi
12. altre

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
- "control" implica estabilització clara d'una posició durant aproximadament 3 segons o més.
- "transicio" és un canvi de posició sense estabilització clara.
- "scramble" és una fase disputada o caòtica sense control definit.
- "intent_finalitzacio" exigeix una acció visible orientada a una submissió.
- "intent_enderroc" exigeix una acció clara per portar l'oponent a terra.
- "controlador" és el lluitador que controla activament la situació durant el segment.
- En posicions neutrals o sense control clar, utilitza "desconegut".
- "avantatge_posicional" és una millora clara de control o estructura sense estabilització completa ni finalització.

Regles del timeline:
- Segmenta el combat en trams consecutius i coherents.
- Cada tram ha de tenir "inici" i "fi" en format MM:SS.
- Els temps són relatius a l'inici del vídeo analitzat.
- No pot haver-hi solapaments.
- Els trams han de cobrir tota la seqüència analitzada.
- Cada tram ha de tenir una sola "posicio" principal.
- Si la fase és ambigua o transitòria, utilitza "scramble" o "other".
- "rellevancia" ha de ser un enter entre 1 i 5.
- "confianca" ha de ser "alta", "mitjana" o "baixa".
- Si hi ha tall de càmera, obstacle visual o pèrdua parcial de l'acció, marca confiança baixa o mitjana i explica-ho a "incerteses".
- El "inici" d'un segment ha de coincidir amb el "fi" del segment anterior.
- No poden existir buits temporals entre segments.
"""


# ─────────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# REGLES D'ANÀLISI
# ─────────────────────────────────────────────

def _auto_analisi_rules(
    athlete_identifier_type: str | None,
    athlete_identifier_value: str | None,
) -> str:
    return f"""
Lluitador a analitzar:
- tipus_identificador: {athlete_identifier_type or "desconegut"}
- valor_identificador: {athlete_identifier_value or "desconegut"}

Objectiu:
- Analitzar el rendiment del lluitador seleccionat com si fos la persona que rep l'informe.

Regles:
- "mode" ha de ser exactament "single_athlete".
- "perfil" ha de ser exactament "lluitador".
- Identifica quin oponent correspon al lluitador indicat.
- "selected_oponent_id" ha de ser "oponent_1", "oponent_2" o "desconegut".
- Parla al lluitador en segona persona.
- Centra't en què has fet bé, què has de corregir i què has de repetir.
- Les millores han de ser accions concretes.
- Relaciona cada correcció amb una conseqüència observable.
- L'altre lluitador només s'ha d'esmentar quan sigui necessari per entendre l'acció.

Coherència d'identitat:
- Si "selected_oponent_id" és "oponent_1", totes les frases de "analisi_lluitador" han de referir-se a "oponent_1".
- Si "selected_oponent_id" és "oponent_2", totes les frases de "analisi_lluitador" han de referir-se a "oponent_2".
- No atribueixis accions de l'altre oponent al lluitador seleccionat.
- Si hi ha dubte sobre la identitat, posa "selected_oponent_id": "desconegut" i explica-ho a "incerteses".

Evita:
- analitzar els dos lluitadors per igual.
- parlar de manera impersonal.
- repetir la mateixa idea en diversos camps.
- fer recomanacions genèriques.
"""


def _alumne_analisi_rules(
    athlete_identifier_type: str | None,
    athlete_identifier_value: str | None,
) -> str:
    return f"""
Lluitador a analitzar:
- tipus_identificador: {athlete_identifier_type or "desconegut"}
- valor_identificador: {athlete_identifier_value or "desconegut"}

Objectiu:
- Generar una anàlisi tècnica del rendiment de l'alumne seleccionat per a un entrenador.

Regles:
- "mode" ha de ser exactament "single_athlete".
- "perfil" ha de ser exactament "entrenador".
- Identifica quin oponent correspon a l'alumne indicat.
- "selected_oponent_id" ha de ser "oponent_1", "oponent_2" o "desconegut".
- Escriu sobre l'alumne en tercera persona.
- No parlis directament a l'alumne.
- L'anàlisi tècnica textual ha d'estar centrada en l'alumne seleccionat.
- Les estadístiques han de cobrir sempre els dos oponents per permetre comparació.
- Prioritza lectura posicional, cadenes tècniques, patrons tàctics i relacions causa-efecte.
- Distingueix errors puntuals de patrons repetits.
- Relaciona cada error important amb una conseqüència observable.
- L'altre lluitador només s'ha d'esmentar quan sigui necessari per explicar una acció de l'alumne.

Criteri tècnic:
- Analitza control postural, gestió de distància, grips, frames, underhooks, inside position,
  pressió, timing, direcció de força, transicions, estabilització, escapes i exposició a
  finalitzacions quan siguin observables.
- En posicions superiors: valora consolidació, pressió, progressió i risc de reversió.
- En posicions inferiors: valora frames, retenció de guàrdia, recuperació, escapes i exposició.
- En scrambles: valora presa de decisions, orientació corporal i capacitat de sortir amb control.

Estadístiques:
- Inclou estadístiques estimades del combat complet per generar gràfics comparatius.
- Les estadístiques han de comparar sempre "oponent_1" i "oponent_2".
- Segueix estrictament els invariants i el procediment definits a la secció INVARIANTS.

Coherència d'identitat:
- Si "selected_oponent_id" és "oponent_1", totes les frases de "analisi_lluitador" han de referir-se a "oponent_1".
- Si "selected_oponent_id" és "oponent_2", totes les frases de "analisi_lluitador" han de referir-se a "oponent_2".
- "estadistiques_estimades" ha de comparar sempre "oponent_1" i "oponent_2", encara que l'anàlisi textual se centri en l'alumne seleccionat.
- No atribueixis accions de l'altre oponent a l'alumne seleccionat.
- Si hi ha dubte sobre la identitat, posa "selected_oponent_id": "desconegut" i explica-ho a "incerteses".

Evita:
- parlar en segona persona.
- donar consells motivacionals.
- fer recomanacions genèriques.
- analitzar els dos lluitadors per igual en l'anàlisi textual.
- incloure estadístiques que no siguin estimables a partir del vídeo.
"""


def _combat_lluitador_rules() -> str:
    return """
Objectiu:
- Generar una anàlisi general del combat complet per a un lluitador.

Regles:
- "mode" ha de ser exactament "full_fight".
- "perfil" ha de ser exactament "lluitador".
- "selected_oponent_id" ha de ser exactament "desconegut".
- Analitza els dos lluitadors de manera equilibrada.
- Inclou una lectura tàctica general dels dos oponents.
- Mantén l'anàlisi més simple i accionable que en el perfil d'entrenador.
- Dona importància a decisions, oportunitats, riscos, errors clars i accions útils per competir millor.
- L'anàlisi de cada oponent ha de ser breu: no entris en el mateix nivell de detall que en single_athlete.
- No incloguis estadístiques.
- No incloguis "analisi_lluitador".

Evita:
- centrar l'anàlisi només en un lluitador.
- fer una anàlisi excessivament acadèmica.
- incloure estadístiques.
- recomanacions massa generals.
"""


def _combat_entrenador_rules() -> str:
    return """
Objectiu:
- Generar una anàlisi general i tècnica del combat complet per a un entrenador.

Regles:
- "mode" ha de ser exactament "full_fight".
- "perfil" ha de ser exactament "entrenador".
- "selected_oponent_id" ha de ser exactament "desconegut".
- Analitza els dos lluitadors de manera equilibrada.
- Inclou una anàlisi general de cada oponent: tàctica, patrons, fortaleses, debilitats, errors principals i encerts.
- Mantén l'anàlisi menys profunda que en mode single_athlete.
- Prioritza dinàmica global del combat, control posicional, patrons repetits i moments decisius.
- Inclou estadístiques estimades del combat complet per generar gràfics comparatius.
- No parlis directament a cap lluitador.
- No incloguis "analisi_lluitador".

Estadístiques:
- Inclou estadístiques estimades del combat complet per generar gràfics comparatius.
- Les estadístiques han de comparar els dos oponents.
- Segueix estrictament els invariants i el procediment definits a la secció INVARIANTS.

Evita:
- focalitzar l'informe en un únic lluitador.
- fer recomanacions individuals massa detallades.
- convertir-ho en un pla d'entrenament.
- incloure estadístiques no estimables visualment.
"""


# ─────────────────────────────────────────────
# INVARIANTS D'ESTADÍSTIQUES
# ─────────────────────────────────────────────

def _stats_invariants() -> str:
    return """
INVARIANTS D'ESTADÍSTIQUES (el JSON és incorrecte si no es compleixen):

1. La suma de tots els "segons" dins "temps_per_posicio" ha de ser igual a "duracio_total_segons".
2. La suma de tots els "percentatge" ha de ser igual a 100.0 (tolerància ±1.0).
3. Cada interval temporal del combat apareix exactament una vegada a "temps_per_posicio".
4. Dues files no poden compartir el mateix interval temporal: PROHIBIT crear parelles mirall.
    PROHIBIT: duplicar el mateix interval temporal per als dos lluitadors.
    INCORRECTE:
    - oponent_1 side_control 20s
    - oponent_2 side_control 20s
    CORRECTE:
    { "controlador": "oponent_1", "posicio": "side_control", "segons": 20 }
5. Posicions controlades (closed_guard, open_guard, half_guard, side_control, mount, back_control, turtle)
6. Posicions neutrals (standing, scramble, other sense control clar): "controlador" és "desconegut".
7. El lluitador defensiu NO genera cap fila a "temps_per_posicio".
8. "resum_accions" ha de ser coherent amb el recompte de "accions_clau":
   el total de cada tipus per lluitador a "accions_clau" ha de coincidir amb "resum_accions".
9. "temps_dominant_total" ha de ser igual a la suma de tots els segments controlats per cada lluitador.
10. Les estadístiques han de derivar exclusivament del timeline.
No afegeixis informació estadística que no aparegui implícitament al timeline.

Definicions per al recompte d'accions:
- "intent_finalitzacio": qualsevol atac visible de submissió (estrangulació, armbar, triangle,
  kimura, americana, ankle lock, kneebar) o control clar orientat a finalitzar.
  Compta intents fallits i reeixits.
- "intent_enderroc": entrada clara per portar l'oponent a terra (single leg, double leg,
  body lock, foot sweep, snap down, projecció). Compta intents fallits i reeixits.
- "guard_pull": acció clara d'asseure's o portar el combat a guàrdia voluntàriament.
- "reversio": el lluitador passa de posició INFERIOR (bottom) a posició SUPERIOR (top).
  Exemple de frontera: recuperar guàrdia des de mount_bottom → és ESCAPADA, no reversió.
- "escapada": sortir d'una posició de control rival cap a standing, guàrdia pròpia o scramble.
  Nota: guàrdia pròpia és posició inferior però compta com a escapada si el rival tenia
  mount/back/side control.
- Si l'autor d'una acció no és visualment clar, no incrementis cap comptador i explica-ho a "incerteses".
- Si una acció passa dins d'un scramble, compta-la només si l'iniciador és visualment clar.

PROCEDIMENT OBLIGATORI abans de generar "estadistiques_estimades":
PAS 1: Usa el timeline com a única font per calcular les estadístiques.
PAS 2: Suma tots els segments del timeline i verifica que coincideixen amb "duracio_total_segons".
PAS 3: Calcula els percentatges amb la fórmula: (segons / duracio_total_segons) × 100.
PAS 4: Verifica que la suma dels percentatges sigui 100.0 amb una tolerància de ±1.0.
PAS 5: Calcula "temps_dominant_total" sumant els segments on "controlador" sigui "oponent_1" o "oponent_2".
PAS 6: Recorre "accions_clau" i compta cada tipus per lluitador.
PAS 7: Verifica que els totals de "accions_clau" coincideixin amb "resum_accions".
PAS 8: Si qualsevol valor és dubtós, afegeix-lo a "incerteses" i usa 0 o "desconegut".
PAS 9: Genera el JSON només després de completar aquestes comprovacions.
"""


# ─────────────────────────────────────────────
# SCHEMAS D'ANÀLISI TEXTUAL
# ─────────────────────────────────────────────

def _analisi_propi_schema() -> str:
    return """{
  "resum_personal": "string",
  "tactica_general": "string",
  "patrons_tactics": ["string"],
  "fortaleses_clau": ["string"],
  "debilitats_clau": ["string"],
  "errors_i_correccions": [
    {
      "error": "string",
      "moment_aproximat": "MM:SS",
      "consequencia": "string",
      "correccio": "string"
    }
  ],
  "encerts_clau": [
    {
      "encert": "string",
      "moment_aproximat": "MM:SS",
      "impacte": "string"
    }
  ],
  "millores_recomanades": [
    {
      "prioritat": "alta|mitjana|baixa",
      "millora": "string",
      "objectiu": "string",
      "benefici_esperat": "string"
    }
  ]
}"""


def _analisi_alumne_schema() -> str:
    return """{
  "resum_tecnic": "string",
  "model_de_combat": "string",
  "lectura_posicional": "string",
  "patrons_tactics": ["string"],
  "fortaleses_clau": ["string"],
  "debilitats_clau": ["string"],
  "errors_i_correccions": [
    {
      "error": "string",
      "moment_aproximat": "MM:SS",
      "fase": "standing|guard|passing|top_control|bottom_defense|back_control|scramble|submission|other",
      "consequencia": "string",
      "causa_tecnica_observable": "string",
      "correccio_tecnica": "string"
    }
  ],
  "encerts_clau": [
    {
      "encert": "string",
      "moment_aproximat": "MM:SS",
      "fase": "standing|guard|passing|top_control|bottom_defense|back_control|scramble|submission|other",
      "impacte": "string",
      "principi_tecnic": "string"
    }
  ],
  "prioritats_de_treball": [
    {
      "prioritat": "alta|mitjana|baixa",
      "area": "string",
      "problema_tecnic": "string",
      "objectiu": "string"
    }
  ]
}"""


def _analisi_oponent_general_schema() -> str:
    return """{
  "tactica_general": "string",
  "patrons_tactics": ["string"],
  "fortaleses_clau": ["string"],
  "debilitats_clau": ["string"],
  "errors_principals": [
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
  "resum_rendiment": "string"
}"""


def _analisi_oponent_general_entrenador_schema() -> str:
    return """{
  "tactica_general": "string",
  "model_de_combat": "string",
  "lectura_posicional": "string",
  "patrons_tactics": ["string"],
  "fortaleses_clau": ["string"],
  "debilitats_clau": ["string"],
  "errors_principals": [
    {
      "error": "string",
      "moment_aproximat": "MM:SS",
      "fase": "standing|guard|passing|top_control|bottom_defense|back_control|scramble|submission|other",
      "impacte": "string"
    }
  ],
  "encerts_clau": [
    {
      "encert": "string",
      "moment_aproximat": "MM:SS",
      "fase": "standing|guard|passing|top_control|bottom_defense|back_control|scramble|submission|other",
      "impacte": "string"
    }
  ],
  "resum_rendiment": "string"
}"""


# ─────────────────────────────────────────────
# SCHEMA D'ESTADÍSTIQUES (únic, reutilitzat)
# ─────────────────────────────────────────────

def _estadistiques_schema() -> str:
    return """{
  "duracio_total_segons": 0,

  "temps_per_posicio": [
    {
      "posicio": "standing|closed_guard|open_guard|half_guard|side_control|mount|back_control|turtle|scramble|other",
      "controlador": "oponent_1|oponent_2|desconegut",
      "segons": 0,
      "percentatge": 0.0
    }
  ],

  "temps_dominant_total": {
    "oponent_1": 0,
    "oponent_2": 0
  },

  "accions_clau": [
    {
      "temps": "MM:SS",
      "lluitador": "oponent_1|oponent_2",
      "tipus": "intent_finalitzacio|intent_enderroc|guard_pull|reversio|escapada",
      "detall": "string",
      "confianca": "alta|mitjana|baixa"
    }
  ],

  "resum_accions": {
    "intents_finalitzacio": { "oponent_1": 0, "oponent_2": 0 },
    "intents_enderroc":     { "oponent_1": 0, "oponent_2": 0 },
    "guard_pulls":          { "oponent_1": 0, "oponent_2": 0 },
    "reversions":           { "oponent_1": 0, "oponent_2": 0 },
    "escapades":            { "oponent_1": 0, "oponent_2": 0 },
    "canvis_control":       0
  }
}"""


# ─────────────────────────────────────────────
# SCHEMA D'INICI (compartit)
# ─────────────────────────────────────────────

def _schema_start(mode: str, profile: str) -> str:
    selected = "desconegut" if mode == "full_fight" else "oponent_1|oponent_2|desconegut"

    return f"""{{
  "mode": "{mode}",
  "perfil": "{profile}",
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
      "controlador": "oponent_1|oponent_2|desconegut",
      "tipus_event": "inici_intercanvi|control|transicio|intent_finalitzacio|intent_enderroc|guard_pull|escape|reversio|scramble|pausa|finalitzacio|altre",
      "descripcio": "string",
      "rellevancia": 1,
      "confianca": "alta|mitjana|baixa"
    }}
  ],"""


# ─────────────────────────────────────────────
# SCHEMAS DE SORTIDA FINALS
# ─────────────────────────────────────────────

def _single_athlete_schema(profile: str) -> str:
    if profile == "lluitador":
        return f"""
Format exacte de sortida:
{_schema_start("single_athlete", profile)}
  "analisi_lluitador": {_analisi_propi_schema()},
  "incerteses": ["string"]
}}

Restriccions finals:
- Inclou obligatòriament "analisi_lluitador".
- No afegeixis cap camp fora d'aquest esquema.
"""

    if profile == "entrenador":
        return f"""
Format exacte de sortida:
{_schema_start("single_athlete", profile)}
  "analisi_lluitador": {_analisi_alumne_schema()},
  "estadistiques_estimades": {_estadistiques_schema()},
  "incerteses": ["string"]
}}

Restriccions finals:
- Inclou obligatòriament "analisi_lluitador".
- Inclou obligatòriament "estadistiques_estimades".
- L'anàlisi tècnica textual ha d'estar centrada en l'alumne seleccionat.
- Les estadístiques han de cobrir sempre els dos oponents per permetre comparació.
- No afegeixis cap camp fora d'aquest esquema.
"""
    return ""


def _full_fight_schema(profile: str) -> str:
    if profile == "lluitador":
        block = _analisi_oponent_general_schema()

        return f"""
Format exacte de sortida:
{_schema_start("full_fight", profile)}
  "analisi_oponents": {{
    "oponent_1": {block},
    "oponent_2": {block}
  }},
  "lectura_global": {{
    "dinamica_general": "string",
    "moments_decisius": ["string"],
    "lliçons_practiques": ["string"]
  }},
  "incerteses": ["string"]
}}

Restriccions finals:
- Inclou obligatòriament "analisi_oponents".
- Inclou obligatòriament "lectura_global".
- No incloguis "analisi_lluitador".
- No incloguis "estadistiques_estimades".
- "mode" ha de ser exactament "full_fight".
- "perfil" ha de ser exactament "lluitador".
- "selected_oponent_id" ha de ser exactament "desconegut".
- L'anàlisi dels oponents ha de ser general i més breu que en mode single_athlete.
- No afegeixis cap camp fora d'aquest esquema.
"""

    if profile == "entrenador":
        block = _analisi_oponent_general_entrenador_schema()

        return f"""
Format exacte de sortida:
{_schema_start("full_fight", profile)}
  "analisi_oponents": {{
    "oponent_1": {block},
    "oponent_2": {block}
  }},
  "estadistiques_estimades": {_estadistiques_schema()},
  "lectura_global": {{
    "dinamica_general": "string",
    "moments_decisius": ["string"],
    "claus_tactiques": ["string"]
  }},
  "incerteses": ["string"]
}}

Restriccions finals:
- Inclou obligatòriament "analisi_oponents".
- Inclou obligatòriament "estadistiques_estimades".
- Inclou obligatòriament "lectura_global".
- No incloguis "analisi_lluitador".
- "mode" ha de ser exactament "full_fight".
- "perfil" ha de ser exactament "entrenador".
- "selected_oponent_id" ha de ser exactament "desconegut".
- L'anàlisi dels oponents ha de ser general i menys profunda que en mode single_athlete.
- No afegeixis cap camp fora d'aquest esquema.
"""
    return ""