import subprocess
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
from gitagent.llm import generate_with_groq
from gitagent.git_utils import create_and_switch_branch, add_all, commit, push_new_branch
from gitagent.prompts import PROMPT_COMMIT

console = Console()

class CommitGenerator():
    @staticmethod
    def get_difference():
        unstaged = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )

        staged = subprocess.run(
            ["git", "diff", "--staged", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )

        return unstaged.stdout + staged.stdout
    
    @staticmethod
    def has_changes():
        return len(CommitGenerator.get_difference().strip()) > 0
    
    def generate(self):
        if not self.has_changes():
            console.print("[bold yellow]No changes detected. You're up to date.[/bold yellow]")
            return

        console.print(Panel("[gray]Agent is thinking...[/gray]"))
        
        diff = self.get_difference()
        prompt = PROMPT_COMMIT.format(diff=diff)

        try:
            result = generate_with_groq(prompt)
            branch_name = result["branch_name"]
            commit_message = result["commit_message"]
        except Exception as e:
            console.print(f"[red]AI failed: {e}[/red]")
            console.print("[yellow]Falling back to default branch name and commit message...[/yellow]")

            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            branch_name = f"gitagent/auto-{timestamp}"
            commit_message = "chore: auto-commit by gitagent (AI failed)"

        create_and_switch_branch(branch_name)
        add_all()
        commit(commit_message)
        push_new_branch(branch_name)


        console.print(Panel(
            f"[bold green]Done![/bold green]\n\n"
            f"Branch: [bold]{branch_name}[/bold]\n"
            f"Message:\n{commit_message}",
            title="gitagent success",
            expand=False
        ))

        