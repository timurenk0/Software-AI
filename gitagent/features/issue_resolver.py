import subprocess
import os
from rich.console import Console
from github import Github
from pathlib import Path

from gitagent.utils.file_selector import FileSelector
from gitagent.utils.get_file_structure import FileStructure
from gitagent.llm import generate_with_groq
from gitagent.prompts import PROMPT_RESOLVE

console = Console()


class IssueResolver:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            console.print("[red]Error: GITHUB_TOKEN not set in .env[/red]")
            raise ValueError
        
        self.gh = Github(login_or_token=token)
        self.repo = self._get_repo()
        

    
    def _get_repo(self):
        try:
            url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True).strip()

            return self.gh.get_repo(url.split("github.com")[1][1:].replace(".git", "").replace(":", "/"))
        
        except Exception:
            console.print("[red]Failed to detect current Github repository[/red]")
            raise


    def get_issues(self):
        try:
            issues = self.repo.get_issues(state="open")
            if not issues:
                console.print("[green]No open issues at the moment![/green]")
                return
            
            for issue in list(issues):
                console.print(f"#{issue.number}. {issue.title}\nDescription: {issue.body}\n\n")
        
        except Exception:
            raise
    
    def get_issue(self, issue_number):
        console.print(f"[dim]Fetching issue #{issue_number}...[/dim]")

        try:
            issue = self.repo.get_issue(number=issue_number)
            if issue.state != "open":
                console.print("[yellow]The issue you are trying to access is closed[/yellow]")
                return
            
            result = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "labels": [label.name for label in issue.labels]
            }

            print(result)
            return result

        except Exception:
            raise

    def resolve(self, issue_number):
        issue = self.get_issue(issue_number=issue_number)
        files = FileSelector().select_files(issue=issue)
        if not files:
            console.print("[red]AI couldn't select files to fix[/red]")
            return
        
        file_structure = FileStructure()
        console.print("[dim]Generating fix...[/dim]")
        
        file_contents = file_structure.get_contents(files["files"])
        if not file_contents:
            console.print("[red]No valid files to edit[/red]")
            return
        

        context = []
        for path, content in file_contents.items():
            context.append(f"=== {path} ===\n{content}\n")

        
        prompt = PROMPT_RESOLVE.format(
            issue_number=issue["number"],
            title=issue["title"],
            body=issue["body"],
            files_with_content="".join(context)
        )

        try:
            result = generate_with_groq(prompt)
            self._apply_fix(fix=result)
        
        except Exception as e:
            console.print(f"[red]Failed to resolve the issue: {e}[/red]")
            return None
    
    def _apply_fix(self, fix):
        if not fix or "files" not in fix:
            return False

        backups = {}
        for path, new_content in fix["files"].items():
            full_path = Path(path)
            if not full_path.exists():
                console.print(f"[yellow]Creating new file: {path}[/yellow]")
            
            else:
                backups[path] = full_path.read_text()
                console.print(f"[dim]Backing up file: {path}[/dim]")
            
            try:
                full_path.write_text(new_content)
            
            except Exception as e:
                console.print("[red]Failed to write file {path}: {e}[/red]")

                for path, old_content in backups.items():
                    Path(path).write_text(old_content)
                
                return False
        

        console.print(f"[bold green]Applied changes to {len(fix["files"])} files[/bold green]")
        console.print(f"[dim]Explanation: {fix.get("explanation", "No explanation")}[/dim]")
        return True