import json
import os
import re
import time
from typing import Any

from google import genai

from app.utils.scouting_prompts import build_scouting_prompt

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _default_response(profile: str) -> dict:
    base = {
        "mode": "scouting",
        "perfil": profile,
        "analysis_type": (
            "scouting_entrenador"
            if profile == "entrenador"
            else "scouting_lluitador"
        ),
        "rival_info": {
            "nom_visible": "desconegut",
            "descripcio_visual": "desconegut",
            "nivell_confianca_global": "baixa",
        },
        "resum_rival": "",
        "patrons_recurrents": [],
        "punts_forts": [],
        "debilitats": [],
        "incerteses": [],
    }

    if profile == "entrenador":
        base["informe_entrenador"] = {
            "model_de_combat": "",
            "patrons_ofensius": [],
            "patrons_defensius": [],
            "situacions_on_puntua": [],
            "situacions_on_queda_exposat": [],
            "pla_tactic_recomanat": [],
            "focus_entrenament": [],
            "exercicis_recomanats": [],
            "riscos_principals": [],
        }

        base["estadistiques"] = {
            "nota": "",
            "nivell_fiabilitat_estadistica": "baixa",
            "per_video": [],
            "resum_global": {
                "accions_mes_frequents": [],
                "situacions_mes_repetides": [],
                "zones_de_risc": [],
                "tendencies_tactiques": [],
                "patrons_amb_mes_evidencia": [],
                "patrons_amb_poca_evidencia": [],
            },
            "perfil_numeric": {
                "pressio": "desconegut",
                "agressivitat": "desconegut",
                "control_posicional": "desconegut",
                "defensa": "desconegut",
                "perill_submissio": "desconegut",
                "explosivitat": "desconegut",
                "adaptabilitat": "desconegut",
            },
        }

        base["grafics_suggerits"] = []

    else:
        base["informe_lluitador"] = {
            "amenaces_principals": [],
            "debilitats_a_explotar": [],
            "que_evitar": [],
            "pla_combat": [],
            "consells_clau": [],
            "missatge_final": "",
        }

    return base


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


def _safe_parse_response(text: str, profile: str) -> dict:
    fallback = _default_response(profile)

    if not text or not text.strip():
        fallback["incerteses"] = ["Resposta buida del model"]
        return fallback

    cleaned = _strip_code_fences(text)
    cleaned = _extract_json_object(cleaned)

    try:
        data = json.loads(cleaned)

        if not isinstance(data, dict):
            fallback["incerteses"] = [
                "La resposta del model no és un objecte JSON"
            ]
            return fallback

        result = _default_response(profile)

        for key in result.keys():
            if key in data:
                result[key] = data[key]

        return result

    except Exception:
        fallback["incerteses"] = [
            "No s'ha pogut parsejar la resposta del model com a JSON"
        ]
        return fallback


def _wait_until_file_is_active(
    file_name: str,
    timeout_seconds: int = 180,
) -> None:
    start = time.time()

    while True:
        current_file = client.files.get(name=file_name)

        state = getattr(current_file, "state", None)

        if state == "ACTIVE" or getattr(state, "name", None) == "ACTIVE":
            return

        if state == "FAILED" or getattr(state, "name", None) == "FAILED":
            raise RuntimeError(
                f"El fitxer {file_name} ha fallat durant el processament"
            )

        if time.time() - start > timeout_seconds:
            raise TimeoutError(
                f"Timeout esperant a que el fitxer {file_name} passi a ACTIVE"
            )

        time.sleep(2)


def _generate_content_with_retry(
    contents: list,
    retries: int = 3,
    wait_seconds: int = 4,
):
    last_error = None

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=contents,
            )

            return response

        except Exception as e:
            last_error = e

            print(f"Intent {attempt + 1} fallit: {str(e)}")

            if attempt < retries - 1:
                time.sleep(wait_seconds)

    raise last_error


def analyze_scouting_videos(
    file_paths: list[str],
    profile: str,
    video_descriptions: list[dict[str, Any]],
) -> dict:
    """
    Analitza múltiples vídeos del mateix rival.
    Cada vídeo inclou una descripció textual per identificar quin atleta és el rival.
    """

    if profile not in {"entrenador", "lluitador"}:
        raise ValueError(
            "profile ha de ser 'entrenador' o 'lluitador'"
        )

    if not file_paths:
        fallback = _default_response(profile)

        fallback["incerteses"] = [
            "No s'han proporcionat vídeos"
        ]

        return fallback

    if len(video_descriptions) != len(file_paths):
        fallback = _default_response(profile)

        fallback["incerteses"] = [
            "El nombre de descripcions no coincideix amb el nombre de vídeos"
        ]

        return fallback

    prompt = build_scouting_prompt(
        profile=profile,
        video_descriptions=video_descriptions,
    )

    uploaded_files = []

    for file_path in file_paths:
        uploaded_file = client.files.upload(file=file_path)

        _wait_until_file_is_active(uploaded_file.name)

        uploaded_files.append(uploaded_file)

    response = _generate_content_with_retry(
        uploaded_files + [prompt]
    )

    parsed = _safe_parse_response(
        response.text,
        profile,
    )

    return parsed