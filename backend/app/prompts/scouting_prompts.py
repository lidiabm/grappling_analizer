from __future__ import annotations
from enum import Enum
from typing import Any

class ProfileType(str, Enum):
    """Perfils de sortida del scouting."""

    LLUITADOR = "lluitador"
    ENTRENADOR = "entrenador"

_MAX_LIST_ITEMS = 5  
_MAX_LIST_ITEMS_PLA = 3

# Punt d'entrada públic
def build_scouting_prompt(
    profile: str,
    video_descriptions: list[dict[str, Any]],
) -> str:
    """Construeix el prompt de scouting segons el perfil indicat.

    Args:
        profile: "lluitador" o "entrenador". Qualsevol altre valor
                 es tracta com a "lluitador" per defecte.
        video_descriptions: Llista de diccionaris amb les claus
          ``index``, ``filename``, ``rival_description`` i,
          opcionalment, ``rival_known_info`` (nom, pes, estil conegut).

    Returns:
        String amb el prompt complet llest per enviar al model.
    """
    try:
        profile_type = ProfileType(profile)
    except ValueError:
        profile_type = ProfileType.LLUITADOR

    video_context = _build_video_context(video_descriptions)
    num_videos = len(video_descriptions)

    builders = {
        ProfileType.LLUITADOR: _fighter_prompt,
        ProfileType.ENTRENADOR: _coach_prompt,
    }
    return builders[profile_type](video_context, num_videos)

# Construcció del context de vídeos
def _build_video_context(video_descriptions: list[dict[str, Any]]) -> str:
    """Converteix la llista de vídeos en un bloc de text estructurat per al prompt.

    Cada entrada té el format:
        - Vídeo N | fitxer: 'nom.mp4' | rival: <descripció>

    Si la llista és buida es retorna un missatge explícit.
    """
    if not video_descriptions:
        return "- No s'han proporcionat descripcions dels vídeos."

    lines: list[str] = []
    for item in video_descriptions:
        raw_index = item.get("index", "?")
        filename = item.get("filename", "desconegut")
        rival_description = item.get("rival_description", "desconegut")
        rival_known_info = item.get("rival_known_info", "")

        try:
            video_number = int(raw_index) + 1
        except (TypeError, ValueError):
            video_number = raw_index

        lines.append(
            f"- Vídeo {video_number} | fitxer: '{filename}' | rival: {rival_description}"
            + (f" | info prèvia: {rival_known_info}" if rival_known_info else "")
        )

    return "\n".join(lines)


