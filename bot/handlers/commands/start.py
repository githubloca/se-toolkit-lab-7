from services.lms_api import fetch_lms_data


def _pick(d, *keys, default=None):
    for key in keys:
        value = d.get(key)
        if value is not None and value != "":
            return value
    return default


async def start_handler():
    return "🤖 Welcome to the LMS Bot! I can provide data about your labs and scores."


async def help_handler():
    return (
        "Available commands:\n"
        "/start - Start the bot and get a welcome message\n"
        "/help - Show this list of available commands\n"
        "/health - Check the status of the LMS backend\n"
        "/labs - List all available laboratory works\n"
        "/scores <lab_id> - Show pass rates for a specific lab"
    )


async def health_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Backend error: {data['error']}"
    if isinstance(data, list):
        return f"✅ Backend is healthy. Found {len(data)} items available."
    return "✅ Backend is healthy."


async def labs_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Backend error: {data['error']}"

    if not isinstance(data, list):
        return "Unexpected backend response for /items/."

    labs = {}

    for item in data:
        item_type = str(_pick(item, "type", "item_type", "kind", default="")).lower()
        item_id = str(_pick(item, "id", "lab_id", "slug", default=""))
        title = _pick(item, "title", "lab_name", "name", "label")

        # Берем либо явные lab-XX записи, либо items типа lab
        if item_type == "lab" or item_id.startswith("lab-"):
            if item_id and title:
                labs[item_id] = title

        # Иногда lab info лежит внутри task item
        parent_lab_id = _pick(item, "lab_id", "lab", "lab_slug")
        parent_lab_name = _pick(item, "lab_name", "lab_title")
        if parent_lab_id and parent_lab_name:
            labs[str(parent_lab_id)] = str(parent_lab_name)

    if not labs:
        return "No labs found from backend data."

    lines = ["Available labs:"]
    for lab_id, title in sorted(labs.items()):
        lines.append(f"- {lab_id}: {title}")

    return "\n".join(lines)


async def scores_handler(lab_id=None):
    if not lab_id:
        return "Usage: /scores <lab_id>"

    requested_lab = str(lab_id).strip()
    data = await fetch_lms_data(f"/analytics/pass-rates?lab={requested_lab}")

    if isinstance(data, dict) and "error" in data:
        return f"Backend error: {data['error']}"

    rows = data
    if isinstance(data, dict):
        rows = (
            data.get("items")
            or data.get("results")
            or data.get("data")
            or data.get("pass_rates")
            or data.get("tasks")
            or []
        )

    if not isinstance(rows, list) or not rows:
        return f"No score data found for {lab_id}. Check the ID and try again."

    lines = [f"Pass rates for {lab_id}:"]

    for item in rows:
        task_name = (
            item.get("task_name")
            or item.get("name")
            or item.get("task")
            or item.get("title")
            or item.get("label")
            or "Unknown task"
        )

        rate = (
            item.get("pass_rate")
            if item.get("pass_rate") is not None
            else item.get("percentage")
        )
        if rate is None:
            rate = item.get("avg_pass_rate")
        if rate is None:
            rate = item.get("percent")
        if rate is None:
            rate = item.get("avg_score")

        attempts = (
            item.get("attempts")
            if item.get("attempts") is not None
            else item.get("submissions")
        )
        if attempts is None:
            attempts = item.get("count")

        if rate is None:
            continue

        try:
            rate_value = float(rate)
        except Exception:
            continue

        if attempts is not None:
            lines.append(f"- {task_name}: {rate_value:.1f}% ({attempts} attempts)")
        else:
            lines.append(f"- {task_name}: {rate_value:.1f}%")

    if len(lines) == 1:
        return f"No score data found for {lab_id}. Check the ID and try again."

    return "\n".join(lines)
