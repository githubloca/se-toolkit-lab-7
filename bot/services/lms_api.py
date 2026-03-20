import httpx
import config

async def fetch_lms_data(endpoint: str):
    headers = {"Authorization": f"Bearer {config.LMS_API_KEY}"}
    url = f"{config.LMS_API_URL}{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": str(e)}
