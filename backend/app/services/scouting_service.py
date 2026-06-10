import json
import re
import time
from typing import Any
from google.genai import types

from app.services.gemini_client import client
from app.prompts.scouting_prompts import build_scouting_prompt
from app.schemas.scouting import ScoutingResponse

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
                "pressio": -1,
                "agressivitat": -1,
                "control_posicional": -1,
                "defensa": -1,
                "perill_submissio": -1,
                "explosivitat": -1,
                "adaptabilitat": -1,
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
            "clau_tactica": "",
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

def _as_list(value, max_items: int = 5) -> list[str]:
    if not isinstance(value, list):
        return []

    result = []

    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())

    return result[:max_items]


def _as_int_or_unknown(value) -> int | str:
    if value == "desconegut":
        return "desconegut"

    try:
        number = int(value)
    except (TypeError, ValueError):
        return "desconegut"

    if number < 0:
        return "desconegut"

    return number


def _as_profile_score(value) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return -1

    return max(-1, min(10, number))


def _normalize_numeric_profile(value: dict | None) -> dict:
    if not isinstance(value, dict):
        value = {}

    return {
        "pressio": _as_profile_score(value.get("pressio")),
        "agressivitat": _as_profile_score(value.get("agressivitat")),
        "control_posicional": _as_profile_score(value.get("control_posicional")),
        "defensa": _as_profile_score(value.get("defensa")),
        "perill_submissio": _as_profile_score(value.get("perill_submissio")),
        "explosivitat": _as_profile_score(value.get("explosivitat")),
        "adaptabilitat": _as_profile_score(value.get("adaptabilitat")),
    }


def _normalize_per_video_stats(items) -> list[dict]:
    if not isinstance(items, list):
        return []

    result = []

    for item in items:
        if not isinstance(item, dict):
            continue

        seguiment = item.get("seguiment_rival", "incert")
        if seguiment not in {"clar", "parcial", "incert"}:
            seguiment = "incert"

        result.append({
            "video": item.get("video", "desconegut"),
            "fitxer": str(item.get("fitxer", "desconegut")),
            "seguiment_rival": seguiment,
            "atacs_iniciats": _as_int_or_unknown(item.get("atacs_iniciats")),
            "atacs_efectius": _as_int_or_unknown(item.get("atacs_efectius")),
            "intents_passada_guardia": _as_int_or_unknown(item.get("intents_passada_guardia")),
            "passades_guardia_efectives": _as_int_or_unknown(item.get("passades_guardia_efectives")),
            "raspades_intentades": _as_int_or_unknown(item.get("raspades_intentades")),
            "raspades_efectives": _as_int_or_unknown(item.get("raspades_efectives")),
            "submissions_intentades": _as_int_or_unknown(item.get("submissions_intentades")),
            "submissions_encaixades": _as_int_or_unknown(item.get("submissions_encaixades")),
            "recuperacions_guardia": _as_int_or_unknown(item.get("recuperacions_guardia")),
            "perdues_posicio": _as_int_or_unknown(item.get("perdues_posicio")),
            "temps_dominant_aproximat": str(item.get("temps_dominant_aproximat", "desconegut")),
            "situacions_mes_frequents": _as_list(item.get("situacions_mes_frequents")),
            "observacions": _as_list(item.get("observacions")),
        })

    return result


def _normalize_scouting_stats(value: dict | None) -> dict:
    if not isinstance(value, dict):
        value = {}

    nivell = value.get("nivell_fiabilitat_estadistica", "baixa")
    if nivell not in {"alta", "mitjana", "baixa"}:
        nivell = "baixa"

    resum_global = value.get("resum_global", {})
    if not isinstance(resum_global, dict):
        resum_global = {}

    return {
        "nota": str(value.get("nota", "")),
        "nivell_fiabilitat_estadistica": nivell,
        "per_video": _normalize_per_video_stats(value.get("per_video")),
        "resum_global": {
            "accions_mes_frequents": _as_list(resum_global.get("accions_mes_frequents")),
            "situacions_mes_repetides": _as_list(resum_global.get("situacions_mes_repetides")),
            "zones_de_risc": _as_list(resum_global.get("zones_de_risc")),
            "tendencies_tactiques": _as_list(resum_global.get("tendencies_tactiques")),
            "patrons_amb_mes_evidencia": _as_list(resum_global.get("patrons_amb_mes_evidencia")),
            "patrons_amb_poca_evidencia": _as_list(resum_global.get("patrons_amb_poca_evidencia")),
        },
        "perfil_numeric": _normalize_numeric_profile(value.get("perfil_numeric")),
    }


