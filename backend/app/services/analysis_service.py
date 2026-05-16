import json
import re
import time

from app.services.gemini_client import client
from app.prompts.analysis_prompts import build_prompt
from app.utils.stats import derive_stats_from_timeline

ALLOWED_POSITIONS = {
    "standing",
    "closed_guard_top",
    "closed_guard_bottom",
    "open_guard_top",
    "open_guard_bottom",
    "half_guard_top",
    "half_guard_bottom",
    "side_control_top",
    "side_control_bottom",
    "mount_top",
    "mount_bottom",
    "back_control_top",
    "back_control_bottom",
    "turtle_top",
    "turtle_bottom",
    "scramble",
    "other",
}
ALLOWED_CONTROLLERS = {"oponent_1", "oponent_2", "cap", "incert"}
ALLOWED_TIPUS_EVENT = {
    "inici_intercanvi",
    "control",
    "transicio",
    "intent_finalitzacio",
    "intent_enderroc",
    "guard_pull",
    "escape",
    "reversio",
    "scramble",
    "pausa",
    "finalitzacio",
    "altre",
}
ALLOWED_CONFIANCA = {"alta", "mitjana", "baixa"}

def _analysis_type(profile: str, mode: str) -> str:
    mapping = {
        ("lluitador", "single_athlete"): "auto_analisi",
        ("lluitador", "full_fight"): "combat_lluitador",
        ("entrenador", "single_athlete"): "analisi_alumne",
        ("entrenador", "full_fight"): "combat_entrenador",
    }
    return mapping.get((profile, mode), "auto_analisi")


def _default_response(profile: str, mode: str) -> dict:
    analysis_type = _analysis_type(profile, mode)

    base = {
        "mode": mode,
        "perfil": profile,
        "analysis_type": analysis_type,
        "selected_oponent_id": "desconegut",
        "combat_info": {
            "oponents": [
                {
                    "id": "oponent_1",
                    "nom_visible": "desconegut",
                    "descripcio_visual": "desconegut",
                },
                {
                    "id": "oponent_2",
                    "nom_visible": "desconegut",
                    "descripcio_visual": "desconegut",
                },
            ],
            "durada_estimada": "00:00",
            "nivell_confianca_global": "baixa",
        },
        "resum_partit": {
            "guanyador": {"id": "desconegut", "descripcio": "desconegut"},
            "metode": "desconegut",
            "tipus_submissio": "desconegut",
            "resum_breu": "",
        },
        "timeline": [],
        "incerteses": [],
    }

    if analysis_type == "auto_analisi":
        base["analisi_lluitador"] = {
            "resum_personal": "",
            "tactica_general": "",
            "patrons_tactics": [],
            "fortaleses_clau": [],
            "debilitats_clau": [],
            "errors_i_correccions": [],
            "encerts_clau": [],
            "millores_recomanades": [],
        }

    elif analysis_type == "analisi_alumne":
        base["analisi_lluitador"] = {
            "resum_tecnic": "",
            "model_de_combat": "",
            "lectura_posicional": "",
            "patrons_tactics": [],
            "fortaleses_clau": [],
            "debilitats_clau": [],
            "errors_i_correccions": [],
            "encerts_clau": [],
            "prioritats_de_treball": [],
        }
        base["estadistiques_estimades"] = _default_student_stats()

    elif analysis_type == "combat_lluitador":
        base["analisi_oponents"] = {
            "oponent_1": _default_general_opponent(),
            "oponent_2": _default_general_opponent(),
        }
        base["lectura_global"] = {
            "dinamica_general": "",
            "moments_decisius": [],
            "lliçons_practiques": [],
        }

    elif analysis_type == "combat_entrenador":
        base["analisi_oponents"] = {
            "oponent_1": _default_general_coach_opponent(),
            "oponent_2": _default_general_coach_opponent(),
        }
        base["estadistiques_estimades"] = _default_combat_stats()
        base["lectura_global"] = {
            "dinamica_general": "",
            "moments_decisius": [],
            "claus_tactiques": [],
        }

    return base

def _default_general_opponent() -> dict:
    return {
        "tactica_general": "",
        "patrons_tactics": [],
        "fortaleses_clau": [],
        "debilitats_clau": [],
        "errors_principals": [],
        "encerts_clau": [],
        "resum_rendiment": "",
    }


def _default_general_coach_opponent() -> dict:
    return {
        "tactica_general": "",
        "model_de_combat": "",
        "lectura_posicional": "",
        "patrons_tactics": [],
        "fortaleses_clau": [],
        "debilitats_clau": [],
        "errors_principals": [],
        "encerts_clau": [],
        "resum_rendiment": "",
    }


