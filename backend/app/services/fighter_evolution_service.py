import json
import re
import time

from app.services.gemini_client import client
from app.prompts.evolution_prompts import build_evolution_prompt


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()

    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    return cleaned.strip()


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]

    return text


def _safe_parse_response(text: str) -> dict:
    fallback = {
        "mode": "evolucio",
        "analysis_type": "evolucio_lluitador",
        "fighter_info": {
            "nom_visible": "desconegut",
            "descripcio_visual": "desconegut",
            "confianca_analisi": "baixa",
        },
        "resum_evolucio": "",
        "magnitud_canvi_global": "baixa",
        "millores": [],
        "regressions": [],
        "patrons_estables": {
            "fortaleses_consolidades": [],
            "debilitats_persistents": [],
        },
        "evolucio_tactica": {
            "model_antic": "",
            "model_recent": "",
            "canvi_observat": "",
            "interpretacio": "",
        },
        "evolucio_tecnica": {
            "tecniques_millorades": [],
            "tecniques_empitjorades": [],
            "tecniques_noves": [],
            "tecniques_abandonades": [],
        },
        "comparativa_numerica": {
            "nota": "No hi ha dades suficients.",
            "disponible": False,
            "perfil_antic": {
                "pressio": -1,
                "agressivitat": -1,
                "control_posicional": -1,
                "defensa": -1,
                "perill_submissio": -1,
                "explosivitat": -1,
                "adaptabilitat": -1,
            },
            "perfil_recent": {
                "pressio": -1,
                "agressivitat": -1,
                "control_posicional": -1,
                "defensa": -1,
                "perill_submissio": -1,
                "explosivitat": -1,
                "adaptabilitat": -1,
            },
            "deltes": {
                "nota": "No calculable.",
                "pressio": None,
                "agressivitat": None,
                "control_posicional": None,
                "defensa": None,
                "perill_submissio": None,
                "explosivitat": None,
                "adaptabilitat": None,
            },
        },
        "grafics_suggerits": [],
        "recomanacions_entrenament": {
            "prioritat_alta": [],
            "prioritat_mitjana": [],
            "manteniment": [],
        },
        "conclusio": "",
        "incerteses": ["No s'ha pogut parsejar correctament la resposta del model."],
    }

    if not text or not text.strip():
        return fallback

    try:
        cleaned = _strip_code_fences(text)
        cleaned = _extract_json_object(cleaned)
        data = json.loads(cleaned)

        if not isinstance(data, dict):
            return fallback

        return {**fallback, **data}

    except Exception as e:
        print("ERROR PARSEJANT EVOLUTION JSON")
        print(str(e))
        print(text)
        return fallback


def _generate_content_with_retry(prompt: str, retries: int = 3):
    last_error = None

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
            )

            return response

        except Exception as e:
            last_error = e

            print(f"Intent {attempt + 1} fallit: {str(e)}")

            if attempt < retries - 1:
                time.sleep(4)

    raise last_error


def _extract_usage_metadata(response) -> dict:
    """
    Extreu la informació de consum de tokens retornada per Gemini.

    usage_metadata pot incloure:
        - prompt_token_count: tokens d'entrada
        - candidates_token_count: tokens de sortida
        - total_token_count: tokens totals
    """

    usage = getattr(response, "usage_metadata", None)

    if usage is None:
        return {
            "prompt_token_count": 0,
            "candidates_token_count": 0,
            "total_token_count": 0,
        }

    return {
        "prompt_token_count": int(getattr(usage, "prompt_token_count", 0) or 0),
        "candidates_token_count": int(getattr(usage, "candidates_token_count", 0) or 0),
        "total_token_count": int(getattr(usage, "total_token_count", 0) or 0),
    }


def analyze_fighter_evolution(
    old_analysis: dict,
    new_analysis: dict,
) -> dict:
    prompt = build_evolution_prompt(
        old_analysis=old_analysis,
        new_analysis=new_analysis,
    )

    response = _generate_content_with_retry(prompt)

    usage_metadata = _extract_usage_metadata(response)

    print(json.dumps({
        "event": "gemini_usage",
        "service": "fighter_evolution",
        "mode": "evolucio",
        "model": "gemini-2.5-flash-lite",
        "tokens": usage_metadata,
    }, ensure_ascii=False))

    parsed = _safe_parse_response(response.text)

    parsed["debug_tokens"] = usage_metadata

    return parsed