def _sum_known(per_video: list[dict], key: str) -> int:
    total = 0

    for item in per_video:
        value = item.get(key)

        if isinstance(value, int):
            total += value

    return total


def _build_scouting_charts(stats: dict) -> list[dict]:
    per_video = stats.get("per_video", [])
    perfil_numeric = stats.get("perfil_numeric", {})

    action_values = [
        ("Atacs iniciats", _sum_known(per_video, "atacs_iniciats")),
        ("Atacs efectius", _sum_known(per_video, "atacs_efectius")),
        ("Intents passada", _sum_known(per_video, "intents_passada_guardia")),
        ("Passades efectives", _sum_known(per_video, "passades_guardia_efectives")),
        ("Raspades intentades", _sum_known(per_video, "raspades_intentades")),
        ("Raspades efectives", _sum_known(per_video, "raspades_efectives")),
        ("Submissions intentades", _sum_known(per_video, "submissions_intentades")),
        ("Submissions encaixades", _sum_known(per_video, "submissions_encaixades")),
        ("Recuperacions guàrdia", _sum_known(per_video, "recuperacions_guardia")),
        ("Pèrdues posició", _sum_known(per_video, "perdues_posicio")),
    ]

    frequencia_accions = [
        {"label": label, "valor": value}
        for label, value in action_values
        if value > 0
    ]

    perfil_tactic = [
        {"label": "pressio", "valor": perfil_numeric.get("pressio", -1)},
        {"label": "agressivitat", "valor": perfil_numeric.get("agressivitat", -1)},
        {"label": "control_posicional", "valor": perfil_numeric.get("control_posicional", -1)},
        {"label": "defensa", "valor": perfil_numeric.get("defensa", -1)},
        {"label": "perill_submissio", "valor": perfil_numeric.get("perill_submissio", -1)},
        {"label": "explosivitat", "valor": perfil_numeric.get("explosivitat", -1)},
        {"label": "adaptabilitat", "valor": perfil_numeric.get("adaptabilitat", -1)},
    ]

    perfil_tactic = [
        item for item in perfil_tactic
        if isinstance(item["valor"], int) and item["valor"] >= 0
    ]

    charts = []

    if frequencia_accions:
        charts.append({
            "id": "frequencia_accions",
            "tipus": "barres",
            "titol": "Freqüència d'accions observades",
            "descripcio": "Recompte total d'accions observades en tots els vídeos.",
            "dades": frequencia_accions,
            "escala": None,
            "interpretacio": "Mostra quines accions apareixen amb més freqüència en el comportament del rival.",
        })

    if perfil_tactic:
        charts.append({
            "id": "perfil_tactic",
            "tipus": "radar",
            "titol": "Perfil tàctic del rival",
            "descripcio": "Valoració tàctica estimada a partir de les accions observades.",
            "dades": perfil_tactic,
            "escala": "0-10",
            "interpretacio": "Resumeix les dimensions tàctiques més destacades del rival.",
        })

    return charts

