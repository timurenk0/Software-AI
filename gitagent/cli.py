import click
from gitagent.features.commit_generator import CommitGenerator
from gitagent.features.code_analyzer import CodeAnalyzer


@click.group()
def cli():
    pass

@cli.command()
def commit():
    CommitGenerator().generate()

@cli.command()
def review():
    CodeAnalyzer().review_changes()

if __name__ == "__main__":
    cli()