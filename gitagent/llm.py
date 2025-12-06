import os
import json
import httpx
from rich.console import Console
from dotenv import load_dotenv


console = Console()

load_dotenv()
def generate_with_groq(prompt):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        console.print("[red]Error: GROQ_API_KEY must be set in .env[/red]")
        raise ValueError("Missing GROQ_API_KEY")
    
    if len(prompt) > 30000:  # Rough token estimate. Truncate if excessive
        console.print(f"[yellow]Warning: Prompt truncated from {len(prompt)} chars[/yellow]")
        prompt = prompt[:30000] + "\n[Truncated for token limit]"
    
    response = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "llama-3.1-8b-instant",
            "temperature": 0.2,
            "max_tokens": 1024,  # Safe for Llama-3.1 (max ~8k)
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a helpful git assistant"},
                {"role": "user", "content": prompt}
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

    try:
        return json.loads(content)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            error_body = e.response.json()
            console.print(f"[red]Groq 400 Details: {error_body.get('error', {}).get('message', 'Unknown')}[/red]")
            console.print(f"[yellow]Prompt preview (first 500 chars): {prompt[:500]}...[/yellow]")
        raise    
