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
        "intents_finalitzacio": _empty_counter(),
        "intents_enderroc": _empty_counter(),
        "guard_pulls": _empty_counter(),
        "reversions": _empty_counter(),
        "escapades": _empty_counter(),
        "canvis_control": 0,
    }

    accions_clau = []
    total_time = 0
    previous_controller = None

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
            if any(word in descripcio for word in ["estrangul", "submiss", "armbar", "triangle", "kimura", "americana"]):
                action_key = "intents_finalitzacio"
                tipus_event = "intent_finalitzacio"
            elif any(word in descripcio for word in ["enderroc", "projecció", "single", "double", "takedown"]):
                action_key = "intents_enderroc"
                tipus_event = "intent_enderroc"
            elif "guard" in descripcio and "pull" in descripcio:
                action_key = "guard_pulls"
                tipus_event = "guard_pull"
            elif "revers" in descripcio:
                action_key = "reversions"
                tipus_event = "reversio"
            elif "escap" in descripcio or "sortida" in descripcio:
                action_key = "escapades"
                tipus_event = "escape"
        
        if action_key and controller in {"oponent_1", "oponent_2"}:
            resum_accions[action_key][controller] += 1

            accio_tipus = "escapada" if tipus_event == "escape" else tipus_event

            accions_clau.append(
                {
                    "temps": event.get("inici", "00:00"),
                    "lluitador": controller,
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