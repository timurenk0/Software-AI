import click
from gitagent.features.commit_generator import CommitGenerator
from gitagent.features.code_analyzer import CodeAnalyzer
from gitagent.features.issue_resolver import IssueResolver


@click.group()
def cli():
    pass

@cli.command()
def commit():
    CommitGenerator().generate()

@cli.command()
def review():
    CodeAnalyzer().review_changes()

@cli.command()
def issues():
    IssueResolver().get_issues()

@cli.command()
@click.argument(
    "issue_number",
    type=click.INT,
    required=True
)
def resolve(issue_number):
    IssueResolver().resolve_issue(issue_number)

if __name__ == "__main__":
    cli()