def _safe_parse_response(text: str, profile: str) -> dict:
    fallback = _default_response(profile)

    if not text or not text.strip():
        fallback["incerteses"] = ["Resposta buida del model"]
        return fallback

    cleaned = _strip_code_fences(text)
    cleaned = _extract_json_object(cleaned)

    try:
        data = json.loads(cleaned)
    except Exception as e:
        print("===== JSON PARSE ERROR =====")
        print(str(e))
        print("===== RAW TEXT START =====")
        print(text)
        print("===== RAW TEXT END =====")
        print("===== CLEANED TEXT START =====")
        print(cleaned)
        print("===== CLEANED TEXT END =====")

        fallback["incerteses"] = [
            f"No s'ha pogut parsejar la resposta del model com a JSON: {str(e)}"
        ]
        return fallback

    if not isinstance(data, dict):
        fallback["incerteses"] = [
            "La resposta del model no és un objecte JSON"
        ]
        return fallback

    result = _default_response(profile)

    rival_info = data.get("rival_info", {})
    if not isinstance(rival_info, dict):
        rival_info = {}

    nivell_confianca = rival_info.get("nivell_confianca_global", "baixa")
    if nivell_confianca not in {"alta", "mitjana", "baixa", "insuficient"}:
        nivell_confianca = "baixa"

    result["rival_info"] = {
        "nom_visible": str(rival_info.get("nom_visible", "desconegut")),
        "descripcio_visual": str(rival_info.get("descripcio_visual", "desconegut")),
        "nivell_confianca_global": nivell_confianca,
    }

    result["resum_rival"] = str(data.get("resum_rival", ""))
    result["patrons_recurrents"] = _as_list(data.get("patrons_recurrents"))
    result["punts_forts"] = _as_list(data.get("punts_forts"))
    result["debilitats"] = _as_list(data.get("debilitats"))
    result["incerteses"] = _as_list(data.get("incerteses"))

    if profile == "lluitador":
        informe = data.get("informe_lluitador", {})
        if not isinstance(informe, dict):
            informe = {}

        result["informe_lluitador"] = {
            "amenaces_principals": _as_list(informe.get("amenaces_principals")),
            "debilitats_a_explotar": _as_list(informe.get("debilitats_a_explotar")),
            "que_evitar": _as_list(informe.get("que_evitar")),
            "pla_combat": _as_list(informe.get("pla_combat"), max_items=3),
            "consells_clau": _as_list(informe.get("consells_clau")),
            "clau_tactica": str(informe.get("clau_tactica", "")),
        }

        result["informe_entrenador"] = None
        result["estadistiques"] = None
        result["grafics_suggerits"] = None

    else:
        informe = data.get("informe_entrenador", {})
        if not isinstance(informe, dict):
            informe = {}

        result["informe_entrenador"] = {
            "model_de_combat": str(informe.get("model_de_combat", "")),
            "patrons_ofensius": _as_list(informe.get("patrons_ofensius")),
            "patrons_defensius": _as_list(informe.get("patrons_defensius")),
            "situacions_on_puntua": _as_list(informe.get("situacions_on_puntua")),
            "situacions_on_queda_exposat": _as_list(informe.get("situacions_on_queda_exposat")),
            "pla_tactic_recomanat": _as_list(informe.get("pla_tactic_recomanat"), max_items=3),
            "focus_entrenament": _as_list(informe.get("focus_entrenament")),
            "exercicis_recomanats": _as_list(informe.get("exercicis_recomanats")),
            "riscos_principals": _as_list(informe.get("riscos_principals")),
        }

        stats = _normalize_scouting_stats(data.get("estadistiques"))

        result["estadistiques"] = stats
        result["grafics_suggerits"] = _build_scouting_charts(stats)
        result["informe_lluitador"] = None

    return result

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
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            return response

        except Exception as e:
            last_error = e

            print(f"Intent {attempt + 1} fallit: {str(e)}")

            if attempt < retries - 1:
                time.sleep(wait_seconds)

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

    usage_metadata = _extract_usage_metadata(response)

    print(json.dumps({
        "event": "gemini_usage",
        "analysis": "scouting",
        "profile": profile,
        "videos_count": len(file_paths),
        "tokens": usage_metadata,
    }, ensure_ascii=False))

    parsed = _safe_parse_response(
        response.text,
        profile,
    )

    validated = ScoutingResponse.model_validate(parsed)

    return validated.model_dump()