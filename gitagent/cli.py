import click
from gitagent.agent_features.commit_generator import CommitGenerator


@click.group()
def cli():
    pass

@cli.command()
def run():
    CommitGenerator().generate()

if __name__ == "__main__":
    cli()