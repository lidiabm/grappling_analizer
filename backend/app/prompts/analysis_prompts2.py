#analysis_prompts2.py

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
- Excepció obligatòria: els camps "millores_recomanades" i "prioritats_de_treball" no poden ser [] quan apareixen a l'esquema.
- Està prohibit escriure "No hi ha millores recomanades" o textos equivalents.
- Si no hi ha errors greus observables, genera una millora de refinament tècnic basada en el patró observable més clar.
- El JSON ha de ser parsejable sense errors.

Principi general:
- Utilitza només informació visualment verificable.
- Si no és clar: "desconegut" o "incert".
- No assumeixis resultats ni control si no es veu completament.
- Registra dubtes a "incerteses".

Identificació dels oponents:
- Assigna sempre dos ids fixos: "oponent_1" i "oponent_2".
- Mantén el mateix id per al mateix lluitador durant tot el JSON.
- Cada oponent ha de tenir una "descripcio_visual" basada només en elements visibles.
- Si apareix clarament un nom al vídeo o marcador, posa'l a "nom_visible".
- Si no es veu cap nom, posa "desconegut".

Valors permesos:
- posicio: standing | closed_guard | open_guard | half_guard | side_control | mount | back_control | turtle | scramble | other
- controlador: oponent_1 | oponent_2 | desconegut
- tipus_event: inici_intercanvi | control | transicio | intent_finalitzacio | intent_enderroc | guard_pull | escape | reversio | scramble | pausa | finalitzacio | avantatge_posicional | altre
- metode: submissio | punts | decisio | avantatge | desqualificacio | desconegut
- tipus_submissio: estrangulacio | armbar | triangle | kimura | americana | leg_lock | ankle_lock | heel_hook | kneebar | toe_hold | guillotine | rear_naked_choke | omoplata | altra | desconegut
- confiança: alta | mitjana | baixa

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

Regles per "tipus_submissio":
- Només si metode = "submissio".
- Si no és visible: "desconegut".


Definicions operatives:
- "control" implica estabilització clara d'una posició durant aproximadament 3 segons o més.
- "transicio" és un canvi de posició sense estabilització clara.
- "scramble" és una fase disputada o caòtica sense control definit.
- "intent_finalitzacio" exigeix una acció visible orientada a una submissió.
- "intent_enderroc" exigeix una acció clara per portar l'oponent a terra.
- "avantatge_posicional" és una millora clara de control o estructura sense estabilització completa ni finalització.

Timeline:
- Cobrir tota la durada sense buits ni solapaments.
- Segments de 5–20s, excepte accions decisives.
- Un sol tipus_event i una sola posició per segment.
- Fusiona segments si la situació no canvia.
- Crea segment nou per: escape, reversió, finalització, guard_pull, intent_enderroc, intent_finalitzacio clar.
- El timeline és la font única d’estadístiques.

Criteris per evitar "other":
- "other" només si la posició no encaixa en cap categoria i no es pot determinar visualment.

Controlador:
- En neutral o scramble: "desconegut".
- En guardes: controlador = qui imposa l'acció principal.
- Només canvia si el domini real canvia.

Tipus d'event:
- guard_pull: acció voluntària d’asseure’s o portar el combat a guàrdia.
- intent_finalitzacio: atac visible de submissió.
- intent_enderroc: entrada clara per portar l’oponent a terra.
- escape: sortir d’una posició de control rival.
- reversio: passar de bottom a top amb control clar.
- control: estabilització ≥3s sense atac principal.
- transicio: canvi de posició sense estabilització.
- scramble: fase caòtica sense controlador.
- finalitzacio: submissió confirmada o final del combat.
- En un combat només pot existir un segment amb "finalitzacio".

Descripcions:
- Resumeix la fase, no microajustos.
- Inclou l’autor en accions comptables.
- rellevancia = 1–5; confiança = alta|mitjana|baixa.
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

Resultat personal obligatori:
- Abans d'escriure "analisi_lluitador", compara sempre:
  selected_oponent_id amb resum_partit.guanyador.id.
- Si selected_oponent_id == resum_partit.guanyador.id:
  "resum_personal" ha de començar exactament amb "Has guanyat el combat".
- Si selected_oponent_id != resum_partit.guanyador.id i resum_partit.guanyador.id no és "desconegut":
  "resum_personal" ha de començar exactament amb "Has perdut el combat".
- Si resum_partit.guanyador.id és "desconegut":
  "resum_personal" ha de començar exactament amb "No es pot confirmar si has guanyat o perdut".
- Està prohibit dir "Has guanyat" si selected_oponent_id no coincideix amb resum_partit.guanyador.id.
- Està prohibit dir "Has perdut" si selected_oponent_id coincideix amb resum_partit.guanyador.id.
- El resum ha de tenir 2 o 3 frases.
- La primera frase ha d'indicar el resultat.
- La segona frase ha d'explicar el moment que ha decidit el combat.
- Totes les accions atribuïdes a "tu" han de correspondre al selected_oponent_id, no al rival.

Coherència d'identitat:
- "analisi_lluitador" només pot analitzar el lluitador indicat per selected_oponent_id.
- Si selected_oponent_id és "oponent_1", qualsevol frase amb "tu", "has", "vas" o "el teu" ha de referir-se només a oponent_1.
- Si selected_oponent_id és "oponent_2", qualsevol frase amb "tu", "has", "vas" o "el teu" ha de referir-se només a oponent_2.

