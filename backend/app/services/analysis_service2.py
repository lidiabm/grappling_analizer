#analysis_service2.py
import json
import re
import time

from app.services.gemini_client import client
# from app.prompts.analysis_prompts import build_prompt
from app.prompts.analysis_prompts2 import build_prompt

from app.utils.stats import derive_stats_from_timeline

ALLOWED_POSITIONS = {
    "standing",
    "closed_guard",
    "open_guard",
    "half_guard",
    "side_control",
    "mount",
    "back_control",
    "turtle",
    "scramble",
    "other",
}

ALLOWED_CONTROLLERS = {"oponent_1", "oponent_2", "desconegut"}

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
    "avantatge_posicional",
    "altre",
}

ALLOWED_CONFIANCA = {"alta", "mitjana", "baixa"}

ALLOWED_SUBMISSION_TYPES = {
    "estrangulacio",
    "armbar",
    "triangle",
    "kimura",
    "americana",
    "leg_lock",
    "ankle_lock",
    "heel_hook",
    "kneebar",
    "toe_hold",
    "guillotine",
    "rear_naked_choke",
    "omoplata",
    "altra",
    "desconegut",
}

def _empty_counter() -> dict:
    return {"oponent_1": 0, "oponent_2": 0}


def _normalize_counter(value) -> dict:
    if isinstance(value, dict):
        return {
            "oponent_1": int(value.get("oponent_1", 0) or 0),
            "oponent_2": int(value.get("oponent_2", 0) or 0),
        }
    return _empty_counter()

def _empty_attempt_counter() -> dict:
    return {
        "oponent_1": {"intents": 0, "reeixits": 0},
        "oponent_2": {"intents": 0, "reeixits": 0},
    }

def _normalize_attempt_counter(value) -> dict:
    result = _empty_attempt_counter()
    if not isinstance(value, dict):
        return result
    for oponent in ("oponent_1", "oponent_2"):
        v = value.get(oponent, {})
        if isinstance(v, dict):
            result[oponent]["intents"] = int(v.get("intents", 0) or 0)
            result[oponent]["reeixits"] = int(v.get("reeixits", 0) or 0)
        elif isinstance(v, int):
            # compatibilidad con formato antiguo
            result[oponent]["intents"] = v
    return result

def _normalize_estadistiques(stats: dict) -> dict:
    if not isinstance(stats, dict):
        return _default_combat_stats()

    resum = stats.get("resum_accions", {}) or {}

    temps_per_posicio = []
    for item in stats.get("temps_per_posicio", []) or []:
        if not isinstance(item, dict):
            continue

        posicio = item.get("posicio", "other")
        if posicio not in ALLOWED_POSITIONS:
            posicio = "other"

        controlador = item.get("controlador", item.get("lluitador", "desconegut"))
        if controlador not in ALLOWED_CONTROLLERS:
            controlador = "desconegut"

        temps_per_posicio.append({
            "posicio": posicio,
            "controlador": controlador,
            "segons": int(item.get("segons", 0) or 0),
            "percentatge": float(item.get("percentatge", 0) or 0),
        })

    accions_clau = []
    for accio in stats.get("accions_clau", []) or []:
        if not isinstance(accio, dict):
            continue

        lluitador = accio.get("lluitador")
        if lluitador not in {"oponent_1", "oponent_2"}:
            continue

        tipus = accio.get("tipus")
        if tipus not in {
            "intent_finalitzacio",
            "intent_enderroc",
            "guard_pull",
            "reversio",
            "escapada",
        }:
            continue

        accions_clau.append({
            "temps": accio.get("temps", "00:00"),
            "lluitador": lluitador,
            "tipus": tipus,
            "detall": accio.get("detall", accio.get("descripcio", "")),
            "confianca": accio.get("confianca", "mitjana")
            if accio.get("confianca") in ALLOWED_CONFIANCA
            else "mitjana",
        })

    return {
        "duracio_total_segons": int(stats.get("duracio_total_segons", 0) or 0),
        "temps_per_posicio": temps_per_posicio,
        "temps_dominant_total": _normalize_counter(
            stats.get("temps_dominant_total")
        ),
        "accions_clau": accions_clau,
        "resum_accions": {
            "intents_finalitzacio": _normalize_attempt_counter(
                resum.get("intents_finalitzacio")
            ),
            "intents_enderroc": _normalize_attempt_counter(
                resum.get("intents_enderroc")
            ),
            "guard_pulls": _normalize_counter(
                resum.get("guard_pulls")
            ),
            "reversions": _normalize_counter(
                resum.get("reversions")
            ),
            "escapades": _normalize_counter(
                resum.get("escapades")
            ),
            "canvis_control": int(resum.get("canvis_control", 0) or 0),
        },
    }

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
        "millores_recomanades": [],
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
        "prioritats_de_treball": [],
        "resum_rendiment": "",
    }


