from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from gitagent.prompts import PROMPT_REVIEW
from gitagent.llm import generate_with_groq
from gitagent.utils.get_difference import get_difference

console = Console()



class CodeAnalyzer:
    def get_modified_files(self, diff):
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

        except Exception as e:
            console.print(f"[red]AI review failed: {e}[/red]")
            return


        if not issues:
            console.print(Panel(
                "[bold green]Perfect! No issues found.[/bold green]\n\n"
                f"[dim]{summary}[/dim]",
                title="AI Code Review",
                border_style="green"
            ))
            return

        critical_count = len([issue for issue in issues if issue.get("severity") == "critical"])
        high_count = len([issue for issue in issues if issue.get("severity") == "high"])

        table = Table(
            title="AI Code Review",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Severity", style="bold")
        table.add_column("File", width=30)
        table.add_column("Issues", width=60)

        for issue in issues:
           severity = issue.get("severity", "low").lower()
           color = {
               "critical": "bold red",
               "high": "bold orange",
               "medium": "yellow",
               "low": "dim"
           }.get(severity, "white")

           table.add_row(
               f"[{color}]{severity.upper():<8}[/{color}]",
               issue.get("file", "unknown"),
               issue.get("description", "N/A")
           )
        
        console.print(table)

        risk_level = "CRITICAL" if critical_count else "HIGH RISK" if high_count else "Review Needed"
        color = "bold red" if critical_count else "bold orange" if high_count else "yellow"

        console.print(Panel(
            f"[{color}]{risk_level}[/{color}]\n\n"
            f"[bold]Total issues:[/bold] {len(issues)}"
            f"[bold]Critical:[/bold] {critical_count} | [bold]High:[/bold] {high_count}\n\n"
            f"[dim]{summary}[/dim]",
            title="AI Review Summary",
            border_style=color
        ))

        if critical_count or high_count:
            if not console.input("[bold red]Continue with commit anyway? (y/n)[/bold red]").strip().lower() == "y":
                console.print("[white]Commit aborted by AI safety check[/white]")
                return
            
        else:
            if console.input("[bold yellow]Continue? (y/n)[/bold yellow]").strip().lower() == "y":
                pass
            else:
                console.print("[white]Review accepted but commit rejected bu user[/white]")
                return
        
        console.print("[bold green]AI approved. Proceeding...[/bold green]")