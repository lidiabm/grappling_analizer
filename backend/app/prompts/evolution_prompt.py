def build_evolution_prompt(
    old_analysis: dict,
    new_analysis: dict,
) -> str:
    return f"""
Ets un entrenador expert en Brazilian Jiu-Jitsu i grappling.

La teva tasca és comparar dos anàlisis del mateix lluitador:
- un anàlisi antic
- un anàlisi recent

Has de detectar:
- millores tècniques
- empitjoraments
- patrons que es mantenen
- evolució tàctica
- evolució tècnica
- recomanacions d’entrenament

IMPORTANT:
- No inventis informació.
- Basa’t NOMÉS en els dos anàlisis proporcionats.
- La comparació ha de ser coherent i realista.
- Respon EXCLUSIVAMENT en JSON vàlid.
- No utilitzis markdown.
- No utilitzis blocs ```json.

ANÀLISI ANTIC:
{old_analysis}

ANÀLISI RECENT:
{new_analysis}

RESPON EXACTAMENT AMB AQUEST FORMAT JSON:

{{
  "summary": "resum general de l’evolució",
  "improvements": [
    "millora 1",
    "millora 2"
  ],
  "regressions": [
    "problema 1",
    "problema 2"
  ],
  "stablePatterns": [
    "patró 1",
    "patró 2"
  ],
  "technicalEvolution": "explicació tècnica",
  "tacticalEvolution": "explicació tàctica",
  "recommendedFocus": [
    "focus 1",
    "focus 2"
  ],
  "conclusion": "conclusió final"
}}
"""