def _default_student_stats() -> dict:
    return _default_combat_stats()

def _default_combat_stats() -> dict:
    return {
        "duracio_total_segons": 0,
        "temps_per_posicio": [],
        "temps_dominant_total": {
            "oponent_1": 0,
            "oponent_2": 0,
        },
        "accions_clau": [],
        "resum_accions": {
            "intents_finalitzacio": {
                "oponent_1": {"intents": 0, "reeixits": 0},
                "oponent_2": {"intents": 0, "reeixits": 0},
            },
            "intents_enderroc": {
                "oponent_1": {"intents": 0, "reeixits": 0},
                "oponent_2": {"intents": 0, "reeixits": 0},
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
            "canvis_control": 0,
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

    controlador = event.get("controlador", "desconegut")
    if controlador not in ALLOWED_CONTROLLERS:
        controlador = "desconegut"

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

def _normalize_submission_type(value) -> str:
    if not isinstance(value, str):
        return "desconegut"

    cleaned = value.strip().lower()

    if "|" in cleaned:
        return "desconegut"

    mapping = {
        "strangle": "estrangulacio",
        "choke": "estrangulacio",
        "estrangulacio": "estrangulacio",
        "estrangulació": "estrangulacio",
        "estrangulación": "estrangulacio",
        "rear naked choke": "rear_naked_choke",
        "mata-lleó": "rear_naked_choke",
        "mata lleó": "rear_naked_choke",
        "mata-leao": "rear_naked_choke",
        "mata leao": "rear_naked_choke",
        "guillotine": "guillotine",
        "guillotina": "guillotine",
        "leglock": "leg_lock",
        "leg lock": "leg_lock",
        "clau de cama": "leg_lock",
        "clau de peu": "leg_lock",
        "ankle lock": "ankle_lock",
        "heel hook": "heel_hook",
        "kneebar": "kneebar",
        "toe hold": "toe_hold",
        "armbar": "armbar",
        "clau de braç": "armbar",
        "triangle": "triangle",
        "kimura": "kimura",
        "americana": "americana",
        "omoplata": "omoplata",
        "other": "altra",
        "altra": "altra",
        "desconegut": "desconegut",
    }

    normalized = mapping.get(cleaned, cleaned)

    if normalized not in ALLOWED_SUBMISSION_TYPES:
        return "desconegut"

    return normalized


def _safe_parse_response(text: str, profile: str, mode: str) -> dict:
    analysis_type = _analysis_type(profile, mode)

    if not text or not text.strip():
        raise ValueError("Resposta buida del model")

    cleaned = _strip_code_fences(text)
    cleaned = _extract_json_object(cleaned)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("ERROR PARSEJANT JSON DE GEMINI:")
        print(cleaned[:3000])
        raise ValueError(f"Gemini ha retornat JSON invàlid: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("La resposta del model no és un objecte JSON")

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

            metode = resum.get("metode", "desconegut")
            tipus_submissio = resum.get("tipus_submissio", "desconegut")

            if metode != "submissio":
                tipus_submissio = "desconegut"
            else:
                tipus_submissio = _normalize_submission_type(tipus_submissio)

            result["resum_partit"] = {
                "guanyador": resum.get(
                    "guanyador",
                    result["resum_partit"]["guanyador"],
                ),
                "perdedor": resum.get("perdedor"),
                "metode": metode,
                "tipus_submissio": tipus_submissio,
                "resum_breu": resum.get("resum_breu", ""),
            }

    raw_timeline = data.get("timeline", [])
    if isinstance(raw_timeline, list):
        result["timeline"] = [
            _normalize_timeline_event(event)
            for event in raw_timeline
            if isinstance(event, dict)
        ]

    if isinstance(data.get("incerteses"), list):
        result["incerteses"] = data["incerteses"]

    if analysis_type in {"auto_analisi", "analisi_alumne"}:
        if isinstance(data.get("analisi_lluitador"), dict):
            result["analisi_lluitador"] = data["analisi_lluitador"]

        if analysis_type == "analisi_alumne":
            result["estadistiques_estimades"] = _default_combat_stats()

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
            result["estadistiques_estimades"] = _default_combat_stats()
        else:
            result.pop("estadistiques_estimades", None)

        result.pop("analisi_lluitador", None)

    return result
  
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

def _ensure_analysis_content(parsed: dict) -> None:
    # --- single_athlete: actúa sobre analisi_lluitador ---
    analysis = parsed.get("analisi_lluitador")
    if isinstance(analysis, dict):
        if not analysis.get("tactica_general"):
            analysis["tactica_general"] = (
                "S'ha observat una tàctica basada en la disputa posicional i la recerca de control."
            )
        if not analysis.get("model_de_combat"):
            analysis["model_de_combat"] = (
                "Model de combat orientat a competir per la posició i estabilitzar els intercanvis."
            )
        if not analysis.get("lectura_posicional"):
            analysis["lectura_posicional"] = (
                "El rendiment mostra fases de transició, control i defensa que cal consolidar millor."
            )
        if not analysis.get("patrons_tactics"):
            analysis["patrons_tactics"] = ["Recerca de control després dels intercanvis."]
        if not analysis.get("fortaleses_clau"):
            analysis["fortaleses_clau"] = ["Manté activitat durant les fases principals del combat."]
        if not analysis.get("debilitats_clau"):
            analysis["debilitats_clau"] = ["Necessita consolidar millor les posicions després de les transicions."]
        if not analysis.get("millores_recomanades"):
            analysis["millores_recomanades"] = [
                {
                    "prioritat": "mitjana",
                    "millora": "Consolidar el control posicional després de les transicions.",
                    "objectiu": "Estabilitzar posicions de domini per crear oportunitats de finalització.",
                    "benefici_esperat": "Reducció d'escapades del rival i major temps en posicions avantatjoses.",
                }
            ]
        if not analysis.get("prioritats_de_treball"):
            analysis["prioritats_de_treball"] = [
                {
                    "prioritat": "mitjana",
                    "area": "Control posicional",
                    "problema_tecnic": "Pèrdua de posicions dominants durant les transicions.",
                    "objectiu": "Consolidar el control i reduir la mobilitat del rival.",
                }
            ]

    # --- full_fight: actúa sobre cada oponent dins analisi_oponents ---
    analisi_oponents = parsed.get("analisi_oponents")
    if isinstance(analisi_oponents, dict):
        for oponent_id in ("oponent_1", "oponent_2"):
            op = analisi_oponents.get(oponent_id)
            if not isinstance(op, dict):
                continue

            if not op.get("tactica_general"):
                op["tactica_general"] = "S'ha observat una tàctica basada en la disputa posicional."
            if not op.get("patrons_tactics"):
                op["patrons_tactics"] = ["Recerca de control i oportunitats ofensives."]
            if not op.get("fortaleses_clau"):
                op["fortaleses_clau"] = ["Manté activitat durant les fases principals del combat."]
            if not op.get("debilitats_clau"):
                op["debilitats_clau"] = ["Necessita consolidar millor les posicions clau."]

            # combat_lluitador → millores_recomanades
            if "millores_recomanades" in op and not op["millores_recomanades"]:
                op["millores_recomanades"] = [
                    {
                        "prioritat": "mitjana",
                        "millora": "Millorar la gestió de les transicions posicionals.",
                        "objectiu": "Reduir l'exposició a finalitzacions durant els canvis de posició.",
                        "benefici_esperat": "Major control del combat i menys risc de derrota per submissió.",
                    }
                ]

            # combat_entrenador → prioritats_de_treball
            if "prioritats_de_treball" in op and not op["prioritats_de_treball"]:
                op["prioritats_de_treball"] = [
                    {
                        "prioritat": "mitjana",
                        "area": "Gestió de transicions",
                        "problema_tecnic": "Exposició durant els canvis de posició.",
                        "objectiu": "Reduir el risc de finalització en fases de transició.",
                    }
                ] 

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
        - mode: tipus d'anàlisi que es vol generar
        - athlete_identifier_type: tipus d'identificador de l'atleta, si aplica
        - athlete_identifier_value: valor de l'identificador de l'atleta, si aplica

    Retorna:
        - diccionari amb el resultat estructurat de l'anàlisi
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

    # Extreu el consum de tokens retornat per Gemini
    usage_metadata = _extract_usage_metadata(response)

    # Mostra el consum de tokens només a la consola del backend
    print(json.dumps({
        "event": "gemini_usage",
        "profile": profile,
        "mode": mode,
        "athlete_identifier_type": athlete_identifier_type,
        "athlete_identifier_value": athlete_identifier_value,
        "tokens": usage_metadata,
    }, ensure_ascii=False))

    # Parseja la resposta del model
    parsed = _safe_parse_response(response.text, profile, mode)

    _ensure_analysis_content(parsed)

    # En mode entrenador + combat complet, les estadístiques han de sortir
    # del timeline normalitzat, no directament de Gemini.
    # Així evitem llistes gegants o duplicades a "temps_per_posicio".
    if profile == "entrenador" and parsed.get("timeline"):
        clean_stats = derive_stats_from_timeline(parsed["timeline"])
        clean_stats = _normalize_estadistiques(clean_stats)

        parsed["estadistiques_estimades"] = clean_stats
        parsed["estadistiques_derivades"] = clean_stats

    else:
        parsed.pop("estadistiques_derivades", None)

    parsed["debug_request"] = {
        "profile": profile,
        "mode": mode,
        "athlete_identifier_type": athlete_identifier_type,
        "athlete_identifier_value": athlete_identifier_value,
    }

    return parsed