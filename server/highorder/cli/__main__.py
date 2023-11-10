import asyncio
import typer
import os
import random
import string
import hashlib
import toml
import json

app = typer.Typer()

from highorder.boot import boot_components

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


async def init_postmodel():
    await boot_components()


def create_application_id():
    generated = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(18)
    )
    return "AP{}".format(generated)


def random_str(prefix="", number=10):
    generated = "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(number)
    )
    return f"{prefix}{generated}"


def get_password_safe(salt, password):
    m = hashlib.sha256(f"{salt}:{password}".encode("utf-8"))
    password_safe = m.hexdigest()
    return password_safe


class AppCreator:
    def __init__(self):
        pass

    def is_empty(self, path):
        if os.path.exists(path) and not os.path.isfile(path):
            if not os.listdir(path):
                return True
            else:
                return False
        else:
            return False

    def create(self, project):
        folder = os.path.join(os.getcwd(), project)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            self.create_app(folder)
        elif self.is_empty(folder):
            self.create_app(folder)
        else:
            typer.echo(f"Folder {project} exists and not empy, creation exited.")

    def init(self, project_folder=None):
        folder = project_folder or os.getcwd()
        if self.is_empty(folder):
            self.create_app(folder)
        else:
            typer.echo(f"Folder {folder} exists and not empy, init exited.")

    def create_app(self, folder):
        app_id = create_application_id()
        client_key = random_str("clientkey", 7)
        client_secret = random_str("clientsecret", 20)
        app_name = os.path.basename(folder)
        app_description = typer.prompt(
            "Please decribe you project",
            default="This app is make for ....",
            show_default=True,
        )
        admin_user = typer.prompt(
            "What's admin name?", default="admin", show_default=True
        )
        salt = random_str("", 4)
        admin_password = typer.prompt("Please set admin's password", hide_input=True)
        password_safe = get_password_safe(salt, admin_password)
        editor_config = {
            "app": {"app_id": app_id, "name": app_name, "description": app_description},
            "users": [{"name": admin_user, "salt": salt, "password": password_safe}],
            "server": {"client_key": client_key, "client_secret": client_secret},
        }
        server_config = {
            "log": {
                "handlers": ["stdout"],
                "stdout": {"handler_type": "stdout", "level": "debug"},
            },
            "server": {
                "db_url": "postgres://postgres:postgres@127.0.0.1:5432/highorder?min_size=10&max_size=30",
                "debug": True,
                "mode": "single",
                "port": 9000,
                "redis_urls": ["redis://127.0.0.1:6379"],
                "run_editor": True,
                "setup_keys": [
                    {"client_key": client_key, "client_secret": client_secret}
                ],
            },
        }
        with open(os.path.join(folder, "editor.json"), "w") as f:
            f.write(json.dumps(editor_config, ensure_ascii=False, indent=4))
        with open(os.path.join(folder, "settings.toml"), "w") as f:
            f.write(toml.dumps(server_config))
        typer.echo("App `{app_name}` created.")


@app.command()
def init_model():
    asyncio.run(init_postmodel())
    typer.echo(f"Init DB Models Completed.")


@app.command()
def create(project: str):
    typer.echo(f"Create Project {project}...")
    creator = AppCreator()
    creator.create(project)


@app.command()
def init():
    typer.echo(f"Init Project In Folder {os.getcwd()}...")
    creator = AppCreator()
    creator.init()


@app.command()
def help():
    typer.echo(f"Help.")


if __name__ == "__main__":
    app()
