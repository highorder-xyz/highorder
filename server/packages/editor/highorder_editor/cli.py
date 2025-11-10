"""
HighOrder Editor CLI Tool
Command line interface for database and user management
"""

import typer
import os

app = typer.Typer()

from highorder_editor.model import init_db as initialize_database

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@app.command()
def init_db():
    """Initialize database schema"""
    typer.echo(f"Initializing database...")
    initialize_database()
    typer.echo(f"Database initialization completed.")


@app.command()
def create_user(email: str, password: str):
    """Create a new user"""
    from highorder_editor.service.auth import Auth
    
    user = Auth.create_user(email, password)
    typer.echo(f"User {email} created with ID: {user.user_id}")
    typer.echo(f"All users have equal access to all applications")


@app.command()
def help():
    """Show help information"""
    typer.echo(f"HighOrder Editor CLI")
    typer.echo(f"Commands:")
    typer.echo(f"  init-db              Initialize database schema")
    typer.echo(f"  create-user          Create a new user")
    typer.echo(f"  help                 Show this help message")


def main():
    """Main entry point for CLI"""
    app()


if __name__ == "__main__":
    app()
