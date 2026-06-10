from __future__ import annotations
import json
from typing import Any

_MAX_LIST_ITEMS = 5 


def build_evolution_prompt(
    old_analysis: dict[str, Any],
    new_analysis: dict[str, Any],
) -> str:
    """Construeix el prompt per analitzar l'evolució d'un lluitador.

    Compara un anàlisi antic amb un de recent del mateix lluitador i genera
    un informe estructurat en JSON sobre la seva evolució tàctica i tècnica.

    Args:
        old_analysis: Diccionari amb l'anàlisi de scouting antic del lluitador.
        new_analysis: Diccionari amb l'anàlisi de scouting recent del lluitador.

    Returns:
        String amb el prompt complet llest per enviar al model.

    Raises:
        TypeError: Si cap dels dos arguments no és un diccionari.
    """
    if not isinstance(old_analysis, dict) or not isinstance(new_analysis, dict):
        raise TypeError(
            "Els dos arguments han de ser diccionaris. "
            f"Rebut: old_analysis={type(old_analysis)}, new_analysis={type(new_analysis)}"
        )

    old_json = json.dumps(old_analysis, ensure_ascii=False, indent=2)
    new_json = json.dumps(new_analysis, ensure_ascii=False, indent=2)

    return _evolution_prompt(old_json, new_json)

