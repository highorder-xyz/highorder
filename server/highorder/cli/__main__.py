import asyncio
import typer

app = typer.Typer()

from highorder.boot import boot_components

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

async def init_postmodel():
    await boot_components()

@app.command()
def init_model():
    asyncio.run(init_postmodel())
    typer.echo(f"Init DB Models Completed.")

@app.command()
def help():
    typer.echo(f"Help.")

if __name__ == '__main__':
    app()