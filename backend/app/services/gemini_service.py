import json
import re
import os
import time
from google import genai
from google.genai import types

from app.utils.prompts import build_prompt
from app.utils.stats import derive_stats_from_timeline

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    "intento_finalitzacio",
    "intento_enderroc",
    "guard_pull",
    "escape",
    "reversio",
    "scramble",
    "pausa",
    "finalitzacio",
    "altre",
}
ALLOWED_CONFIANCA = {"alta", "mitjana", "baixa"}


def _default_response(profile: str) -> dict:
    return {
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
            "perdedor": {"id": "desconegut", "descripcio": "desconegut"},
            "metode": "desconegut",
            "tipus_submissio": "desconegut",
            "resum_breu": "",
        },
        "timeline": [],
        "analisi_oponents": {
            "oponent_1": {
                "tactica_general": "",
                "patrons_tactics": [],
                "fortaleses_clau": [],
                "debilitats_clau": [],
                "errors_detallats": [],
                "encerts_clau": [],
                "sequencies_repetides": [],
                "millores_recomanades": [],
            },
            "oponent_2": {
                "tactica_general": "",
                "patrons_tactics": [],
                "fortaleses_clau": [],
                "debilitats_clau": [],
                "errors_detallats": [],
                "encerts_clau": [],
                "sequencies_repetides": [],
                "millores_recomanades": [],
            },
        },
        "estadistiques_estimades": {
            "temps_per_posicio": [],
            "canvis_control": 0,
            "intents_finalitzacio": 0,
            "intents_enderroc": 0,
            "guard_pulls": 0,
        },
        "patrons_globals": {
            "dinamiques_clau": [],
            "moments_decisius": [],
            "resum_comparable": [],
        },
        "incerteses": [],
        "perfil": profile,
    }


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


def _safe_parse_response(text: str, profile: str) -> dict:
    fallback = _default_response(profile)

    if not text or not text.strip():
        fallback["incerteses"] = ["Resposta buida del model"]
        return fallback

    cleaned = _strip_code_fences(text)
    cleaned = _extract_json_object(cleaned)

    try:
        data = json.loads(cleaned)
        result = _default_response(profile)

        if isinstance(data.get("combat_info"), dict):
            result["combat_info"] = {
                "oponents": data["combat_info"].get("oponents", result["combat_info"]["oponents"]),
                "durada_estimada": data["combat_info"].get("durada_estimada", "00:00"),
                "nivell_confianca_global": data["combat_info"].get("nivell_confianca_global", "baixa"),
            }

        if isinstance(data.get("resum_partit"), dict):
            result["resum_partit"] = {
                "guanyador": data["resum_partit"].get("guanyador", result["resum_partit"]["guanyador"]),
                "perdedor": data["resum_partit"].get("perdedor", result["resum_partit"]["perdedor"]),
                "metode": data["resum_partit"].get("metode", "desconegut"),
                "tipus_submissio": data["resum_partit"].get("tipus_submissio", "desconegut"),
                "resum_breu": data["resum_partit"].get("resum_breu", ""),
            }

        raw_timeline = data.get("timeline", [])
        if isinstance(raw_timeline, list):
            result["timeline"] = [
                _normalize_timeline_event(event)
                for event in raw_timeline
                if isinstance(event, dict)
            ]

        result["analisi_oponents"] = data.get("analisi_oponents", result["analisi_oponents"])
        result["estadistiques_estimades"] = data.get(
            "estadistiques_estimades",
            result["estadistiques_estimades"],
        )
        result["patrons_globals"] = data.get("patrons_globals", result["patrons_globals"])
        result["incerteses"] = data.get("incerteses", [])
        result["perfil"] = profile

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
                model="gemini-2.5-flash",
                contents=[uploaded_file, prompt],
            )
            return response

        except Exception as e:
            last_error = e
            print(f"Intent {attempt + 1} fallit: {str(e)}")

            if attempt < retries - 1:
                time.sleep(wait_seconds)

    raise last_error

def analyze_video(file_path: str, profile: str) -> dict:
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
    prompt = build_prompt(profile)
    
    # Puja el vídeo a Gemini perquè el model el pugui processar
    uploaded_file = client.files.upload(file=file_path)

    # Espera a que Gemini acabi de processar el vídeo
    _wait_until_file_is_active(uploaded_file.name)

    # Demana al model que analitzi el vídeo seguint el prompt indicat
    response = _generate_content_with_retry(uploaded_file, prompt)

    parsed = _safe_parse_response(response.text, profile)

    if parsed.get("timeline"):
        parsed["estadistiques_derivades"] = derive_stats_from_timeline(parsed["timeline"])
    else:
        parsed["estadistiques_derivades"] = {
            "temps_per_posicio": [],
            "temps_dominant_per_lluitador": {},
            "canvis_control_recalculats": 0,
        }

    return parsed