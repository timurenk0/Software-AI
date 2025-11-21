import os
import json
import httpx
from rich.console import Console
from pathlib import Path

from .prompt import PROMPT_TEMPLATE


console = Console()

env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()
    console.print(f"[dim]Loaded .env from {env_path}[/dim]")
else:
    console.print(f"[red].env not found at {env_path}[/red]")


def generate_with_groq(diff):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        console.print("[red]Error: GROQ_API_KEY must be set in .env[/red]")
        raise ValueError("Missing GROQ_API_KEY")
    
    response = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "model": "llama-3.1-70b-instant",
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful git assistant"
                },
                {
                    "role": "user",
                    "content": PROMPT_TEMPLATE.format(diff=diff[:120000])
                }
            ]
        },
        timeout=30
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return json.loads(content)
