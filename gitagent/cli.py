import click
from rich.console import Console
from rich.panel import Panel
from .diff_utils import get_full_diff, has_changes
from .git_utils import create_and_switch_branch, add_all, commit, push_new_branch
from .llm import genetate_with_groq
from .prompt import PROMPT_TEMPLATE

console = Console()

@click.group()
def cli():
    pass

@cli.command()
def run():
    if not has_changes():
        console.print("[bold yellow]No changes detected. You're up to date.[/bold yellow]")
        return
    
    console.print(Panel("[bold cyan]gitagent is thinking...[/bold cyan]", expand=False))

    diff = get_full_diff()
    prompt = PROMPT_TEMPLATE.format(diff=diff)

    try:
        result = genetate_with_groq(prompt)
        branch_name = result["branch_name"]
        commit_message = result["commit_message"]
    except Exception as e:
        console.print(f"[red]AI failed: {e}[/red]")
        console.print("[yellow]Falling back to default branch and message...[/yellow]")

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        branch_name = f"gitagent/auto-{timestamp}"
        commit_message = "chore: auto-commit by gitagent (AI failed)"
    
    create_and_switch_branch(branch_name)
    add_all()
    commit(commit_message)
    push_new_branch(branch_name)

    console.print(Panel(
        f"[bold green]Done![/bold green]\n\n",
        f"Branch: [bold]{branch_name}[/bold]\n",
        f"Message:\n{commit_message}",
        title="gitagent success",
        expand=False
    ))

if __name__ == "__main__":
    cli()