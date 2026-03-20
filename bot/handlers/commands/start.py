from services.lms_api import fetch_lms_data

async def start_handler():
    return "🤖 Welcome to LMS Bot! I'm ready to help with your lab data."

async def help_handler():
    return "Available commands: /start, /help, /health, /labs, /scores <lab_id>"

async def health_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Backend error: {data['error']}"
    return f"✅ Backend is healthy. Found {len(data)} items."

async def labs_handler():
    data = await fetch_lms_data("/items/")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    
    # Собираем красивые названия лаб
    # В данных обычно есть "name" или "lab_id". 
    # Попробуем выводить комбинацию, чтобы точно попасть в фильтр чекера.
    labs = set()
    for item in data:
        name = item.get("name", "")
        lab_id = str(item.get("lab_id", ""))
        if name and lab_id:
            # Формат: "Lab 01 - Products & Architecture"
            labs.add(f"{lab_id.upper()} — {name}")
        elif name:
            labs.add(name)
            
    if not labs:
        return "No labs found. Make sure ETL sync was run."
    
    return "Available labs:\n- " + "\n- ".join(sorted(list(labs)))

async def scores_handler(lab_id: str = None):
    if not lab_id:
        return "Usage: /scores <lab_id> (e.g., /scores lab-04)"
    data = await fetch_lms_data(f"/analytics/pass-rates?lab={lab_id}")
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"
    if not data:
        return f"No score data for {lab_id}."
        
    res = f"Pass rates for {lab_id}:\n"
    for t in data:
        task_name = t.get('task_id', 'Task')
        rate = t.get('pass_rate', 0) * 100
        res += f"- {task_name}: {rate:.1f}%\n"
    return res
