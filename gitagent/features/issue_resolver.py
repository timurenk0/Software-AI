import os
import subprocess
from pathlib import Path
from github import Github
from github import Auth

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from gitagent.llm import generate_with_groq
from gitagent.prompts import PROMPT_RESOLVE

console = Console()

class IssueResolver:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            console.print("[red]Error: GITHUB_TOKEN not set in .env[/red]")
            raise ValueError("Missing .env variable")
        
        auth = Auth.Token(token)
        self.gh = Github(auth=auth)
        self.repo_name = ""
        self.repo = {}

        try:
            origin = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip()
            self.repo_name = origin.split("github.com")[-1].replace(".git", "").strip("/")
            

        except:
            raise ValueError("Failed to detect project repository. Set a remote url leading to your Github repository first")
        
        print(self.repo_name)
        self.repo = self.gh.get_repo(self.repo_name)


    def get_issues(self):
        try:
            open_issues = list(self.repo.get_issues(state="open"))[:10]

            if not open_issues:
                console.print(Panel(
                    "[bold green]No open issues found![/bold green]\n\n"
                    "You're all caught up — excellent work!",
                    title="GitHub Issues",
                    border_style="green",
                    padding=(1, 2)
                ))
                return
            
                
            table = Table(
                title=f"[bold magenta]Open Issues — {self.repo.full_name or self.repo_name}[/bold magenta]",
                show_header=True,
                header_style="bold cyan",
                box=box.ROUNDED,
                border_style="bright_blue",
                title_style="bold white on #1e1e2e",
                padding=(0, 1)
            )

            table.add_column("#", style="dim", width=4)
            table.add_column("Title", style="bold white", width=50)
            table.add_column("Description", style="white")
            table.add_column("Opened by", style="dim")

            for issue in open_issues:
                title = issue.title.strip()
                body = (issue.body or "No description").strip().replace("\n", " ").replace("\r", " ")
                
                # Truncate long descriptions
                if len(body) > 120:
                    body = body[:117] + "..."

                table.add_row(
                    f"[cyan]#{issue.number}[/cyan]",
                    title,
                    f"{body}",
                    f"{issue.user.login}"
                )

            console.print(table)

            if len(open_issues) >= 10:
                console.print(f"[dim]Showing first 10 issues • Use GitHub for full list[/dim]")   
            
        
        except Exception as e:
            console.print(Panel(
                f"[red]Failed to load issues[/red]\n\n"
                f"Error: ${e}\n",
                title="API Error",
                border_style="red"
            ))

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
            f"[bold green]Fix applied successfully![/bold green]"
        ))