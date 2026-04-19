from collections import defaultdict

DOMINANT_TOP_POSITIONS = {
    "side_control_top",
    "mount_top",
    "back_control_top",
    "turtle_top",
}

VALID_CONTROLLERS = {"oponent_1", "oponent_2"}


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
    time_by_position = defaultdict(int)
    dominant_time = defaultdict(int)
    control_changes = 0

    previous_controller = None

    for event in timeline:
        start = mmss_to_seconds(event.get("inici", "00:00"))
        end = mmss_to_seconds(event.get("fi", "00:00"))
        duration = max(0, end - start)

        position = event.get("posicio", "other")
        controller = event.get("controlador", "incert")

        if controller in VALID_CONTROLLERS:
            time_by_position[(controller, position)] += duration

            if position in DOMINANT_TOP_POSITIONS:
                dominant_time[controller] += duration

            if previous_controller and controller != previous_controller:
                control_changes += 1

            previous_controller = controller

    structured_positions = [
        {
            "lluitador": fighter,
            "posicio": position,
            "segons": seconds,
            "dominant": position in DOMINANT_TOP_POSITIONS,
        }
        for (fighter, position), seconds in sorted(time_by_position.items())
    ]

    return {
        "temps_per_posicio": structured_positions,
        "temps_dominant_per_lluitador": dict(dominant_time),
        "canvis_control_recalculats": control_changes,
    }