# Regles base compartides
def _base_rules(video_context: str, num_videos: int) -> str:
    """Bloc de regles i instruccions comunes als dos perfils."""
    return f"""
Analitza el material proporcionat sobre un rival en un context de grappling.

Nombre real de vídeos proporcionats: {num_videos}

Vídeos proporcionats:
{video_context}

REGLA CRÍTICA SOBRE EL NOMBRE DE VÍDEOS
- Has rebut exactament {num_videos} vídeo(s). No n'inventis cap altre.
- No escriguis mai freqüències impossibles com "3 de 4 vídeos", "4 de 4 vídeos" o "en diversos vídeos" si només s'ha proporcionat 1 vídeo.
- Qualsevol referència quantitativa ha de respectar exactament el nombre real de vídeos proporcionats.

FORMAT DE SORTIDA 
- Retorna ÚNICAMENT un objecte JSON vàlid, sense cap text fora del JSON.
- No utilitzis Markdown, blocs de codi ni cap caràcter fora del JSON.
- Escriu tot el contingut textual en català.
- Respecta exactament l'estructura i l'ordre de claus indicat.
- No afegeixis camps addicionals fora del format especificat.

IDENTIFICACIÓ DEL RIVAL (CRÍTIC)
- El rival és EXCLUSIVAMENT la persona descrita a "rival_description" i/o "rival_known_info".
- El lluitador propi (l’esportista que rep l’informe) NO s’ha d’analitzar en cap cas.
- Si al vídeo apareixen dues persones i no és clar qui és el rival, assumeix que el rival és qui coincideix amb la descripció proporcionada.
- Si no es pot identificar amb seguretat, indica-ho a "incerteses" i redueix el nivell de confiança global.

OBJECTIU GENERAL 
- Analitza NOMÉS el rival indicat en cada vídeo.
- Tracta cada vídeo com una observació independent abans de sintetitzar.
- Si hi ha 2 o més vídeos, detecta patrons recurrents entre vídeos.
- Si només hi ha 1 vídeo, detecta només observacions limitades dins del vídeo.
- Diferencia accions puntuals de patrons reals:
    · Marca com a "evidència limitada" els que apareguin en un sol vídeo.
    · Marca com a "patró confirmat" els que apareguin en diversos vídeos.
- Identifica punts forts, debilitats, riscos i hàbits tàctics repetits.
- Detecta situacions on el rival rendeix millor o queda exposat.
- Justifica breument cada conclusió amb una observació visual concreta.

DEFINICIONS CLAU
- "Evidència limitada": acció observada en un únic vídeo.
- "Patró confirmat": acció observada en 2 o més vídeos.
- "Desconegut": informació no observable amb claredat.
- "Seguiment parcial": el rival és visible però no sempre.

PAS PREVI (NO MOSTRAR)
- Analitza cada vídeo individualment.
- Si n’hi ha més d’un, compara i detecta patrons.
- Classifica tota la informació en: punts forts, debilitats, patrons, incerteses.
- Avalua el nivell de confiança global.
- Genera el JSON final sense mostrar cap raonament intern.

REGLES DE QUALITAT 
- No descriguis elements irrellevants (públic, àrbitre, càmera, qualitat del vídeo).
- Si no pots identificar clarament el rival en un vídeo, indica-ho a "incerteses".
- Si un vídeo no permet seguir el rival amb seguretat, redueix el nivell de confiança global.
- Si no hi ha evidència suficient per omplir un camp, utilitza [] o "desconegut".
- Per a cada valor numèric que incloguis, ha d'existir una acció concreta observable que el justifiqui. Si no pots citar-la, utilitza "desconegut".
- Evita afirmacions vagues: en lloc de "és agressiu" escriu "inicia l'agarre als primers 10 segons de cada intercanvi".
- Sigues específic i vincula cada afirmació a una acció observable.
- Limita cada llista a un màxim de {_MAX_LIST_ITEMS} ítems, ordenant per rellevància.
- No repeteixis informació entre seccions.
- Totes les estadístiques, mètriques i observacions descriuen EXCLUSIVAMENT el rival.


PRIORITAT DE REGLES
- Si alguna regla entra en conflicte amb una altra, té prioritat:
  1) Nombre real de vídeos proporcionats
  2) No inventar informació
  3) Format JSON exacte
  4) Límit d’ítems per llista

CRITERI DE NIVELL DE CONFIANÇA GLOBAL
- "alta": només si hi ha 2 o més vídeos i el rival està identificat clarament sense dubtes significatius.
- "mitjana": rival identificat clarament en 1 vídeo, o amb dubtes puntuals en diversos vídeos.
- "baixa": identificació incerta, vídeo de baixa qualitat o seguiment poc fiable.
- "insuficient": material no analitzable.

EXEMPLES DE REFERÈNCIA 
Aquests exemples mostren el nivell de concreció esperat. NO els copiïs literalment.
- Amb un sol vídeo: "Observació limitada: intenta passar la guàrdia quan l'oponent queda assegut."
- Amb diversos vídeos: "Patró confirmat: inicia guard pull en 2 de 3 vídeos proporcionats."
- Punt fort: "Control fort des de side control; en cap vídeo l'adversari aconsegueix escapar un cop establert el pes"
- Debilitat: "Perd l'esquena quan intenta el guillotin i no tanca el braç; observat 2 vegades al vídeo 1"
- Acció accionable: "Quan intenta passar la guàrdia per dalt, rota cap a l'esquena immediatament"
- Valor numèric vàlid: atacs_iniciats = 4 (observat: 2 intents de single leg, 1 guard pull, 1 doble cama)
- Valor numèric invàlid → "desconegut": no es pot comptar amb seguretat des de l'angle de càmera
"""