def _default_student_stats() -> dict:
    return {
        "temps_per_posicio": [],
        "temps_dominant_total": 0,
        "temps_defensiu_total": 0,
        "temps_neutral_total": 0,
        "canvis_control": 0,
        "intents_finalitzacio": 0,
        "intents_enderroc": 0,
        "guard_pulls": 0,
        "reversions": 0,
        "escapades": 0,
    }


def _default_combat_stats() -> dict:
    return {
        "temps_per_posicio": [],
        "temps_dominant_total": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "temps_defensiu_total": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "temps_neutral_total": 0,
        "canvis_control": 0,
        "intents_finalitzacio": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "intents_enderroc": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "guard_pulls": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "reversions": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "escapades": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
    }

def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    cleaned = cleaned.replace("\\'", "'")

    return cleaned.strip()

def _extract_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def _normalize_timeline_event(event: dict) -> dict:
    posicio = event.get("posicio", "other")
    if posicio not in ALLOWED_POSITIONS:
        posicio = "other"

    controlador = event.get("controlador", "incert")
    if controlador not in ALLOWED_CONTROLLERS:
        controlador = "incert"

    tipus_event = event.get("tipus_event", "altre")
    if tipus_event not in ALLOWED_TIPUS_EVENT:
        tipus_event = "altre"

    rellevancia = event.get("rellevancia", 3)
    try:
        rellevancia = int(rellevancia)
    except (TypeError, ValueError):
        rellevancia = 3
    rellevancia = max(1, min(5, rellevancia))

    confianca = event.get("confianca", "mitjana")
    if confianca not in ALLOWED_CONFIANCA:
        confianca = "mitjana"

    return {
        "inici": event.get("inici", "00:00"),
        "fi": event.get("fi", "00:00"),
        "posicio": posicio,
        "controlador": controlador,
        "tipus_event": tipus_event,
        "descripcio": event.get("descripcio", ""),
        "rellevancia": rellevancia,
        "confianca": confianca,
    }


def _safe_parse_response(text: str, profile: str, mode: str) -> dict:
    analysis_type = _analysis_type(profile, mode)
    fallback = _default_response(profile, mode)

    if not text or not text.strip():
        fallback["incerteses"] = ["Resposta buida del model"]
        return fallback

    cleaned = _strip_code_fences(text)
    cleaned = _extract_json_object(cleaned)

    try:
        data = json.loads(cleaned)
        if not isinstance(data, dict):
            fallback["incerteses"] = ["La resposta del model no és un objecte JSON"]
            return fallback

        result = _default_response(profile, mode)

        result["mode"] = mode
        result["perfil"] = profile
        result["analysis_type"] = analysis_type
        result["selected_oponent_id"] = data.get(
            "selected_oponent_id",
            result["selected_oponent_id"],
        )

        if mode == "full_fight":
            result["selected_oponent_id"] = "desconegut"

        if isinstance(data.get("combat_info"), dict):
            combat_info = data["combat_info"]
            result["combat_info"] = {
                "oponents": combat_info.get(
                    "oponents",
                    result["combat_info"]["oponents"],
                ),
                "durada_estimada": combat_info.get("durada_estimada", "00:00"),
                "nivell_confianca_global": combat_info.get(
                    "nivell_confianca_global",
                    "baixa",
                ),
            }

        if isinstance(data.get("resum_partit"), dict):
            resum = data["resum_partit"]
            result["resum_partit"] = {
                "guanyador": resum.get(
                    "guanyador",
                    result["resum_partit"]["guanyador"],
                ),
                "metode": resum.get("metode", "desconegut"),
                "tipus_submissio": resum.get("tipus_submissio", "desconegut"),
                "resum_breu": resum.get("resum_breu", ""),
            }

        raw_timeline = data.get("timeline", [])
        if isinstance(raw_timeline, list):
            result["timeline"] = [
                _normalize_timeline_event(event)
                for event in raw_timeline
                if isinstance(event, dict)
            ]

        if "incerteses" in data and isinstance(data["incerteses"], list):
            result["incerteses"] = data["incerteses"]

        if analysis_type in {"auto_analisi", "analisi_alumne"}:
            if isinstance(data.get("analisi_lluitador"), dict):
                result["analisi_lluitador"] = data["analisi_lluitador"]

            if analysis_type == "analisi_alumne":
                if isinstance(data.get("estadistiques_estimades"), dict):
                    result["estadistiques_estimades"] = data["estadistiques_estimades"]

            result.pop("analisi_oponents", None)
            result.pop("lectura_global", None)

            if analysis_type == "auto_analisi":
                result.pop("estadistiques_estimades", None)

        elif analysis_type in {"combat_lluitador", "combat_entrenador"}:
            if isinstance(data.get("analisi_oponents"), dict):
                result["analisi_oponents"] = data["analisi_oponents"]

            if isinstance(data.get("lectura_global"), dict):
                result["lectura_global"] = data["lectura_global"]

            if analysis_type == "combat_entrenador":
                if isinstance(data.get("estadistiques_estimades"), dict):
                    result["estadistiques_estimades"] = data["estadistiques_estimades"]
            else:
                result.pop("estadistiques_estimades", None)

            result.pop("analisi_lluitador", None)

        return result

    except Exception as e:
        print("ERROR PARSEJANT JSON DE GEMINI:", repr(cleaned))
        print("EXCEPCIÓ:", str(e))
        fallback["incerteses"] = [cleaned]
        return fallback
    
