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
from gitagent.prompts import PROMPT_RESOLVE, PROMPT_RESOLVE_HELPER

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

    
    def _get_project_context(self, issue):
        with console.status("[dim]AI is analyzing the issue to find relevant files[/dim]"):
            try:
                response = generate_with_groq(PROMPT_RESOLVE_HELPER.format(
                    issue_number = issue.number,
                    issue_title = issue.title,
                    issue_body = issue.body or "No description provided."
                ))
                selected_files = [line.strip() for line in response.strip().split("\n") if line.strip() and "test" not in line.strip().lower()][:6]
            
            except Exception as e:
                console.print(f"[red]File selection failed: {e}[/red]")
                return
            
        
        console.print(f"[dim]AI selected {len(selected_files)} files to analzye[/dim]")

        parts = ["Relevant files selcted bu AI:\n" + "\n".join(selected_files)]
        for file_path in selected_files:
            try:
                path = Path(file_path)
                if not path.exists():
                    parts.append(f"\n=== {file_path} ===\n<file not found>")
                    continue

                content = path.read_text()
                if len(content) > 12000:
                    content = content[:12000] + "\n\n (truncated)"
                
                parts.append(f"\n=== {file_path} ===\n{content}\n")

            except:
                parts.append(f"\n=== {file_path} ===\n<Failed to read the file>")
        
        context = "\n".join(parts)
        return context
    

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
        try:
            issue = self.repo.get_issue(number=issue_number)
        except Exception as e:
            console.print(f"[red]Could not fetch issue #{issue_number}: {e}[/red]")
            return

        if issue.state != "open":
            console.print(f"[yellow]Issue #{issue_number} is {issue.state}. Skipping...[/yellow]")
            return

        console.print(Panel(
            f"[bold blue]#{issue.number}: {issue.title}[/bold blue]\n\n{issue.body or 'No description'}",
            title="Resolving GitHub Issue",
            border_style="blue"
        ))

        # STEP 1: AI selects relevant files
        with console.status("[bold yellow]AI is selecting relevant files...[/bold yellow]"):
            selected_files = self._select_relevant_files(issue)  # ← Fixed: no 'self='

        if not selected_files:
            console.print("[yellow]No relevant files identified[/yellow]")
            return

        console.print(f"[dim]AI selected: {', '.join(selected_files)}[/dim]")

        # STEP 2: Load only those files
        project_context = self._load_selected_files(selected_files)

        # STEP 3: Generate fix
        with console.status("[bold magenta]AI is generating fix...[/bold magenta]"):
            prompt = PROMPT_RESOLVE.format(
                issue_number=issue.number,
                issue_title=issue.title,
                issue_body=issue.body or "No description",
                issue_labels=issue.labels,
                project_context=project_context
            )
            try:
                result = generate_with_groq(prompt)
                changes = result.get("changes", {})
            except Exception as e:
                console.print(f"[red]AI failed: {e}[/red]")
                return

        if not changes:
            console.print("[yellow]No code changes needed[/yellow]")
            return

        # Apply fixes
        for file_path, new_content in changes.items():
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                backup = path.with_suffix(path.suffix + ".gitagent-backup")
                backup.write_text(path.read_text())
            path.write_text(new_content)
            console.print(f"[green]Fixed → {file_path}[/green]")

        console.print(Panel(
            f"[bold green]Issue #{issue.number} resolved![/bold green]\n\n"
            f"Fixed {len(changes)} file(s)\n"
            f"Next: [bold cyan]gitagent commit[/bold cyan]",
            title="Success",
            border_style="green"
        ))

    def _select_relevant_files(self, issue):
        file_list = self._list_python_files()
        prompt = f"""
    You are an expert Python developer.

    Issue #{issue.number}: {issue.title}
    Description: {issue.body or "No description"}

    Available Python files:
    {file_list}

    Return only the file paths (one per line) most likely involved.
    Max 6. Be precise.

    Respond with file paths only:
    """
        try:
            response = generate_with_groq(prompt)
            lines = [l.strip() for l in response.strip().split("\n") if l.strip()]
            valid = [f for f in lines if f in file_list.split("\n")]
            return valid[:6] or ["best_feature.py"]
        except Exception as e:
            console.print(f"[red]File selection failed: {e}[/red]")
            return ["best_feature.py"]

    def _list_python_files(self) -> str:
        try:
            files = subprocess.check_output(["git", "ls-files", "*.py"], text=True).splitlines()
            filtered = [f for f in files if not f.startswith("test/") and "__pycache__" not in f]
            return "\n".join(sorted(filtered)) or "best_feature.py"
        except:
            return "best_feature.py"

    def _load_selected_files(self, files):
        parts = ["Relevant files:"]
        for f in files:
            try:
                content = Path(f).read_text(encoding="utf-8", errors="ignore")
                if len(content) > 12000:
                    content = content[:12000] + "\n\n... (truncated)"
                parts.append(f"\n=== {f} ===\n{content}\n")
            except:
                parts.append(f"\n=== {f} ===\n<file not readable>\n")
        return "\n".join(parts)
