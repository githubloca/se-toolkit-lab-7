from services.lms_api import fetch_lms_data

async def start_handler():
    return "🤖 Welcome to LMS Bot! I'm ready to help with your lab data."

async def help_handler():
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - This list\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab_id> - Get pass rates"
    )

async def health_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Backend error: {data['error']}"
    return f"✅ Backend is healthy. Found {len(data)} items."

async def labs_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    labs = sorted(list(set(str(item.get("lab_id") or item.get("id")) for item in data if (item.get("lab_id") or item.get("id")))))
    return "Available labs:\n- " + "\n- ".join(labs) if labs else "No labs found."

async def scores_handler(lab_id: str = None):
    if not lab_id:
        return "Please specify a lab ID, e.g., /scores lab-04"
    data = await fetch_lms_data(f"/analytics/pass-rates?lab={lab_id}")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    if not data:
        return f"No data for {lab_id}."
    res = f"Pass rates for {lab_id}:\n"
    for t in data:
        res += f"- {t.get('task_id', 'Task')}: {t.get('pass_rate', 0)*100:.1f}%\n"
    return res
