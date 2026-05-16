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
    lines: list[str] = []

    for item in video_descriptions:
        index = item.get("index", "?")
        filename = item.get("filename", "desconegut")
        rival_description = item.get("rival_description", "desconegut")

        try:
            video_number = int(index) + 1
        except (TypeError, ValueError):
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
- Mantén exactament l'estructura i l'ordre de claus indicat.
- No afegeixis camps fora del format especificat.

Objectiu general:
- Analitzar només el rival indicat en cada vídeo.
- Detectar patrons recurrents entre vídeos.
- Diferenciar accions puntuals de patrons reals.
- Identificar punts forts, debilitats i riscos.
- Detectar hàbits tàctics repetits.
- Detectar situacions on el rival funciona millor o queda exposat.
- Justificar breument cada conclusió amb una observació visual concreta.

Regles generals:
- Utilitza només informació observable als vídeos.
- No inventis informació.
- No assumeixis dades que no es puguin veure clarament.
- No descriguis elements no rellevants (públic, àrbitre, càmera, qualitat del vídeo).
- Si no pots identificar clarament el rival en un vídeo, indica-ho a "incerteses".
- Si un vídeo no permet seguir el rival amb seguretat, redueix la confiança global.
- Si alguna conclusió no és clara, posa-la a "incerteses".
- Si no hi ha evidència suficient per omplir un camp, utilitza [] o "desconegut".
- Evita frases vagues com "és agressiu", "és tècnic", "manté pressió".
- Sigues específic i vincula cada afirmació a una acció observable.
- Tracta cada vídeo com una observació independent abans de sintetitzar.
- Marca com a "evidència limitada" els patrons que només apareixen en un vídeo.
- Marca com a "patró confirmat" els que apareixen en diversos vídeos.
- Mantén les llistes amb frases curtes i directes.
- No repeteixis informació entre seccions.
"""


def _fighter_prompt(video_context: str) -> str:
    return (
        _base_rules(video_context)
        + """
Perfil de sortida: lluitador.

Objectiu específic:
- Generar un scouting pràctic i fàcil d'aplicar abans del combat.
- Parlar de manera clara i directa.
- Prioritzar decisions útils per competir.
- Evitar informació massa tècnica, estadística o difícil d'aplicar ràpidament.
- No incloure mètriques, gràfics ni estadístiques avançades.

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

Objectiu específic:
- Generar un informe tàctic útil per preparar un esportista.
- Utilitzar llenguatge tècnic i estructurat.
- Detectar patrons transferibles a entrenament.
- Incloure mètriques observables, estadístiques estimades i dades preparades per generar gràfics.
- Ajudar l'entrenador a prendre decisions tàctiques i planificar sessions d'entrenament.

Regles específiques per a mètriques:
- Les mètriques han de ser estimacions basades només en accions observables.
- Si no es pot comptar una acció amb seguretat, utilitza "desconegut".
- No inventis percentatges ni números precisos si el vídeo no ho permet.
- Diferencia entre recompte observat, estimació i interpretació tàctica.
- Utilitza valors numèrics només quan hi hagi evidència visual suficient.
- Per a escales de 0 a 10, utilitza números enters.
- Si una mètrica no es pot valorar, utilitza "desconegut".
- Els camps de gràfics han de contenir dades que l'aplicació pugui representar visualment.

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

  "estadistiques": {
    "nota": "string",
    "nivell_fiabilitat_estadistica": "alta|mitjana|baixa",

    "per_video": [
      {
        "video": "number|string",
        "fitxer": "string|desconegut",
        "seguiment_rival": "clar|parcial|incert",
        "atacs_iniciats": "number|desconegut",
        "atacs_efectius": "number|desconegut",
        "intents_passada_guardia": "number|desconegut",
        "passades_guardia_efectives": "number|desconegut",
        "raspades_intentades": "number|desconegut",
        "raspades_efectives": "number|desconegut",
        "submissions_intentades": "number|desconegut",
        "submissions_encaixades": "number|desconegut",
        "recuperacions_guardia": "number|desconegut",
        "perdues_posicio": "number|desconegut",
        "temps_dominant_aproximat": "string|desconegut",
        "situacions_mes_frequents": ["string"],
        "observacions": ["string"]
      }
    ],

    "resum_global": {
      "accions_mes_frequents": ["string"],
      "situacions_mes_repetides": ["string"],
      "zones_de_risc": ["string"],
      "tendencies_tactiques": ["string"],
      "patrons_amb_mes_evidencia": ["string"],
      "patrons_amb_poca_evidencia": ["string"]
    },

    "perfil_numeric": {
      "pressio": "number|desconegut",
      "agressivitat": "number|desconegut",
      "control_posicional": "number|desconegut",
      "defensa": "number|desconegut",
      "perill_submissio": "number|desconegut",
      "explosivitat": "number|desconegut",
      "adaptabilitat": "number|desconegut"
    }
  },

  "grafics_suggerits": [
    {
      "id": "frequencia_accions",
      "tipus": "barres",
      "titol": "Freqüència d'accions observades",
      "descripcio": "string",
      "dades": [
        {
          "label": "string",
          "valor": "number"
        }
      ],
      "interpretacio": "string"
    },
    {
      "id": "perfil_tactic",
      "tipus": "radar",
      "titol": "Perfil tàctic del rival",
      "descripcio": "string",
      "dades": [
        {
          "label": "pressio",
          "valor": "number"
        },
        {
          "label": "agressivitat",
          "valor": "number"
        },
        {
          "label": "control_posicional",
          "valor": "number"
        },
        {
          "label": "defensa",
          "valor": "number"
        },
        {
          "label": "perill_submissio",
          "valor": "number"
        },
        {
          "label": "explosivitat",
          "valor": "number"
        },
        {
          "label": "adaptabilitat",
          "valor": "number"
        }
      ],
      "escala": "0-10",
      "interpretacio": "string"
    },
    {
      "id": "risc_per_situacio",
      "tipus": "barres",
      "titol": "Risc per situació",
      "descripcio": "string",
      "dades": [
        {
          "label": "string",
          "valor": "number"
        }
      ],
      "escala": "0-10",
      "interpretacio": "string"
    }
  ],

  "incerteses": ["string"]
}
"""
    )
