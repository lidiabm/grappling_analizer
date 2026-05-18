from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any


CHART_WEEKS = 10
FOCUS_WEEKS = 3


def normalize_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        cleaned = value.replace(",", ".")
        cleaned = "".join(ch for ch in cleaned if ch.isdigit() or ch in ".-")

        try:
            return float(cleaned)
        except ValueError:
            return 0

    return 0


def round1(value: float) -> float:
    return round(value, 1)


def pct(value: float, total: float) -> float:
    if total <= 0:
        return 0

    return round1((value / total) * 100)


def get_analysis_data(analysis: dict) -> dict:
    return analysis.get("result") or analysis.get("data") or analysis


def get_student_id(analysis: dict) -> str:
    data = get_analysis_data(analysis)
    return data.get("selected_oponent_id") or "oponent_1"


def get_by_fighter_or_global(value: Any, fighter: str) -> float:
    if isinstance(value, dict):
        return normalize_number(value.get(fighter))

    if fighter == "oponent_1":
        return normalize_number(value)

    return 0


def parse_date(value: Any) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)

    try:
        cleaned = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(cleaned)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return parsed
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def get_analysis_fight_date(analysis: dict) -> datetime:
    return parse_date(analysis.get("fightDate"))


def get_analysis_label(analysis: dict, index: int) -> str:
    fight_date = analysis.get("fightDate") or ""

    if fight_date:
        date = str(fight_date)[:10]
        title = analysis.get("title") or f"Combat #{index + 1}"
        return f"{date} · {title}"

    return f"Anàlisi {index + 1}"


def filter_recent_weeks(analyses: list[dict], weeks: int) -> list[dict]:
    valid_dates = [
        get_analysis_fight_date(analysis)
        for analysis in analyses
        if get_analysis_fight_date(analysis)
        != datetime.min.replace(tzinfo=timezone.utc)
    ]

    if not valid_dates:
        return []

    latest_date = max(valid_dates)
    cutoff_date = latest_date - timedelta(weeks=weeks)

    return [
        analysis
        for analysis in analyses
        if get_analysis_fight_date(analysis) >= cutoff_date
    ]


def build_metrics(analyses: list[dict]) -> list[dict]:
    metrics = []

    for index, analysis in enumerate(analyses):
        data = get_analysis_data(analysis)
        stats = data.get("estadistiques_estimades") or {}
        student_id = get_student_id(analysis)

        dominant_time = get_by_fighter_or_global(
            stats.get("temps_dominant_total"),
            student_id,
        )

        defensive_time = get_by_fighter_or_global(
            stats.get("temps_defensiu_total"),
            student_id,
        )

        neutral_time = normalize_number(stats.get("temps_neutral_total"))
        total_fight_time = dominant_time + defensive_time + neutral_time

        metrics.append({
            "fightId": analysis.get("fightId") or analysis.get("id") or str(index),
            "label": get_analysis_label(analysis, index),
            "date": analysis.get("fightDate"),
            "dominantTime": round1(dominant_time),
            "defensiveTime": round1(defensive_time),
            "neutralTime": round1(neutral_time),
            "totalFightTime": round1(total_fight_time),
            "dominantPct": pct(dominant_time, total_fight_time),
            "defensivePct": pct(defensive_time, total_fight_time),
            "neutralPct": pct(neutral_time, total_fight_time),
            "submissionAttempts": round1(get_by_fighter_or_global(
                stats.get("intents_finalitzacio"),
                student_id,
            )),
            "takedownAttempts": round1(get_by_fighter_or_global(
                stats.get("intents_enderroc"),
                student_id,
            )),
            "guardPulls": round1(get_by_fighter_or_global(
                stats.get("guard_pulls"),
                student_id,
            )),
            "reversals": round1(get_by_fighter_or_global(
                stats.get("reversions"),
                student_id,
            )),
            "escapes": round1(get_by_fighter_or_global(
                stats.get("escapades"),
                student_id,
            )),
        })

    return metrics


