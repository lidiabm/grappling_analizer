def build_prompt(profile: str) -> str:
    base = """
Analitza aquest vídeo d’un combat de grappling.

Retorna la resposta exclusivament en català.
Respon només amb JSON vàlid.
No afegeixis text extra.
No facis servir Markdown.
No incloguis blocs de codi ni l'etiqueta json.

Regles generals:
- Utilitza exclusivament informació observable al vídeo.
- No inventis dades, noms, resultat oficial, categories, regles específiques ni intencions dels lluitadors si no es poden confirmar visualment.
- Si una dada no es pot confirmar visualment, fes servir el valor "desconegut" o "incert" segons correspongui i afegeix una nota a "incerteses".
- Si els noms dels lluitadors no es poden identificar amb claredat, fes servir "oponent_1" i "oponent_2" com a identificadors interns estables.
- Pots fer servir una descripció observable per distingir-los visualment, com ara color de samarreta, rashguard, pantalons o un altre tret clar.
- Quan facis inferències tàctiques, basa-les només en patrons visibles, repeticions clares o decisions observables. No atribueixis motivacions internes.
- Mantén consistència terminològica a tota la resposta.

Identificació dels oponents:
- Cada oponent ha de tenir un "id" fix: "oponent_1" o "oponent_2".
- Cada oponent pot tenir una "descripcio_visual" com per exemple "rashguard blava", "samarreta negra", "sense samarreta", etc.
- Si apareix clarament el nom d’un lluitador al vídeo o en el marcador, el pots posar a "nom_visible".
- Si no es veu cap nom clar, fes servir "desconegut" a "nom_visible".

Posicions permeses (llista tancada):
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

Valors permesos per a "controlador":
- oponent_1
- oponent_2
- cap
- incert

Valors permesos per a "tipus_event":
- inici_intercanvi
- control
- transicio
- intento_finalitzacio
- intento_enderroc
- guard_pull
- escape
- reversio
- scramble
- pausa
- finalitzacio
- altre

Valors permesos per a "metode":
- submissio
- punts
- decisio
- desconegut

Valors permesos per a "confianca":
- alta
- mitjana
- baixa

Regles per al resum del partit:
- "guanyador" i "perdedor" han de ser objectes amb:
  - "id": "oponent_1" o "oponent_2" o "desconegut"
  - "descripcio": una descripció observable breu o "desconegut"
- Si no es pot confirmar visualment qui guanya o perd, fes servir "desconegut".
- No facis servir "temps" com a mètode de victòria.
- Si la victòria és per submissió i el tipus concret es pot inferir visualment, omple "tipus_submissio". Si no, posa "desconegut".
- Si el resultat no es pot confirmar amb suficient evidència visual, marca-ho clarament a "incerteses".

Regles per al timeline:
- Segmenta el combat en trams temporals coherents i consecutius.
- Cada tram ha de tenir un inici i un fi en format MM:SS.
- Els trams no s’han de solapar i, en conjunt, han de cobrir tota la seqüència analitzada.
- Evita trams innecessàriament curts, excepte si hi ha un esdeveniment clarament rellevant (per exemple: sweep, takedown, pass, submission attempt, reversal o finalització).
- Cada tram ha de tenir una sola posició principal, escollida exclusivament de la llista tancada de posicions permeses.
- Si hi ha una fase transitòria, confusa o ambigua, fes servir "scramble" o "other".
- Indica qui controla l’acció utilitzant exclusivament els valors permesos.
- Descriu l’acció de forma concreta, observable i concisa, sense interpretar intencions no visibles.
- Cada descripció ha d’explicar què passa en aquell tram amb prou detall per entendre la seqüència, però sense excedir-se en longitud.
- "rellevancia" ha de ser un enter de 1 a 5:
  - 1 = baixa
  - 2 = menor
  - 3 = moderada
  - 4 = alta
  - 5 = crítica
- Afegeix "confianca" a cada segment, utilitzant només els valors permesos o l’escala definida.
- Prioritza els canvis reals de posició, control o iniciativa per decidir quan comença o acaba un tram.

Regles per a l’anàlisi:
- L’anàlisi ha d’estar basada en conductes observables durant el combat.
- "tactica_general" ha de resumir l’enfocament predominant observable.
- "patrons_tactics" només ha d’incloure patrons repetits o clarament visibles.
- "errors_detallats" només ha d’incloure errors amb impacte observable o probable.
- "millores_recomanades" han de derivar directament dels errors o patrons observats.
- No repeteixis exactament el mateix contingut en diversos camps.

Regles per a les estadístiques:
- Fes estimacions raonables només quan hi hagi base visual suficient.
- No donis una precisió falsa.
- Si una mètrica no és fiable, usa un valor conservador, "desconegut" quan calgui, i reflecteix-ho a "incerteses".
- "temps_per_posicio" ha d’estimar segons acumulats per lluitador i posició.
- "dominant" indica si aquell lluitador era el controlador principal en aquella posició.
- "canvis_control" és el nombre estimat de canvis clars de control.
- "intents_finalitzacio" és el nombre estimat d’intents visibles de submissió.
- "intents_enderroc" és el nombre estimat d’intents visibles de takedown o projecció.
- "guard_pulls" és el nombre estimat de guard pulls visibles.

Regles per a patrons i comparació futura:
- Extreu fortaleses i debilitats clau de cada lluitador de forma breu i normalitzable.
- Extreu seqüències repetides si apareixen clarament.
- Aquests camps han de ser útils per comparar combats futurs del mateix lluitador o per scouting d’oponents.

"""

    if profile == "entrenador":
        profile_block = """
Enfoca l’anàlisi per a un ENTRENADOR.

Prioritza:
- patrons tàctics recurrents
- presa de decisions observable
- transicions i estabilització de control
- pèrdua i recuperació de la iniciativa
- errors sistemàtics
- recomanacions útils per planificar entrenament
- informació útil per comparar combats i preparar scouting

Fes les recomanacions amb orientació d’entrenament, correcció tècnica i treball tàctic.
"""
    else:
        profile_block = """
Enfoca l’anàlisi per a un LLUITADOR.

Prioritza:
- errors tècnics concrets
- encerts clars
- moments clau del combat
- situacions on guanya o perd el control
- recomanacions pràctiques, concretes i accionables
- informació útil per estudiar oponents

Fes les recomanacions de forma directa i aplicable a la pràctica.
"""

    response_schema = """
Format exacte de sortida:
{
  "combat_info": {
    "oponents": [
      {
        "id": "oponent_1",
        "nom_visible": "string",
        "descripcio_visual": "string"
      },
      {
        "id": "oponent_2",
        "nom_visible": "string",
        "descripcio_visual": "string"
      }
    ],
    "durada_estimada": "MM:SS",
    "nivell_confianca_global": "alta"
  },
  "resum_partit": {
    "guanyador": {
      "id": "string",
      "descripcio": "string"
    },
    "perdedor": {
      "id": "string",
      "descripcio": "string"
    },
    "metode": "string",
    "tipus_submissio": "string",
    "resum_breu": "string"
  },
  "timeline": [
    {
      "inici": "MM:SS",
      "fi": "MM:SS",
      "posicio": "string",
      "controlador": "string",
      "tipus_event": "string",
      "descripcio": "string",
      "rellevancia": 1,
      "confianca": "string"
    }
  ],
  "analisi_oponents": {
    "oponent_1": {
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
    },
    "oponent_2": {
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
  },
  "estadistiques_estimades": {
    "temps_per_posicio": [
      {
        "lluitador": "string",
        "posicio": "string",
        "segons": 0,
        "dominant": true
      }
    ],
    "canvis_control": 0,
    "intents_finalitzacio": 0,
    "intents_enderroc": 0,
    "guard_pulls": 0
  },
  "patrons_globals": {
    "dinamiques_clau": ["string"],
    "moments_decisius": ["string"],
    "resum_comparable": ["string"]
  },
  "incerteses": ["string"]
}

Restriccions finals:
- Retorna només JSON vàlid.
- No afegeixis cap clau fora d’aquest esquema.
- Si una dada no es pot confirmar, fes servir "desconegut", "incert" o una llista buida segons pertoqui.
- Mantén consistència entre timeline, resum i estadístiques.
"""

    return base + profile_block + response_schema