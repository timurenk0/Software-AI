import os
import json
import httpx
from rich.console import Console
from pathlib import Path


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


def generate_with_groq(prompt):
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
            "model": "llama-3.1-8b-instant",
            "temperature": 0.2,
            "max_tokens": 1024,
            "response_format": {
                "type": "json_object"
            },
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful git assistant"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        },
        timeout=30
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    start = content.find("{")
    end = content.rfind("}") + 1
    if start == -1 or end == 0:
        console.print(f"[red]No JSON found in response:[/red]\n{content}")
        raise ValueError("No JSON in response")

    json_str = content[start:end]

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        console.print(f"[yellow]Raw response:[/yellow]\n{json_str}")
        raise    