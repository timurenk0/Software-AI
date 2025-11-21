import subprocess
from rich.console import Console


console = Console()

def run_git(cmd, **kwargs):
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        **kwargs
        )
    
    if result.returncode != 0:
        console.print(f"[red]Git error: {result.stderr.strip()}[/red]")
        raise RuntimeError(f"Git command failed: {" ".join(cmd)}")

    return result.stdout


def create_and_switch_branch(branch_name):
    console.print(f"[bold green]Creating and switching to branch:[/bold green] {branch_name}")
    run_git(["checkout", "-b", branch_name])


def add_all():
    console.print("[yellow]Adding all changes...[/yellow]")
    run_git(["add", "."])


def commit(message):
    console.print(f"[bold blue]Commiting changes...[/bold blue]\n{message}")
    run_git(["commit", "-m", message])


def push_new_branch(branch_name):
    console.print(f"[bold magent]Pushing branch {branch_name} and setting upstream...[/bold magenta]")
    run_git(["push", "--set-upstream", "origin", branch_name])