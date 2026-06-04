# stats.py

from collections import defaultdict

VALID_POSITIONS = {
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

VALID_CONTROLLERS = {"oponent_1", "oponent_2", "desconegut"}

COUNTABLE_ACTIONS = {
    "intent_finalitzacio": "intents_finalitzacio",
    "finalitzacio": "intents_finalitzacio",
    "intent_enderroc": "intents_enderroc",
    "guard_pull": "guard_pulls",
    "reversio": "reversions",
    "escape": "escapades",
}


def _empty_counter() -> dict:
    return {
        "oponent_1": 0,
        "oponent_2": 0,
    }

def _empty_attempt_counter() -> dict:
    return {
        "oponent_1": {"intents": 0, "reeixits": 0},
        "oponent_2": {"intents": 0, "reeixits": 0},
    }

def _is_successful_action(event: dict, action_key: str, tipus_event: str) -> bool:
    descripcio = event.get("descripcio", "").lower()

    if tipus_event == "finalitzacio" or event.get("tipus_event") == "finalitzacio":
        return True

    if action_key == "intents_finalitzacio":
        return any(word in descripcio for word in [
            "finalitza",
            "finalització",
            "submissió confirmada",
            "tap",
            "rendició",
            "abandona",
            "acaba amb submissió",
            "aconsegueix la submissió",
        ])

    if action_key == "intents_enderroc":
        return any(word in descripcio for word in [
            "reeix",
            "èxit",
            "exitós",
            "aconsegueix",
            "completa",
            "porta a terra",
            "porta l'oponent a terra",
            "queda per sobre",
            "estableix control",
            "control consolidat",
            "enderroc reeixit",
            "derribo exitoso",
            "takedown successful",
        ])

    return False

def mmss_to_seconds(value: str) -> int:
    if not value or ":" not in value:
        return 0

    parts = value.split(":")
    if len(parts) != 2:
        return 0

    try:
        minutes = int(parts[0])
        seconds = int(parts[1])

        if minutes < 0 or seconds < 0:
            return 0

        return minutes * 60 + seconds
    except ValueError:
        return 0

def derive_stats_from_timeline(timeline: list[dict]) -> dict:
    time_by_position_and_controller = defaultdict(int)
    dominant_time = _empty_counter()

    resum_accions = {
        "intents_finalitzacio": _empty_attempt_counter(),
        "intents_enderroc": _empty_attempt_counter(),
        "guard_pulls": _empty_counter(),
        "reversions": _empty_counter(),
        "escapades": _empty_counter(),
        "canvis_control": 0,
    }

    accions_clau = []
    total_time = 0
    previous_controller = None
    finalitzacio_comptada = False

    for event in timeline:
        if not isinstance(event, dict):
            continue

        start = mmss_to_seconds(event.get("inici", "00:00"))
        end = mmss_to_seconds(event.get("fi", "00:00"))
        duration = max(0, end - start)

        if duration <= 0:
            continue

        position = event.get("posicio", "other")
        if position not in VALID_POSITIONS:
            position = "other"

        controller = event.get("controlador", "desconegut")
        if controller not in VALID_CONTROLLERS:
            controller = "desconegut"

        total_time += duration
        time_by_position_and_controller[(position, controller)] += duration

        if controller in {"oponent_1", "oponent_2"}:
            dominant_time[controller] += duration

            if (
                previous_controller in {"oponent_1", "oponent_2"}
                and previous_controller != controller
            ):
                resum_accions["canvis_control"] += 1

            previous_controller = controller

        tipus_event = event.get("tipus_event")
        action_key = COUNTABLE_ACTIONS.get(tipus_event)
        descripcio = event.get("descripcio", "").lower()

        if not action_key:
            submission_keywords = [
                "estrangul",
                "submiss",
                "finalitz",
                "armbar",
                "clau de braç",
                "triangle",
                "kimura",
                "americana",
                "guillotina",
                "mata-lleó",
                "rear naked",
                "choke",
                "ankle lock",
                "heel hook",
                "leg lock",
                "kneebar",
                "toe hold",
                "omoplata",
            ]

            takedown_keywords = [
                "enderroc",
                "derribo",
                "projecció",
                "proyección",
                "takedown",
                "single",
                "single leg",
                "double",
                "double leg",
                "body lock",
                "foot sweep",
                "snap down",
                "entrada a cama",
                "portar-lo a terra",
                "porta l'oponent a terra",
                "porta a terra",
                "caiguda",
            ]

            guard_pull_keywords = [
                "guard pull",
                "pull guard",
                "guardia volunt",
                "guàrdia volunt",
                "s'asseu a guàrdia",
                "se sienta a guardia",
                "asseure's a guàrdia",
            ]

            if any(word in descripcio for word in submission_keywords):
                action_key = "intents_finalitzacio"
                tipus_event = "intent_finalitzacio"

            elif any(word in descripcio for word in takedown_keywords):
                action_key = "intents_enderroc"
                tipus_event = "intent_enderroc"

            elif any(word in descripcio for word in guard_pull_keywords):
                action_key = "guard_pulls"
                tipus_event = "guard_pull"

            elif (
                "revers" in descripcio
                or "inverteix" in descripcio
                or "sweep" in descripcio
                or "raspada" in descripcio
            ):
                action_key = "reversions"
                tipus_event = "reversio"

            elif (
                "escap" in descripcio
                or "sortida" in descripcio
                or "recupera guàrdia" in descripcio
                or "recupera guardia" in descripcio
            ):
                action_key = "escapades"
                tipus_event = "escape"

        actor = controller

        if actor not in {"oponent_1", "oponent_2"}:
            descripcio_original = event.get("descripcio", "").lower()

            if "oponent_1" in descripcio_original:
                actor = "oponent_1"
            elif "oponent_2" in descripcio_original:
                actor = "oponent_2"

        if action_key and actor in {"oponent_1", "oponent_2"}:
            if action_key in {"intents_finalitzacio", "intents_enderroc"}:
                resum_accions[action_key][actor]["intents"] += 1

                is_successful = _is_successful_action(event, action_key, tipus_event)

                if action_key == "intents_finalitzacio":
                    if is_successful and not finalitzacio_comptada:
                        resum_accions[action_key][actor]["reeixits"] += 1
                        finalitzacio_comptada = True

                elif action_key == "intents_enderroc":
                    if is_successful:
                        resum_accions[action_key][actor]["reeixits"] += 1
            else:
                resum_accions[action_key][actor] += 1

            if tipus_event in {"finalitzacio", "intent_finalitzacio"}:
                accio_tipus = "intent_finalitzacio"
            elif tipus_event == "escape":
                accio_tipus = "escapada"
            else:
                accio_tipus = tipus_event

            accions_clau.append(
                {
                    "temps": event.get("inici", "00:00"),
                    "lluitador": actor,
                    "tipus": accio_tipus,
                    "detall": event.get("descripcio", ""),
                    "confianca": event.get("confianca", "mitjana"),
                }
            )

    temps_per_posicio = []

    for (position, controller), seconds in time_by_position_and_controller.items():
        percentatge = round((seconds / total_time) * 100, 2) if total_time else 0

        temps_per_posicio.append(
            {
                "posicio": position,
                "controlador": controller,
                "segons": seconds,
                "percentatge": percentatge,
            }
        )

    temps_per_posicio.sort(key=lambda item: item["segons"], reverse=True)

    return {
        "duracio_total_segons": total_time,
        "temps_per_posicio": temps_per_posicio,
        "temps_dominant_total": dominant_time,
        "accions_clau": accions_clau,
        "resum_accions": resum_accions,
    }