def avg(metrics: list[dict], key: str) -> float:
    if not metrics:
        return 0

    return round1(sum(float(item.get(key) or 0) for item in metrics) / len(metrics))


def total(metrics: list[dict], key: str) -> float:
    return round1(sum(float(item.get(key) or 0) for item in metrics))


def diff(metrics: list[dict], key: str) -> float:
    if len(metrics) < 2:
        return 0

    first = float(metrics[0].get(key) or 0)
    last = float(metrics[-1].get(key) or 0)

    return round1(last - first)


def latest(metrics: list[dict], key: str) -> float:
    if not metrics:
        return 0

    return float(metrics[-1].get(key) or 0)


def build_position_totals(
    analyses: list[dict],
    only_selected_student: bool = False,
) -> list[dict]:
    totals: dict[str, float] = defaultdict(float)

    for analysis in analyses:
        data = get_analysis_data(analysis)
        student_id = get_student_id(analysis)

        positions = (
            data.get("estadistiques_estimades", {})
            .get("temps_per_posicio", [])
        )

        for item in positions:
            if (
                only_selected_student
                and item.get("lluitador")
                and item.get("lluitador") != student_id
            ):
                continue

            position = item.get("posicio") or "other"
            totals[position] += normalize_number(item.get("segons"))

    return sorted(
        [
            {"name": name, "segons": round1(seconds)}
            for name, seconds in totals.items()
            if seconds > 0
        ],
        key=lambda item: item["segons"],
        reverse=True,
    )


def get_iso_week_key(analysis: dict) -> str:
    date = get_analysis_fight_date(analysis)

    if date == datetime.min.replace(tzinfo=timezone.utc):
        return "Sense setmana"

    year, week, _ = date.isocalendar()
    return f"{year} · Setmana {str(week).zfill(2)}"


def build_global_metrics_by_week(analyses: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)

    for analysis in analyses:
        grouped[get_iso_week_key(analysis)].append(analysis)

    result = []

    for week in sorted(grouped.keys()):
        metrics = build_metrics(grouped[week])

        dominant_time = avg(metrics, "dominantTime")
        defensive_time = avg(metrics, "defensiveTime")
        neutral_time = avg(metrics, "neutralTime")
        total_fight_time = dominant_time + defensive_time + neutral_time

        result.append({
            "fightId": week,
            "label": week,
            "dominantTime": dominant_time,
            "defensiveTime": defensive_time,
            "neutralTime": neutral_time,
            "totalFightTime": round1(total_fight_time),
            "dominantPct": pct(dominant_time, total_fight_time),
            "defensivePct": pct(defensive_time, total_fight_time),
            "neutralPct": pct(neutral_time, total_fight_time),
            "submissionAttempts": total(metrics, "submissionAttempts"),
            "takedownAttempts": total(metrics, "takedownAttempts"),
            "guardPulls": total(metrics, "guardPulls"),
            "reversals": total(metrics, "reversals"),
            "escapes": total(metrics, "escapes"),
        })

    return result


def get_evolution_text(metrics: list[dict]) -> str:
    if len(metrics) < 2:
        return "Encara no hi ha prou dades."

    dominant_diff = diff(metrics, "dominantTime")
    defensive_diff = diff(metrics, "defensiveTime")
    submission_diff = diff(metrics, "submissionAttempts")
    escape_diff = diff(metrics, "escapes")

    messages = []

    if dominant_diff > 0:
        messages.append(f"més domini (+{dominant_diff}s)")

    if defensive_diff < 0:
        messages.append(f"menys defensa ({defensive_diff}s)")

    if submission_diff > 0:
        messages.append(f"més finalitzacions (+{submission_diff})")

    if escape_diff > 0:
        messages.append(f"millors escapades (+{escape_diff})")

    return " · ".join(messages) if messages else "Evolució estable."


