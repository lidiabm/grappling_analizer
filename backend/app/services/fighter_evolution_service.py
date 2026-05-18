import json
import re
import time

from app.services.gemini_client import client
from app.prompts.evolution_prompt import build_evolution_prompt


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
        "summary": "",
        "improvements": [],
        "regressions": [],
        "stablePatterns": [],
        "technicalEvolution": "",
        "tacticalEvolution": "",
        "recommendedFocus": [],
        "conclusion": "",
    }

    if not text or not text.strip():
        return fallback

    try:
        cleaned = _strip_code_fences(text)
        cleaned = _extract_json_object(cleaned)

        data = json.loads(cleaned)

        if not isinstance(data, dict):
            return fallback

        return {
            "summary": data.get("summary", ""),
            "improvements": data.get("improvements", []),
            "regressions": data.get("regressions", []),
            "stablePatterns": data.get("stablePatterns", []),
            "technicalEvolution": data.get("technicalEvolution", ""),
            "tacticalEvolution": data.get("tacticalEvolution", ""),
            "recommendedFocus": data.get("recommendedFocus", []),
            "conclusion": data.get("conclusion", ""),
        }

    except Exception as e:
        print("ERROR PARSEJANT EVOLUTION JSON")
        print(str(e))

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


def analyze_fighter_evolution(
    old_analysis: dict,
    new_analysis: dict,
) -> dict:
    prompt = build_evolution_prompt(
        old_analysis=old_analysis,
        new_analysis=new_analysis,
    )

    response = _generate_content_with_retry(prompt)

    parsed = _safe_parse_response(response.text)

    return parsed