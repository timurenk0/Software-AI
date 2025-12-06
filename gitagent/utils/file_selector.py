from rich.console import Console

from gitagent.utils.get_file_structure import FileStructure
from gitagent.llm import generate_with_groq

from gitagent.prompts import PROMPT_FILE_SELECTION


console = Console()

class FileSelector:
    def __init__(self):
        self.files = FileStructure()

    
    def select_files(self, issue):
        paths = self.files.get_paths()
        if not paths:
            return None


        prompt = PROMPT_FILE_SELECTION.format(
            title=issue["title"],
            body=issue["body"] or "Not available",
            labels=", ".join(issue["labels"]) or "Not available",
            files_list="\n".join(f"- {path}" for path in paths)
        )

        try:
            result = generate_with_groq(prompt)
            files = result.get("files", [])
            confidence = result.get("confidence", 0)
            reasoning = result.get("reasoning", "")

            if confidence < 75 or not files:
                console.print("[bold yellow]Low confidence! ({confidence}%). Model's best guess is:\n{reasoning}[/bold yellow]")
                return None

            return {
                "files": files,
                "confidence": confidence,
                "reasoning": reasoning
            }

        except Exception as e:
            console.print("[red]Failed to select files![/red]")
            return None