# Construcció del prompt
def _evolution_prompt(old_json: str, new_json: str) -> str:
    """Genera el prompt complet per a l'anàlisi d'evolució."""
    return f"""
Ets un entrenador expert en Brazilian Jiu-Jitsu i grappling amb àmplia experiència
en l'anàlisi del rendiment esportiu i el seguiment de la progressió de lluitadors.

La teva tasca és comparar dos anàlisis de scouting del MATEIX lluitador:
  - ANÀLISI ANTIC : observació en un combat o període anterior.
  - ANÀLISI RECENT: observació en un combat o període més recent.

A partir d'aquesta comparació, has de generar un informe d'evolució que sigui
útil per a l'entrenador i el lluitador per entendre la progressió real i planificar
les properes sessions d'entrenament.

FORMAT DE SORTIDA 
- Retorna ÚNICAMENT un objecte JSON vàlid, sense cap text fora del JSON.
- No utilitzis Markdown, blocs de codi ni cap caràcter fora del JSON.
- Escriu tot el contingut textual en català.
- Respecta exactament l'estructura i l'ordre de claus indicat.
- No afegeixis camps addicionals fora del format especificat.
- El JSON ha de ser parsejable sense errors.

OBJECTIU GENERAL 
- Detectar millores tècniques i tàctiques reals entre els dos anàlisis.
- Identificar empitjoraments o regressions.
- Reconèixer patrons que es mantenen estables (fortaleses consolidades o debilitats persistents).
- Analitzar l'evolució del model de combat (tàctica global).
- Analitzar l'evolució tècnica (execució d'accions específiques).
- Generar recomanacions d'entrenament concretes i accionables.

IDENTIFICACIÓ DEL LLUITADOR (CRÍTIC)
- Els dos anàlisis proporcionats corresponen al MATEIX lluitador.
- L'informe d'evolució s'ha de basar EXCLUSIVAMENT en aquest lluitador.
- No analitzis rivals, oponents ni tercers que apareguin en els anàlisis.
- Si algun anàlisi no permet identificar clarament el lluitador, indica-ho a "incerteses".
- No barregis informació entre anàlisis: cada dada ha de provenir clarament de l'anàlisi antic o del recent, mai d'una fusió inventada.

REGLES DE QUALITAT 
- Basa't EXCLUSIVAMENT en els dos anàlisis proporcionats. No inventis informació.
- No assumeixis progrés o regressió si no hi ha evidència clara en les dades.
- Diferencia entre canvis confirmats i possibles canvis amb evidència limitada.
- Si una àrea no permet comparació clara, indica-ho a "incerteses".
- Evita afirmacions vagues com "ha millorat" o "és millor"; especifica en quina
  acció o situació concreta s'observa el canvi.
- Cada ítem de les llistes ha de ser una frase curta, concreta i verificable.
- Limita cada llista a un màxim de {_MAX_LIST_ITEMS} ítems, ordenats per rellevància.
- No repeteixis informació entre seccions.
- El camp "magnitud_canvi" ha de reflectir la intensitat real del canvi observat,
  no una valoració optimista.

PRIORITAT DE REGLES
1) No inventar informació.
2) Basar-se només en els dos anàlisis proporcionats.
3) Respectar el format JSON exacte.
4) Limitar les llistes a {_MAX_LIST_ITEMS} ítems.

CRITERI DE MAGNITUD DEL CANVI 
- "alta"  : canvi clar i consistent en múltiples aspectes o àrees.
- "mitjana": canvi observable en algunes àrees però no generalitzat.
- "baixa" : canvi puntual o amb evidència limitada; podria ser variabilitat natural.

CRITERI DE CONFIANÇA DE L'ANÀLISI 
- "alta"  : els dos anàlisis contenen dades riques i comparables sense ambigüitats.
- "mitjana": un dels dos anàlisis té dades parcials o hi ha algunes ambigüitats.
- "baixa" : dades insuficients en un o ambdós anàlisis per fer comparacions fiables.

DADES D'ENTRADA 

ANÀLISI ANTIC:
{old_json}

ANÀLISI RECENT:
{new_json}

FORMAT JSON EXACTE 

{{
  "mode": "evolucio",
  "analysis_type": "evolucio_lluitador",

  "fighter_info": {{
    "nom_visible": "Nom del lluitador si és identificable en els anàlisis, o 'desconegut'",
    "descripcio_visual": "Descripció física si és identificable, o 'desconegut'",
    "confianca_analisi": "alta | mitjana | baixa"
  }},

  "resum_evolucio": "Resum en 3-4 frases de l'evolució global: si ha progressat, en quines àrees i quin és el canvi més significatiu",

  "magnitud_canvi_global": "alta | mitjana | baixa",

  "millores": [
    "Millora concreta i verificable. Exemple: 'Ha incorporat la raspada de taló des de 50/50, absent en l'anàlisi antic'"
  ],

  "regressions": [
    "Regressió o empitjorament concret. Exemple: 'La defensa de passada de guàrdia per dalt ha empitjorat; en l'anàlisi recent perd la posició amb més freqüència'"
  ],

  "patrons_estables": {{
    "fortaleses_consolidades": [
      "Punt fort present en ambdós anàlisis. Exemple: 'Control des de back mount consistent en els dos períodes'"
    ],
    "debilitats_persistents": [
      "Debilitat present en ambdós anàlisis. Exemple: 'Dificultat per recuperar la guàrdia des de bottom side control en els dos períodes'"
    ]
  }},

  "evolucio_tactica": {{
    "model_antic": "Descripció concreta del model de combat en l'anàlisi antic. Exemple: 'Prioritzava el combat de peu i evitava la lluita de terra'",
    "model_recent": "Descripció concreta del model de combat en l'anàlisi recent. Exemple: 'Ha incorporat el guard pull sistemàtic i busca la lluita de cames'",
    "canvi_observat": "Descripció del canvi tàctic entre els dos períodes, o 'sense canvis significatius' si no n'hi ha",
    "interpretacio": "Frase que interpreta el significat tàctic del canvi observat per a l'entrenador"
  }},

  "evolucio_tecnica": {{
    "tecniques_millorades": [
      "Tècnica específica que ha millorat. Exemple: 'Execució del heel hook extern: més ràpida i amb millor control de l'angle'"
    ],
    "tecniques_empitjorades": [
      "Tècnica específica que ha empitjorat. Exemple: 'Guillotin en arm-in: perd el tancament amb més freqüència que en el període anterior'"
    ],
    "tecniques_noves": [
      "Tècnica absent en l'anàlisi antic i present en el recent. Exemple: 'Apareix per primera vegada l'ús de la guàrdia de butterfly per iniciar la lluita de cames'"
    ],
    "tecniques_abandonades": [
      "Tècnica present en l'anàlisi antic i absent en el recent. Exemple: 'El single leg des de peu, freqüent en el període anterior, no apareix en el recent'"
    ]
  }},

  "comparativa_numerica": {{
    "nota": "Explicació breu sobre la fiabilitat de la comparativa numèrica",
    "disponible": "true si ambdós anàlisis contenen perfil_numeric comparable, false en cas contrari",
    "perfil_antic": {{
      "pressio": "integer 0-10 o -1 si desconegut",
      "agressivitat": "integer 0-10 o -1 si desconegut",
      "control_posicional": "integer 0-10 o -1 si desconegut",
      "defensa": "integer 0-10 o -1 si desconegut",
      "perill_submissio": "integer 0-10 o -1 si desconegut",
      "explosivitat": "integer 0-10 o -1 si desconegut",
      "adaptabilitat": "integer 0-10 o -1 si desconegut"
    }},
    "perfil_recent": {{
      "pressio": "integer 0-10 o -1 si desconegut",
      "agressivitat": "integer 0-10 o -1 si desconegut",
      "control_posicional": "integer 0-10 o -1 si desconegut",
      "defensa": "integer 0-10 o -1 si desconegut",
      "perill_submissio": "integer 0-10 o -1 si desconegut",
      "explosivitat": "integer 0-10 o -1 si desconegut",
      "adaptabilitat": "integer 0-10 o -1 si desconegut"
    }},
    "deltes": {{
      "nota": "Diferència entre perfil_recent i perfil_antic per cada dimensió (positiu = millora, negatiu = regressió, 0 = estable, null si alguna de les dues és -1)",
      "pressio": "integer o null",
      "agressivitat": "integer o null",
      "control_posicional": "integer o null",
      "defensa": "integer o null",
      "perill_submissio": "integer o null",
      "explosivitat": "integer o null",
      "adaptabilitat": "integer o null"
    }}
  }},

  "grafics_suggerits": [
    {{
      "id": "comparativa_perfil_tactic",
      "tipus": "radar_doble",
      "titol": "Evolució del perfil tàctic",
      "descripcio": "Comparativa visual del perfil tàctic entre el període antic i el recent. Inclou NOMÉS dimensions amb valor != -1 en ambdós perfils.",
      "series": [
        {{
          "nom": "Antic",
          "dades": [
            {{"label": "pressio",            "valor": "integer 0-10 o -1"}},
            {{"label": "agressivitat",       "valor": "integer 0-10 o -1"}},
            {{"label": "control_posicional", "valor": "integer 0-10 o -1"}},
            {{"label": "defensa",            "valor": "integer 0-10 o -1"}},
            {{"label": "perill_submissio",   "valor": "integer 0-10 o -1"}},
            {{"label": "explosivitat",       "valor": "integer 0-10 o -1"}},
            {{"label": "adaptabilitat",      "valor": "integer 0-10 o -1"}}
          ]
        }},
        {{
          "nom": "Recent",
          "dades": [
            {{"label": "pressio",            "valor": "integer 0-10 o -1"}},
            {{"label": "agressivitat",       "valor": "integer 0-10 o -1"}},
            {{"label": "control_posicional", "valor": "integer 0-10 o -1"}},
            {{"label": "defensa",            "valor": "integer 0-10 o -1"}},
            {{"label": "perill_submissio",   "valor": "integer 0-10 o -1"}},
            {{"label": "explosivitat",       "valor": "integer 0-10 o -1"}},
            {{"label": "adaptabilitat",      "valor": "integer 0-10 o -1"}}
          ]
        }}
      ],
      "escala": "0-10",
      "interpretacio": "Frase que destaca les dimensions amb més canvi i la seva implicació per a l'entrenament"
    }},
    {{
      "id": "deltes_dimensions",
      "tipus": "barres_horitzontals",
      "titol": "Canvi per dimensió tàctica",
      "descripcio": "Diferència (delta) entre el perfil recent i l'antic per a cada dimensió. Valors positius indiquen millora, negatius regressió. Inclou NOMÉS dimensions amb delta != null.",
      "dades": [
        {{
          "label": "Nom de la dimensió. Exemple: 'control_posicional'",
          "valor": "integer (delta: recent - antic)"
        }}
      ],
      "escala": "-10 a +10",
      "interpretacio": "Frase que resumeix quines dimensions han tingut el canvi més significatiu"
    }}
  ],

  "recomanacions_entrenament": {{
    "prioritat_alta": [
      "Acció d'entrenament urgent. Exemple: 'Treballar la defensa de heel hook extern des de 50/50, que ha aparegut com a nova amenaça en el període recent'"
    ],
    "prioritat_mitjana": [
      "Acció d'entrenament important però no urgent. Exemple: 'Consolidar la guàrdia de butterfly, que és nova i encara poc fiable'"
    ],
    "manteniment": [
      "Aspecte ja sòlid que cal mantenir. Exemple: 'Continuar drillant el back control, que es manté com a fortalesa en els dos períodes'"
    ]
  }},

  "conclusio": "Conclusió global en 2-3 frases: balanç net de l'evolució, el canvi més rellevant i la recomanació estratègica principal per als propers mesos",

  "incerteses": [
    "Aspecte no comparable o amb evidència insuficient. Exemple: 'L'anàlisi antic no conté dades de perfil numèric; la comparativa quantitativa no és possible'"
  ]
}}
"""