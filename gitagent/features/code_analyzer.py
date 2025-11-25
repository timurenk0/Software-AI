from pathlib import Path
from rich.console import Console
from gitagent.prompts import PROMPT_REVIEW
from gitagent.llm import generate_with_groq
from gitagent.utils.get_difference import get_difference

console = Console()



class CodeAnalyzer:

    @staticmethod
    def get_modified_files(diff):
        files = {}
        current_file = None 
        lines = diff.splitlines()

        for line in lines:
            if line.startswith("+++ b/"):
                current_file = line[6:].strip()
                files[current_file] = []
            elif line.startswith("+") and current_file and not line.startswith("+++"):
                files[current_file].append(line[1:])
            elif line.startswith(" ") and current_file:
                files[current_file].append(line[1:])

        
        full_content = {}
        for file_path in files.keys():
            path = Path(file_path)
            if path.exists():
                full_content[file_path] = path.read_text()
            else:
                full_content[file_path] = "file not found"
        
        
        return full_content
    

    def review_changes(self):
        diff = get_difference()
        
        files_content = self.get_modified_files(diff)
        if not files_content:
            return { "issues": [], "summary": "No changes detected" }
        
        formatted_files = ""
        for path, content in files_content.items():
            formatted_files += f"\n=== {path} ===\n{content}\n"
        
        prompt = PROMPT_REVIEW.format(
            files_content=formatted_files[:100000],
            diff=diff[:50000]
        )

        try:
            result = generate_with_groq(prompt)
            issues = result.get("issues")
            summary = result.get("summary", "Review completed")

            return { "issues": issues, "summary": summary }
        except Exception as e:
            console.print(f"[red]AI review failed: {e}[/red]")
            return { "issues": [], "summary": "AI review failed" }