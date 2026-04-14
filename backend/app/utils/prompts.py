def build_prompt(profile: str) -> str:
    base = """
Analitza aquest vídeo d’un combat de grappling.

Retorna la resposta exclusivament en català.
No inventis dades si el vídeo no permet assegurar-les.
"""

    if profile == "entrenador":
        return base + """
Enfoca l’anàlisi per a un ENTRENADOR.
Prioritza:
- patrons tàctics
- presa de decisions
- moments de control i pèrdua d’iniciativa
- possibles línies de millora per als entrenaments
"""
    else:
        return base + """
Enfoca l’anàlisi per a un LLUITADOR.
Prioritza:
- errors tècnics
- encerts
- moments clau
- recomanacions pràctiques per millorar
"""