# Prompt per al perfil lluitador
def _fighter_prompt(video_context: str, num_videos: int) -> str:
    """Prompt orientat al competidor: pràctic, directe i aplicable."""
    return (
        _base_rules(video_context, num_videos)
        + f"""
PERFIL DE SORTIDA: LLUITADOR
Objectiu: generar un scouting pràctic i fàcil d'aplicar abans del combat.
- Llenguatge clar i directe, sense terminologia tàctica avançada.
- Prioritza decisions útils per competir, no anàlisi estadística.
- No incloguis mètriques, gràfics ni dades difícils d'aplicar ràpidament.
- Cada ítem de les llistes ha de ser una frase curta i accionable.
- Màxim {_MAX_LIST_ITEMS} ítems per llista.

FORMAT JSON EXACTE:

{{
  "mode": "scouting",
  "perfil": "lluitador",
  "analysis_type": "scouting_lluitador",

  "rival_info": {{
    "nom_visible": "string o desconegut",
    "descripcio_visual": "Descripció física breu: complexió, alçada aproximada, trets distintius",
    "nivell_confianca_global": "alta | mitjana | baixa | insuficient"
  }},

  "resum_rival": "Resum en 2-3 frases del rival: estil predominant, posicions preferides i principal amenaça",

  "patrons_recurrents": [
    "Acció concreta observada en múltiples vídeos."
  ],

  "punts_forts": [
    "Habilitat específica."
  ],

  "debilitats": [
    "Vulnerabilitat concreta."
  ],

  "informe_lluitador": {{
    "amenaces_principals": [
      "Perill concret que pot representar."
    ],
    "debilitats_a_explotar": [
      "Com aprofitar una debilitat."
    ],
    "que_evitar": [
      "Situació o posició que cal evitar. "
    ],
    "pla_combat": [
      "Pas tàctic concret i ordenat. Màxim 3 passos."
    ],
    "consells_clau": [
      "Consell pràctic i directe."
    ],
    "clau_tactica": "La conclusió tàctica més important en 1-2 frases, basada únicament en el que s'ha observat als vídeos. Sense frases motivacionals."
  }},

  "incerteses": [
    "Aspecte no clar o no verificable."
  ]
}}
"""
    )


