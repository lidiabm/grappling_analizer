from collections import defaultdict

VALID_CONTROLLERS = {"oponent_1", "oponent_2"}

DOMINANT_POSITIONS = {
    "side_control",
    "mount",
    "back_control",
    "turtle",
}

POSITION_MAP = {
    "closed_guard_top": "closed_guard",
    "closed_guard_bottom": "closed_guard",
    "open_guard_top": "open_guard",
    "open_guard_bottom": "open_guard",
    "half_guard_top": "half_guard",
    "half_guard_bottom": "half_guard",
    "side_control_top": "side_control",
    "side_control_bottom": "side_control",
    "mount_top": "mount",
    "mount_bottom": "mount",
    "back_control_top": "back_control",
    "back_control_bottom": "back_control",
    "turtle_top": "turtle",
    "turtle_bottom": "turtle",
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


def normalize_position(position: str) -> str:
    return POSITION_MAP.get(position, position)


def derive_stats_from_timeline(timeline: list[dict]) -> dict:
    time_by_position = defaultdict(int)

    dominant_time = {
        "oponent_1": 0,
        "oponent_2": 0,
    }

    defensive_time = {
        "oponent_1": 0,
        "oponent_2": 0,
    }

    neutral_time = 0
    control_changes = 0
    previous_controller = None

    for event in timeline:
        start = mmss_to_seconds(event.get("inici", "00:00"))
        end = mmss_to_seconds(event.get("fi", "00:00"))
        duration = max(0, end - start)

        if duration <= 0:
            continue

        raw_position = event.get("posicio", "other")
        position = normalize_position(raw_position)
        controller = event.get("controlador", "incert")

        time_by_position[position] += duration

        if controller in VALID_CONTROLLERS and position in DOMINANT_POSITIONS:
            dominant_time[controller] += duration

            defender = "oponent_2" if controller == "oponent_1" else "oponent_1"
            defensive_time[defender] += duration

            if previous_controller and controller != previous_controller:
                control_changes += 1

            previous_controller = controller
        else:
            neutral_time += duration

    total_time = sum(time_by_position.values())

    structured_positions = [
        {
            "posicio": position,
            "segons": seconds,
            "percentatge": round((seconds / total_time) * 100) if total_time else 0,
            "dominant": False,
        }
        for position, seconds in sorted(time_by_position.items())
    ]

    return {
        "temps_per_posicio": structured_positions,
        "temps_dominant_total": dominant_time,
        "temps_defensiu_total": defensive_time,
        "temps_neutral_total": neutral_time,
        "canvis_control": control_changes,
    }