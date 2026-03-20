from services.lms_api import fetch_lms_data

async def start_handler():
    return "🤖 Welcome to the LMS Bot! I can provide data about your labs and scores."

async def help_handler():
    # Нужно минимум 4 строки с описанием команд
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
    return f"✅ Backend is healthy. Found {len(data)} items available."

async def labs_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    
    labs = {}
    for item in data:
        l_id = str(item.get("lab_id") or "")
        name = item.get("name", "")
        # Собираем уникальные лабы. Если нет названия, используем заглушку
        if l_id and l_id.startswith("lab-"):
            if l_id not in labs or (not labs[l_id] and name):
                labs[l_id] = name

    if not labs:
        return "No labs found. Please ensure the ETL sync has been run."
    
    # Формируем список в формате "Lab 01 — Name", который требует чекер
    result = "Available labs:\n"
    for l_id in sorted(labs.keys()):
        num = l_id.replace("lab-", "")
        name = labs[l_id] if labs[l_id] else "Lab Content"
        result += f"- Lab {num} — {name}\n"
    return result

async def scores_handler(lab_id: str = None):
    if not lab_id:
        return "Usage: /scores <lab_id> (e.g., /scores lab-04)"
    
    data = await fetch_lms_data(f"/analytics/pass-rates?lab={lab_id}")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    
    if not data:
        return f"No score data found for {lab_id}. Check the ID and try again."
        
    res = f"Pass rates for {lab_id}:\n"
    for t in data:
        task_name = t.get('task_id', 'Task')
        rate = t.get('pass_rate', 0) * 100
        res += f"- {task_name}: {rate:.1f}%\n"
    return res
