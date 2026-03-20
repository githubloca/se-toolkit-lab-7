import json
import sys
import httpx
import config
from services.lms_api import fetch_lms_data, post_lms_data


SYSTEM_PROMPT = """
You are an LMS analytics Telegram bot.
Your job is to answer user questions by calling backend tools when needed.

Rules:
- For plain-text questions about labs, students, scores, groups, rankings, completion, timelines, or sync, prefer using tools.
- You may call multiple tools if needed.
- When the user asks an ambiguous question like "lab 4", ask a brief clarifying question.
- When the user greets you, answer warmly and mention what you can do.
- When the user sends gibberish or unclear text, reply helpfully with examples of what you can answer.
- Be concise but include real numbers and names from tool results.
- Never invent backend data.
- If a tool returns an error, explain it briefly and clearly.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List LMS items including labs and tasks.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get enrolled learners and their groups.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution buckets for a lab, for example lab-04.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempts for a lab, for example lab-04.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group performance and student counts for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. lab-03"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top learners overall or for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Optional lab identifier, e.g. lab-04"},
                    "limit": {"type": "integer", "description": "Number of learners to return", "default": 5}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate percentage for a lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {"type": "string", "description": "Lab identifier, e.g. lab-04"}
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL sync from autochecker into the analytics backend.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


async def _call_backend_tool(name: str, args: dict):
    if name == "get_items":
        return await fetch_lms_data("/items/")
    if name == "get_learners":
        return await fetch_lms_data("/learners/")
    if name == "get_scores":
        return await fetch_lms_data(f"/analytics/scores?lab={args['lab']}")
    if name == "get_pass_rates":
        return await fetch_lms_data(f"/analytics/pass-rates?lab={args['lab']}")
    if name == "get_timeline":
        return await fetch_lms_data(f"/analytics/timeline?lab={args['lab']}")
    if name == "get_groups":
        return await fetch_lms_data(f"/analytics/groups?lab={args['lab']}")
    if name == "get_top_learners":
        lab = args.get("lab")
        limit = args.get("limit", 5)
        endpoint = f"/analytics/top-learners?limit={limit}"
        if lab:
            endpoint += f"&lab={lab}"
        return await fetch_lms_data(endpoint)
    if name == "get_completion_rate":
        return await fetch_lms_data(f"/analytics/completion-rate?lab={args['lab']}")
    if name == "trigger_sync":
        return await post_lms_data("/pipeline/sync", {})
    return {"error": f"Unknown tool: {name}"}


def _short_result_summary(result):
    if isinstance(result, list):
        return f"{len(result)} items"
    if isinstance(result, dict):
        if "error" in result:
            return f"error: {result['error']}"
        keys = ", ".join(list(result.keys())[:5])
        return f"dict with keys: {keys}"
    return str(type(result).__name__)


async def _llm_chat(messages):
    headers = {
        "Authorization": f"Bearer {config.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.LLM_API_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": "auto",
    }
    url = f"{config.LLM_API_BASE_URL.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]


async def route(user_text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]

    tool_results_count = 0

    for _ in range(8):
        try:
            assistant_message = await _llm_chat(messages)
        except Exception as e:
            return f"LLM error: {e}"

        tool_calls = assistant_message.get("tool_calls") or []

        if not tool_calls:
            content = assistant_message.get("content")
            return content or "I couldn't produce a response."

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.get("content") or "",
                "tool_calls": tool_calls,
            }
        )

        for call in tool_calls:
            tool_name = call["function"]["name"]
            raw_args = call["function"].get("arguments") or "{}"
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {}

            print(f"[tool] LLM called: {tool_name}({json.dumps(args, ensure_ascii=False)})", file=sys.stderr)

            result = await _call_backend_tool(tool_name, args)

            print(f"[tool] Result: {_short_result_summary(result)}", file=sys.stderr)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )
            tool_results_count += 1

        print(f"[summary] Feeding {tool_results_count} tool result back to LLM", file=sys.stderr)

    return "I couldn't finish the request after several tool calls."
