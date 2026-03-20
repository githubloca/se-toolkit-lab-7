from services.lms_api import fetch_lms_data

async def start_handler():
    return "🤖 Welcome to LMS Bot! Use /help to see what I can do."

async def help_handler():
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - This list\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab_id> - Get pass rates (e.g., /scores lab-04)"
    )

async def health_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Backend error: {data['error']}"
    return f"✅ Backend is healthy. Found {len(data)} items."

async def labs_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Error fetching labs: {data['error']}"
    
    labs = set()
    for item in data:
        # Извлекаем ID и приводим к строке сразу
        l_id = item.get("lab_id") or item.get("id")
        if l_id:
            labs.add(str(l_id))
            
    if not labs:
        return "No labs found in the system."
    
    # Сортируем строковые ID и собираем список
    sorted_labs = sorted(list(labs))
    return "Available labs:\n- " + "\n- ".join(sorted_labs)

async def scores_handler(lab_id: str = None):
    if not lab_id:
        return "Please specify a lab ID, e.g., /scores lab-04"
    
    data = await fetch_lms_data(f"/analytics/pass-rates?lab={lab_id}")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    
    if not data:
        return f"No score data found for {lab_id}."

    result = f"Pass rates for {lab_id}:\n"
    for task in data:
        name = task.get("task_id") or "Unknown"
        rate = task.get("pass_rate", 0) * 100
        result += f"- {name}: {rate:.1f}%\n"
    return result
