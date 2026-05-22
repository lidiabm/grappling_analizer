"""
scouting_prompts.py
-------------------
Generació de prompts per a l'anàlisi de scouting de rivals en grappling.

Perfils suportats:
  - ProfileType.LLUITADOR : informe pràctic i directe per al competidor.
  - ProfileType.ENTRENADOR: informe tàctic avançat amb mètriques i gràfics.

Ús bàsic:
    prompt = build_scouting_prompt(
        profile="entrenador",
        video_descriptions=[
            {"index": 0, "filename": "video1.mp4", "rival_description": "cinturó blau, cabell curt"},
        ],
    )
"""

from __future__ import annotations

from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Tipus i constants
# ---------------------------------------------------------------------------

class ProfileType(str, Enum):
    """Perfils de sortida del scouting."""

    LLUITADOR = "lluitador"
    ENTRENADOR = "entrenador"


_MAX_LIST_ITEMS = 5  # límit recomanat per a llistes en el prompt


# ---------------------------------------------------------------------------
# Punt d'entrada públic
# ---------------------------------------------------------------------------

def build_scouting_prompt(
    profile: str,
    video_descriptions: list[dict[str, Any]],
) -> str:
    """Construeix el prompt de scouting segons el perfil indicat.

    Args:
        profile: "lluitador" o "entrenador". Qualsevol altre valor
                 es tracta com a "lluitador" per defecte.
        video_descriptions: Llista de diccionaris amb les claus
            ``index``, ``filename`` i ``rival_description``.

    Returns:
        String amb el prompt complet llest per enviar al model.
    """
    try:
        profile_type = ProfileType(profile)
    except ValueError:
        profile_type = ProfileType.LLUITADOR

    video_context = _build_video_context(video_descriptions)

    builders = {
        ProfileType.LLUITADOR: _fighter_prompt,
        ProfileType.ENTRENADOR: _coach_prompt,
    }
    return builders[profile_type](video_context)


