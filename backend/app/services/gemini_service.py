import json
import re
import os
import time
from google import genai
from app.utils.prompts import build_prompt

# Crea instancia del client de Gemini. Llegeix la clau API des de la variable d'entorn GEMINI_API_KEY
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _safe_parse_response(text: str, profile: str) -> dict:
    """
    Funció que intenta convertir la resposta de Gemini a JSON. Serveix per protegir el backend 
    davant respostes inesperades del model. 

    Si la resposta té el format esperat, retorna un diccionari amb els camps principals normalitzats. 
    Si la resposta no té un JSON vàlid, fa un fallback: posa tot el text dins de "summary" i deixa la
    resta de camps com a llistes buides.
    """

    cleaned = text.strip()

    # Treure ```json ... ``` o ``` ... ```
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        return {
            "resum": data.get("resum", ""),
            "moments_clau": data.get("moments_clau", []),
            "observacions_tecniques": data.get("observacions_tecniques", []),
            "recomanacions": data.get("recomanacions", []),
            "perfil": profile,
        }
    except Exception as e:
        print("ERROR PARSEJANT JSON DE GEMINI:", repr(cleaned))
        print("EXCEPCIÓ:", str(e))
        return {
            "resum": cleaned,
            "moments_clau": [],
            "observacions_tecniques": [],
            "recomanacions": [],
            "perfil": profile,
        }


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
    prompt = build_prompt(profile) + """

Respon només amb JSON vàlid.
No afegeixis text extra.
No facis servir blocs Markdown.
No posis ```json.

Format exacte:
{
  "resum": "string",
  "moments_clau": ["string"],
  "observacions_tecniques": ["string"],
  "recomanacions": ["string"]
}
"""
    # Puja el vídeo a Gemini perquè el model el pugui processar
    uploaded_file = client.files.upload(file=file_path)

    # Espera a que Gemini acabi de processar el vídeo
    _wait_until_file_is_active(uploaded_file.name)

    # Demana al model que analitzi el vídeo seguint el prompt indicat
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[uploaded_file, prompt],
    )

    return _safe_parse_response(response.text, profile)