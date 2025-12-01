import os
import subprocess
from pathlib import Path
from github import Github

from rich.console import Console
from rich.panel import Panel

from gitagent.llm import generate_with_groq
from gitagent.prompts import PROMPT_RESOLVE

console = Console()

class IssueResolver:
    pass