def _wait_until_file_is_active(file_name: str, timeout_seconds: int = 180) -> None:
    """
    Espera fins que el fitxer pujat estigui preparat per a ser utilitzat (en estat ACTIVE). 
    Quan es puja un video a Gemini, el fitxer no queda disponible immediatament, ha d'estar en 
    estat ACTIVE, per ser analitzat correctament. 

    Funciona fent una consulta periòdica a l'estat del fitxer cada 2 segons (polling):
    - si és ACTIVE, acaba
    - si és FAILED, llença una excepció
    - si supera el timeout, llença TimeoutError
    """

    start = time.time()

    while True:
        # Es comprova l'estat del fitxer (PROCESSING, ACTIVE o FAILED)
        current_file = client.files.get(name=file_name)
        state = getattr(current_file, "state", None)

        if state == "ACTIVE" or getattr(state, "name", None) == "ACTIVE":
            return

        if state == "FAILED" or getattr(state, "name", None) == "FAILED":
            raise RuntimeError(f"El fitxer {file_name} ha fallat durant el processament")

        if time.time() - start > timeout_seconds:
            raise TimeoutError(
                f"Timeout esperant a que el fitxer {file_name} passi a ACTIVE"
            )

        time.sleep(2)

def _generate_content_with_retry(uploaded_file, prompt: str, retries: int = 3, wait_seconds: int = 4):
    last_error = None

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                # model="gemini-2.5-flash",
                model = "gemini-2.5-flash-lite",
                contents=[uploaded_file, prompt],
            )
            return response

        except Exception as e:
            last_error = e
            print(f"Intent {attempt + 1} fallit: {str(e)}")

            if attempt < retries - 1:
                time.sleep(wait_seconds)

    raise last_error

def analyze_video(
    file_path: str,
    profile: str,
    mode: str,
    athlete_identifier_type: str | None = None,
    athlete_identifier_value: str | None = None,
) -> dict:
    """
    Analitza un vídeo amb Gemini i retorna el resultat estructurat.

    Procés:
        1. Construeix un prompt segons el perfil rebut.
        2. Afegeix una instrucció perquè Gemini respongui en JSON.
        3. Puja el vídeo a Gemini i espera que el fitxer estigui llest (ACTIVE).
        4. Envia el vídeo i el prompt al model.
        5. Intenta parsejar la resposta i la retorna en format diccionari.

    Paràmetres:
        - file_path: ruta local del fitxer de vídeo
        - profile: perfil d'anàlisi que es farà servir per construir el prompt

    Retorna:
        - diccionari amb summary, key_moments, technical_observations, recommendations i profile
    """
    prompt = build_prompt(
        profile=profile,
        mode=mode,
        athlete_identifier_type=athlete_identifier_type,
        athlete_identifier_value=athlete_identifier_value,
    )
    
    # Puja el vídeo a Gemini perquè el model el pugui processar
    uploaded_file = client.files.upload(file=file_path)

    # Espera a que Gemini acabi de processar el vídeo
    _wait_until_file_is_active(uploaded_file.name)

    # Demana al model que analitzi el vídeo seguint el prompt indicat
    response = _generate_content_with_retry(uploaded_file, prompt)

    parsed = _safe_parse_response(response.text, profile, mode)
    
    analysis_type = _analysis_type(profile, mode)

    if profile == "entrenador" and mode == "full_fight" and parsed.get("timeline"):
        clean_stats = derive_stats_from_timeline(parsed["timeline"])

        parsed["estadistiques_estimades"]["temps_per_posicio"] = clean_stats[
            "temps_per_posicio"
        ]

        parsed["estadistiques_derivades"] = clean_stats
    else:
        parsed.pop("estadistiques_derivades", None)
    
    return parsed