# ---------------------------------------------------------------------------
# Construcció del context de vídeos
# ---------------------------------------------------------------------------

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

        try:
            video_number = int(raw_index) + 1
        except (TypeError, ValueError):
            video_number = raw_index

        lines.append(
            f"- Vídeo {video_number} | fitxer: '{filename}' | rival: {rival_description}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Regles base compartides
# ---------------------------------------------------------------------------

def _base_rules(video_context: str) -> str:
    """Bloc de regles i instruccions comunes als dos perfils."""
    return f"""
Analitza diversos vídeos del mateix rival en un context de grappling.

Vídeos proporcionats:
{video_context}

=== FORMAT DE SORTIDA ===
- Retorna ÚNICAMENT un objecte JSON vàlid, sense cap text fora del JSON.
- No utilitzis Markdown, blocs de codi ni cap caràcter fora del JSON.
- Escriu tot el contingut textual en català.
- Respecta exactament l'estructura i l'ordre de claus indicat.
- No afegeixis camps addicionals fora del format especificat.
- El JSON ha de ser parsejable sense errors.

=== OBJECTIU GENERAL ===
- Analitza NOMÉS el rival indicat en cada vídeo.
- Tracta cada vídeo com una observació independent abans de sintetitzar.
- Detecta patrons recurrents entre vídeos.
- Diferencia accions puntuals de patrons reals:
    · Marca com a "evidència limitada" els que apareguin en un sol vídeo.
    · Marca com a "patró confirmat" els que apareguin en diversos vídeos.
- Identifica punts forts, debilitats, riscos i hàbits tàctics repetits.
- Detecta situacions on el rival rendeix millor o queda exposat.
- Justifica breument cada conclusió amb una observació visual concreta.

=== REGLES DE QUALITAT ===
- Utilitza NOMÉS informació observable als vídeos. No inventis dades.
- No assumeixis res que no es pugui veure clarament.
- No descriguis elements irrellevants (públic, àrbitre, càmera, qualitat del vídeo).
- Si no pots identificar clarament el rival en un vídeo, indica-ho a "incerteses".
- Si un vídeo no permet seguir el rival amb seguretat, redueix el nivell de confiança global.
- Si una conclusió no és clara, posa-la a "incerteses".
- Si no hi ha evidència suficient per omplir un camp, utilitza [] o "desconegut".
- Evita afirmacions vagues: en lloc de "és agressiu" escriu "inicia l'agarre als primers 10 segons de cada intercanvi".
- Sigues específic i vincula cada afirmació a una acció observable.
- Limita cada llista a un màxim de {_MAX_LIST_ITEMS} ítems, ordenant per rellevància.
- No repeteixis informació entre seccions.

=== CRITERI DE NIVELL DE CONFIANÇA GLOBAL ===
- "alta"  : rival identificat clarament en 2 o més vídeos sense dubtes significatius.
- "mitjana": identificat en 1 vídeo, o amb dubtes puntuals en algun vídeo.
- "baixa" : identificació incerta, vídeo de baixa qualitat o seguiment poc fiable.
"""


# ---------------------------------------------------------------------------
# Prompt per al perfil lluitador
# ---------------------------------------------------------------------------

def _fighter_prompt(video_context: str) -> str:
    """Prompt orientat al competidor: pràctic, directe i aplicable."""
    return (
        _base_rules(video_context)
        + f"""
=== PERFIL DE SORTIDA: LLUITADOR ===
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
    "nivell_confianca_global": "alta | mitjana | baixa"
  }},

  "resum_rival": "Resum en 2-3 frases del rival: estil predominant, posicions preferides i principal amenaça",

  "patrons_recurrents": [
    "Acció concreta observada en múltiples vídeos. Exemple: 'Agafa doble cama des de la distància mitjana quan l'adversari avança'"
  ],

  "punts_forts": [
    "Habilitat específica. Exemple: 'Control fort des de side control, difícil d'escapar quan estableix el pes'"
  ],

  "debilitats": [
    "Vulnerabilitat concreta. Exemple: 'Perd l'esquena quan intenta el guillotin i no tanca el braç'"
  ],

  "informe_lluitador": {{
    "amenaces_principals": [
      "Perill concret que pot representar. Exemple: 'Triangle des de guard tancat si et descuides el braç esquerre'"
    ],
    "debilitats_a_explotar": [
      "Com aprofitar una debilitat. Exemple: 'Quan intenta passar la guàrdia per dalt, exposa l'esquena'"
    ],
    "que_evitar": [
      "Situació o posició que cal evitar. Exemple: 'No anar al terra en posició inferior, domina el ground-and-pound'"
    ],
    "pla_combat": [
      "Pas tàctic concret. Exemple: '1. Mantenir la distància i forçar-lo a avançar. 2. Aprofitar les seves intents de doble cama per cercar la guillotina'"
    ],
    "consells_clau": [
      "Consell pràctic i directe. Exemple: 'Si et submergeix sota, rota immediatament cap a la dreta per evitar el single leg'"
    ],
    "missatge_final": "Frase motivacional i estratègica de 1-2 línies que resumeixi la clau del combat"
  }},

  "incerteses": [
    "Aspecte no clar o no verificable. Exemple: 'En el vídeo 2 no es pot confirmar si la pèrdua de posició va ser tàctica o un error'"
  ]
}}
"""
    )


# ---------------------------------------------------------------------------
# Prompt per al perfil entrenador
# ---------------------------------------------------------------------------

def _coach_prompt(video_context: str) -> str:
    """Prompt orientat a l'entrenador: tàctic, estructurat i amb mètriques."""
    return (
        _base_rules(video_context)
        + f"""
=== PERFIL DE SORTIDA: ENTRENADOR ===
Objectiu: generar un informe tàctic detallat per preparar un esportista.
- Utilitza llenguatge tècnic i estructurat.
- Detecta patrons transferibles a sessions d'entrenament.
- Inclou mètriques observables i dades preparades per generar gràfics.
- Ajuda l'entrenador a prendre decisions tàctiques i planificar sessions.
- Màxim {_MAX_LIST_ITEMS} ítems per llista.

=== REGLES PER A MÈTRIQUES I ESTADÍSTIQUES ===
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
    "nivell_confianca_global": "alta | mitjana | baixa"
  }},

  "resum_rival": "Resum en 2-4 frases: model de combat, posicions preferides, estil defensiu i principal amenaça tàctica",

  "patrons_recurrents": [
    "Patró tàctic observat en múltiples vídeos amb indicació de freqüència. Exemple: 'Inicia guard pull sistemàtic en 3 dels 4 vídeos quan l'adversari pressiona'"
  ],

  "punts_forts": [
    "Habilitat tècnica específica amb evidència. Exemple: 'Raspada de taló des de guard de destraler amb alta taxa d'efectivitat observada'"
  ],

  "debilitats": [
    "Vulnerabilitat tàctica concreta. Exemple: 'Defensa reactiva quan perd el control de la cama; no recupera la guàrdia i cau al bottom side control'"
  ],

  "informe_entrenador": {{
    "model_de_combat": "Descripció concreta en 1-2 frases del model tàctic. Exemple: 'Cerca la lluita de terra via single leg o guard pull; una vegada al terra prioritza posicions de cama sobre control posicional clàssic'",
    "patrons_ofensius": [
      "Patró ofensiu específic. Exemple: 'Ataca el heel hook extern des de guard de 50/50 quan l'adversari intenta passar per dalt'"
    ],
    "patrons_defensius": [
      "Patró defensiu específic. Exemple: 'Recupera guard usant la tècnica de inversió de cadera quan és al bottom de side control'"
    ],
    "situacions_on_puntua": [
      "Context tàctic on el rival és més efectiu. Exemple: 'Puntua majoritàriament des de guard de destraler en combat de peu'"
    ],
    "situacions_on_queda_exposat": [
      "Context tàctic on el rival és vulnerable. Exemple: 'Queda exposat quan l'adversari passa a north-south i controla el pes'"
    ],
    "pla_tactic_recomanat": [
      "Acció tàctica recomanada. Exemple: '1. Evitar la lluita de cames i prioritzar control posicional clàssic (mount, back control)'"
    ],
    "focus_entrenament": [
      "Àrea d'entrenament prioritària. Exemple: 'Defensa de heel hook extern des de posició de 50/50'"
    ],
    "exercicis_recomanats": [
      "Exercici concret. Exemple: 'Drilling de sortida de 50/50 cap a tall-kneeling per evitar l'exposició al heel hook'"
    ],
    "riscos_principals": [
      "Risc tàctic prioritari. Exemple: 'Alt risc de submissió per heel hook si es permet el 50/50 sense control de la línia central'"
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
        "atacs_iniciats": "number o desconegut",
        "atacs_efectius": "number o desconegut",
        "intents_passada_guardia": "number o desconegut",
        "passades_guardia_efectives": "number o desconegut",
        "raspades_intentades": "number o desconegut",
        "raspades_efectives": "number o desconegut",
        "submissions_intentades": "number o desconegut",
        "submissions_encaixades": "number o desconegut",
        "recuperacions_guardia": "number o desconegut",
        "perdues_posicio": "number o desconegut",
        "temps_dominant_aproximat": "string o desconegut",
        "situacions_mes_frequents": ["string"],
        "observacions": ["string"]
      }}
    ],

    "resum_global": {{
      "accions_mes_frequents": ["Acció observada amb freqüència. Exemple: 'Intents de guard pull: ~8 vegades en total'"],
      "situacions_mes_repetides": ["Situació recurrent. Exemple: 'Lluita de cames des de guard de destraler'"],
      "zones_de_risc": ["Zona o posició de risc. Exemple: '50/50 amb control de l'angle exterior'"],
      "tendencies_tactiques": ["Tendència observada. Exemple: 'Preferència per submissions de cama sobre estrangulaments'"],
      "patrons_amb_mes_evidencia": ["Patró confirmat en múltiples vídeos"],
      "patrons_amb_poca_evidencia": ["Patró observat en un sol vídeo (evidència limitada)"]
    }},

    "perfil_numeric": {{
      "pressio": "integer 0-10 o -1 si desconegut",
      "agressivitat": "integer 0-10 o -1 si desconegut",
      "control_posicional": "integer 0-10 o -1 si desconegut",
      "defensa": "integer 0-10 o -1 si desconegut",
      "perill_submissio": "integer 0-10 o -1 si desconegut",
      "explosivitat": "integer 0-10 o -1 si desconegut",
      "adaptabilitat": "integer 0-10 o -1 si desconegut"
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
          "label": "Nom curt de l'acció. Exemple: 'Guard pull'",
          "valor": "number (recompte total observat)"
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
        {{"label": "pressio",           "valor": "integer 0-10 o -1"}},
        {{"label": "agressivitat",      "valor": "integer 0-10 o -1"}},
        {{"label": "control_posicional","valor": "integer 0-10 o -1"}},
        {{"label": "defensa",           "valor": "integer 0-10 o -1"}},
        {{"label": "perill_submissio",  "valor": "integer 0-10 o -1"}},
        {{"label": "explosivitat",      "valor": "integer 0-10 o -1"}},
        {{"label": "adaptabilitat",     "valor": "integer 0-10 o -1"}}
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
          "label": "Nom curt de la situació. Exemple: '50/50'",
          "valor": "integer 0-10 (risc estimat)"
        }}
      ],
      "escala": "0-10",
      "interpretacio": "Frase que indica quines situacions cal evitar prioritàriament i per quina raó"
    }}
  ],

  "incerteses": [
    "Aspecte no clar o no verificable. Exemple: 'En el vídeo 3 no es pot confirmar si la pèrdua de posició va ser tàctica o un error de càmera'"
  ]
}}
"""
    )