# Prompt per al perfil entrenador
def _coach_prompt(video_context: str, num_videos: int) -> str:
    """Prompt orientat a l'entrenador: tàctic, estructurat i amb mètriques."""
    return (
        _base_rules(video_context, num_videos)
        + f"""
PERFIL DE SORTIDA: ENTRENADOR 
Objectiu: generar un informe tàctic detallat per preparar un esportista.
- Utilitza llenguatge tècnic i estructurat.
- Detecta patrons transferibles a sessions d'entrenament.
- Inclou mètriques observables i dades preparades per generar gràfics.
- Ajuda l'entrenador a prendre decisions tàctiques i planificar sessions.
- Màxim {_MAX_LIST_ITEMS} ítems per llista.

REGLES PER A MÈTRIQUES I ESTADÍSTIQUES
- Les mètriques han de ser estimacions basades NOMÉS en accions observables.
- Si no es pot comptar una acció amb seguretat, utilitza "desconegut".
- No inventis percentatges ni números si el vídeo no ho permet.
- Diferencia entre recompte observat, estimació i interpretació tàctica.
- Valors numèrics NOMÉS quan hi hagi evidència visual suficient.
- Per a escales 0-10, utilitza integers. Si no es pot valorar, utilitza -1.
- Els camps de gràfics han de contenir dades que l'aplicació pugui representar.
- Per al gràfic de barres "frequencia_accions", inclou NOMÉS accions amb valor > 0.
- Per al gràfic "risc_per_situacio", valora el risc de 0 (cap risc) a 10 (risc màxim).

FORMAT JSON EXACTE:

{{
  "mode": "scouting",
  "perfil": "entrenador",
  "analysis_type": "scouting_entrenador",

  "rival_info": {{
    "nom_visible": "string o desconegut",
    "descripcio_visual": "Descripció física breu: complexió, alçada aproximada, trets distintius",
    "nivell_confianca_global": "alta | mitjana | baixa | insuficient"
  }},

  "resum_rival": "Resum en 2-4 frases: model de combat, posicions preferides, estil defensiu i principal amenaça tàctica",

  "patrons_recurrents": [
    "Patró tàctic observat en múltiples vídeos amb indicació de freqüència."
  ],

  "punts_forts": [
    "Habilitat tècnica específica amb evidència."
  ],

  "debilitats": [
    "Vulnerabilitat tàctica concreta."
  ],

  "informe_entrenador": {{
    "model_de_combat": "Descripció concreta en 1-2 frases del model tàctic.", 
    "patrons_ofensius": [
      "Patró ofensiu específic."
    ],
    "patrons_defensius": [
      "Patró defensiu específic." 
    ],
    "situacions_on_puntua": [
      "Context tàctic on el rival és més efectiu." 
    ],
    "situacions_on_queda_exposat": [
      "Context tàctic on el rival és vulnerable." 
    ],
    "pla_tactic_recomanat": [
       "Acció tàctica recomanada. Màxim {_MAX_LIST_ITEMS_PLA} passos ordenats."
    ],
    "focus_entrenament": [
      "Àrea d'entrenament prioritària."
    ],
    "exercicis_recomanats": [
      "Exercici concret."
    ],
    "riscos_principals": [
      "Risc tàctic prioritari."
    ]
  }},

  "estadistiques": {{
    "nota": "Explicació breu sobre la fiabilitat de les estadístiques d'aquest anàlisi",
    "nivell_fiabilitat_estadistica": "alta | mitjana | baixa",

    "per_video": [
      {{
        "video": "number o string",
        "fitxer": "string o desconegut",
        "seguiment_rival": "clar | parcial | incert",
        "atacs_iniciats": "number | desconegut (només si observable)",
        "atacs_efectius": "number | desconegut (només si observable)",
        "intents_passada_guardia": "number | desconegut (només si observable)",
        "passades_guardia_efectives": "number | desconegut (només si observable)",
        "raspades_intentades": "number | desconegut (només si observable)",
        "raspades_efectives": "number | desconegut (només si observable)",
        "submissions_intentades": "number | desconegut (només si observable)",
        "submissions_encaixades": "number | desconegut (només si observable)",
        "recuperacions_guardia": "number | desconegut (només si observable)",
        "perdues_posicio": "number | desconegut (només si observable)",
        "temps_dominant_aproximat": "string o desconegut",
        "situacions_mes_frequents": ["string"],
        "observacions": ["string"]
      }}
    ],

    "resum_global": {{
      "accions_mes_frequents": ["Acció observada amb freqüència."],
      "situacions_mes_repetides": ["Situació recurrent."],
      "zones_de_risc": ["Zona o posició de risc."],
      "tendencies_tactiques": ["Tendència observada."],
      "patrons_amb_mes_evidencia": ["Patró confirmat en múltiples vídeos"],
      "patrons_amb_poca_evidencia": ["Patró observat en un sol vídeo (evidència limitada)"]
    }},

    "perfil_numeric": {{
      "pressio": "integer 0-10 | -1 (només si avaluable)"
      "agressivitat": "integer 0-10 | -1 (només si avaluable)"
      "control_posicional": "integer 0-10 | -1 (només si avaluable)"
      "defensa": "integer 0-10 | -1 (només si avaluable)"
      "perill_submissio": "integer 0-10 | -1 (només si avaluable)"
      "explosivitat": "integer 0-10 | -1 (només si avaluable)"
      "adaptabilitat": "integer 0-10 | -1 (només si avaluable)"
    }}
  }},

  "grafics_suggerits": [
    {{
      "id": "frequencia_accions",
      "tipus": "barres",
      "titol": "Freqüència d'accions observades",
      "descripcio": "Recompte total d'accions ofensives observades en tots els vídeos. Inclou NOMÉS accions amb valor > 0.",
      "dades": [
        {{
          "label": "Nom curt de l'acció.",
          "valor": "number (recompte total observat, > 0)"
        }}
      ],
      "interpretacio": "Frase que explica el que mostren les dades i la seva rellevància tàctica"
    }},
    {{
      "id": "perfil_tactic",
      "tipus": "radar",
      "titol": "Perfil tàctic del rival",
      "descripcio": "Valoració de 0 a 10 de les principals dimensions tàctiques. Utilitza -1 per a dimensions no avaluables.",
      "dades": [
          {{"label": "pressio", "valor": "integer 0-10 o -1"}},
          {{"label": "agressivitat", "valor": "integer 0-10 o -1"}},
          {{"label": "control_posicional", "valor": "integer 0-10 o -1"}},
          {{"label": "defensa", "valor": "integer 0-10 o -1"}},
          {{"label": "perill_submissio", "valor": "integer 0-10 o -1"}},
          {{"label": "explosivitat", "valor": "integer 0-10 o -1"}},
          {{"label": "adaptabilitat", "valor": "integer 0-10 o -1"}}
      ],
      "escala": "0-10",
      "interpretacio": "Frase que destaca els punts alts i baixos del perfil i la seva implicació tàctica"
    }},
    {{
      "id": "risc_per_situacio",
      "tipus": "barres",
      "titol": "Risc per situació",
      "descripcio": "Nivell de risc (0-10) que representa el rival en cadascuna de les situacions de combat identificades.",
      "dades": [
        {{
          "label": "Nom curt de la situació.",
          "valor": "integer 0-10 (risc estimat)"
        }}
      ],
      "escala": "0-10",
      "interpretacio": "Frase que indica quines situacions cal evitar prioritàriament i per quina raó"
    }}
  ],

  "incerteses": [
    "Aspecte no clar o no verificable. "
  ]
}}
"""
    )