def get_main_focus(metrics: list[dict]) -> str:
    recent_metrics = metrics[-3:] if len(metrics) > 3 else metrics

    last_dominant = latest(recent_metrics, "dominantTime")
    last_defensive = latest(recent_metrics, "defensiveTime")
    last_submission = latest(recent_metrics, "submissionAttempts")
    last_escapes = latest(recent_metrics, "escapes")

    if last_defensive > last_dominant:
        return "Treballar defensa i escapades"

    if last_defensive > 0 and last_escapes < 1:
        return "Treballar sortides de posicions inferiors"

    if last_submission < 1:
        return "Treballar atac i finalitzacions"

    return "Consolidar domini"


def get_global_focus(metrics: list[dict]) -> list[str]:
    defensive_avg = avg(metrics, "defensiveTime")
    dominant_avg = avg(metrics, "dominantTime")

    submission_total = total(metrics, "submissionAttempts")
    takedown_total = total(metrics, "takedownAttempts")
    escapes_total = total(metrics, "escapes")
    reversals_total = total(metrics, "reversals")

    defensive_trend = diff(metrics, "defensiveTime")

    focuses = []

    if defensive_avg > dominant_avg or defensive_trend > 0:
        focuses.append(
            "Reduir temps defensiu: frames, retenció de guàrdia i escapades"
        )

    if escapes_total < len(metrics) and defensive_avg > 0:
        focuses.append(
            "Millorar sortides de posicions inferiors abans de concedir control"
        )

    if dominant_avg > defensive_avg and submission_total < len(metrics):
        focuses.append(
            "Convertir posicions dominants en amenaces de finalització"
        )

    if takedown_total < len(metrics):
        focuses.append(
            "Treballar entrades, desequilibris i continuïtat fins a l’enderroc"
        )

    if reversals_total < len(metrics) and defensive_avg > 0:
        focuses.append(
            "Afegir reversions des de defensa per recuperar la iniciativa"
        )

    if not focuses:
        return ["Consolidar pressió, control i continuïtat ofensiva"]

    return focuses[:3]


def group_by_student(analyses: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)

    for analysis in analyses:
        student_name = (analysis.get("studentFolder") or "").strip() or "Sense alumne"
        grouped[student_name].append(analysis)

    students = []

    for student_name, items in grouped.items():
        sorted_asc = sorted(
            items,
            key=lambda item: get_analysis_fight_date(item),
        )

        metrics = build_metrics(sorted_asc)

        students.append({
            "studentName": student_name,
            "analysesCount": len(metrics),
            "metrics": metrics,
            "positionTotals": build_position_totals(sorted_asc, True),
            "summary": {
                "dominantChange": diff(metrics, "dominantTime"),
                "defensiveChange": diff(metrics, "defensiveTime"),
                "submissionChange": diff(metrics, "submissionAttempts"),
                "evolutionText": get_evolution_text(metrics),
                "mainFocus": get_main_focus(metrics),
            },
        })

    return sorted(students, key=lambda item: item["studentName"])


def build_training_focus_response(
    all_analyses: list[dict],
    chart_weeks: int = CHART_WEEKS,
    focus_weeks: int = FOCUS_WEEKS,
) -> dict:
    analyses = [
        analysis
        for analysis in all_analyses
        if analysis.get("profileType") == "entrenador"
        and (analysis.get("studentFolder") or "").strip()
        and get_analysis_fight_date(analysis) != datetime.min.replace(tzinfo=timezone.utc)
    ]

    chart_analyses = filter_recent_weeks(analyses, chart_weeks)
    focus_analyses = filter_recent_weeks(analyses, focus_weeks)

    students = group_by_student(chart_analyses)

    global_metrics = build_global_metrics_by_week(chart_analyses)
    focus_metrics = build_global_metrics_by_week(focus_analyses)

    return {
        "studentsCount": len(students),
        "analysesCount": len(analyses),
        "recentCount": len(focus_analyses),
        "chartWeeks": chart_weeks,
        "focusWeeks": focus_weeks,
        "globalMetrics": global_metrics,
        "globalPositionTotals": build_position_totals(chart_analyses, False),
        "globalFocus": get_global_focus(focus_metrics),
        "students": students,
    }