Camps de "analisi_lluitador":
- "resum_personal" ha de tenir 2 o 3 frases i ha de ser directe i personal.
- "patrons_tactics", "fortaleses_clau", "debilitats_clau" i "millores_recomanades" han de tenir mínim 1 element.
- "errors_i_correccions" i "encerts_clau" poden ser [] si no hi ha evidència clara.

Evita:
- analitzar els dos lluitadors per igual.
- parlar de manera impersonal.
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

Camps de "analisi_lluitador" — regla de completesa obligatòria:
- Cap camp de text pot quedar buit (""). Si no hi ha evidència suficient, escriu "sense evidència observable".
- Cap llista pot quedar buida ([]). Cada llista ha de tenir com a mínim un element.
  Si no hi ha evidència suficient per a un element concret, inclou un objecte amb els camps
  corresponents omplerts amb "sense evidència observable" o "desconegut" segons el tipus.
- Aquesta regla s'aplica a: "patrons_tactics", "fortaleses_clau", "debilitats_clau",
  "errors_i_correccions", "encerts_clau" i "prioritats_de_treball".

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

Millores obligatòries:
- Cada oponent dins "analisi_oponents" ha d'incloure com a mínim una entrada a "millores_recomanades".
- Està prohibit escriure "No hi ha millores recomanades".
- Si un oponent guanya clarament, proposa una millora de refinament tècnic basada en una situació observable.
- Si un oponent perd, proposa una millora relacionada amb la causa observable de la derrota.
- Cada millora ha de ser concreta, accionable i vinculada a una fase del combat.

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

Prioritats de treball obligatòries:
- Cada oponent dins "analisi_oponents" ha d'incloure com a mínim una entrada a "prioritats_de_treball".
- Està prohibit escriure "No hi ha millores recomanades".
- Si un oponent guanya clarament, proposa una prioritat de refinament tècnic basada en una situació observable.
- Si un oponent perd, proposa una prioritat vinculada a la causa observable de la derrota.
- Cada prioritat ha d'estar basada en una acció, patró o situació observable del timeline.

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
INVARIANTS D'ESTADÍSTIQUES (obligatoris):

1. La suma total de "segons" a temps_per_posicio = duracio_total_segons.
2. La suma de tots els "percentatge" = 100.0 ±1.0.
3. Cada interval temporal apareix exactament una vegada (sense solapaments ni buits).
4. Només el controlador genera files a temps_per_posicio; el lluitador defensiu no en genera.
5. En posicions neutrals (standing, scramble, other), "controlador" = "desconegut".
6. temps_dominant_total = suma dels segments on el controlador és oponent_1 o oponent_2.
7. Els totals d'accions_clau han de coincidir amb resum_accions.
8. Totes les estadístiques han de derivar exclusivament del timeline (prohibit inventar-ne).

DEFINICIONS PER AL RECOMPTE D'ACCIONS:
- intent_finalitzacio: qualsevol atac visible de submissió. "intents" = tots; "reeixits" = només els que acaben en finalització confirmada.
- intent_enderroc: entrada clara per portar l'oponent a terra. "intents" = tots; "reeixits" = només els que acaben amb l'oponent a terra.
- guard_pull: acció voluntària d’asseure’s o portar el combat a guàrdia.
- reversio: passar de posició inferior a superior amb control clar.
- escapada: sortir d’una posició de control rival cap a standing, guàrdia pròpia o scramble.
- Si l’autor no és clar, no comptis l’acció i registra-ho a "incerteses".
- Accions dins d’un scramble només es compten si l’iniciador és visualment clar.

PROCEDIMENT PER GENERAR LES ESTADÍSTIQUES:
1. Usa el timeline com a única font.
2. Suma tots els segments i verifica que coincideixen amb duracio_total_segons.
3. Calcula percentatges = (segons / duracio_total_segons) × 100.
4. Verifica que la suma de percentatges = 100 ±1%.
5. Calcula temps_dominant_total per a cada lluitador.
6. Recompte d'accions_clau per lluitador.
7. Verifica coherència amb resum_accions.
8. Si hi ha dubtes, marca-ho a incerteses i usa 0 o "desconegut".
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
  "millores_recomanades": [
    {
      "prioritat": "alta|mitjana|baixa",
      "millora": "string",
      "objectiu": "string",
      "benefici_esperat": "string"
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
  "prioritats_de_treball": [
    {
      "prioritat": "alta|mitjana|baixa",
      "area": "string",
      "problema_tecnic": "string",
      "objectiu": "string"
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
    "intents_finalitzacio": { "oponent_1": { "intents": 0, "reeixits": 0 }, "oponent_2": { "intents": 0, "reeixits": 0 } },
    "intents_enderroc":     { "oponent_1": { "intents": 0, "reeixits": 0 }, "oponent_2": { "intents": 0, "reeixits": 0 } },
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
    "tipus_submissio": "estrangulacio|armbar|triangle|kimura|americana|leg_lock|ankle_lock|heel_hook|kneebar|toe_hold|guillotine|rear_naked_choke|omoplata|altra|desconegut",
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