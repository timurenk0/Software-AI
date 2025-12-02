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
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            console.print("[red]Error: GITHUB_TOKEN not set in .env[/red]")
            raise ValueError("Missing .env variable")
        
        self.gh = Github(token)

        try:
            origin = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip()
            repo_name = origin.split("github.com")[-1].replace(".git", "").strip(":")
            if repo_name.endswith("/"):
                repo_name = repo_name[:-1]
        
        except:
            raise ValueError("Failed to detect project repository. Set a remote url leading to your Github repository first")
        
        self.repo = self.gh.get_repo(repo_name)
    

    def resolve_issue(self, issue_number):
        issue = self.repo.get_issue(number=issue_number)
        if issue.state != "open":
            console.print(f"[yellow]Issue #{issue_number} is {issue.state}. Skipping...[/yellow]")
            return
        
        console.print(Panel(
            f"[bold blue]#{issue.number}: {issue.title}[/bold blue]\n\n"
            f"{issue.body or "No description."}",
            title="Resolving Github Issue",
            border_style="blue"
        ))

        with console.status("[bold magenta]AI is generating a fix...[/bold magenta]"):
            prompt = PROMPT_RESOLVE.format(
                issue_title = issue.title,
                issue_body = issue.body or "No description provided.",
                issue_labels = ", ".join(label.name for label in issue.labels),
                issue_number = issue.number
            )

            try:
                result = generate_with_groq(prompt)
            
            except Exception as e:
                console.print(f"[red]AI failed: {e}[/red]")
                return
            

        changes = result.get("changes", {})
        if not changes:
            console.print("[yellow]AI didn't generate any necessary code fixes (possible already fixed or non-code issues)[/yellow]")
            return
        
        applied = 0
        for file_path, new_content in changes.items():
            path = Path(file_path)
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            backup_path = path.with_suffix(path.suffix + ".gitagent-backup")
            if path.exists():
                backup_path.write_text(path.read_text())
            
            path.write_text(new_content)
            console.print(f"[green]Applied fixes to {file_path}[/green]")
            applied+=1
        
        console.print(Panel(
            f"[bold green]Fix applied successfully!"
        ))