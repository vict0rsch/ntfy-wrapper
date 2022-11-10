from typing import Optional
from uuid import uuid4
import typer
from rich.console import Console

from ntfy_wrapper import utils

print = Console().print

app = typer.Typer()
add_app = typer.Typer()
app.add_typer(
    add_app,
    name="add",
    help="[command sub-group] Add a new notification target or a default "
    + "notification value. Run `$ py-ntfy add --help` for more info.",
)
remove_app = typer.Typer()
app.add_typer(
    remove_app,
    name="remove",
    help="[command sub-group] Remove a notification target or a default "
    + "notification value. Run `$ py-ntfy remove --help` for more info.",
)


@app.command()
def init(conf_path: Optional[str] = None, force: bool = False):
    """
    Initializes the configuration file. It should NOT be tracked by version
    control in order to protect the topic ID.
    Use --conf-path to specify a path to the configuration file.
    Use --force to overwrite an existing configuration file.
    """
    conf_path = utils.get_conf_path(conf_path)
    if conf_path.exists() and not force:
        print(f"Config file already exists at {str(conf_path)}")
        raise typer.Abort()
    utils.write_conf(conf_path, topics=[str(uuid4())], defaults=utils.load_conf())
    print(f"🎊 Config file created at {str(conf_path)}", style="green")


@app.command()
def clean(conf_path: Optional[str] = None, force: bool = False):
    """
    Removes the configuration file.
    Use --conf-path to specify a path to the configuration file.
    Use --force to skip the confirmation prompt.
    """
    conf_path = utils.get_conf_path(conf_path)
    if conf_path.exists():
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to delete {str(conf_path)}?"
            )
            if not confirm:
                raise typer.Abort()
        conf_path.unlink()
    else:
        print(f"Config file does not exist at {str(conf_path)}")
        raise typer.Abort()
    print(f"🎊 Config file removed from {str(conf_path)}", style="green")


@add_app.command("topic")
def add_topic(topic: str, conf_path: Optional[str] = None):
    """
    Adds a topic to the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = utils.get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = utils.load_conf(conf_path)
    topics = conf.get("topics", [])
    if topic not in topics:
        topics.append(topic)
    else:
        print(f"Topic {topic} already exists.")
        raise typer.Abort()
    utils.write_conf(conf_path, topics, conf.pop("emails", None), conf)
    print(f"🎊 Topic {topic} added to {str(conf_path)}", style="green")


@add_app.command("email")
def add_email(email: str, conf_path: Optional[str] = None):
    """
    Adds an email to the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = utils.get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = utils.load_conf(conf_path)
    emails = conf.get("emails", [])
    if email not in emails:
        emails.append(email)
    else:
        print(f"email {email} already exists.")
        raise typer.Abort()
    utils.write_conf(conf_path, conf.pop("topics", None), emails, conf)
    print(f"🎊 Email {email} added to {str(conf_path)}", style="green")


@add_app.command("default")
def add_default(key: str, value: str, conf_path: Optional[str] = None):
    """
    Adds a default to the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = utils.get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = utils.load_conf(conf_path)
    if key in conf:
        print(f"Default {key} already exists: {conf[key]}.\nOverwriting.")
        conf[key] = value
    utils.write_conf(
        conf_path, conf.pop("topics", None), conf.pop("emails", None), conf
    )
    print(f"🎊 Default {key}={value} added to {str(conf_path)}", style="green")


@remove_app.command("topic")
def remove_topic(topic: str, conf_path: Optional[str] = None):
    """
    Removes a topic from the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = utils.get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = utils.load_conf(conf_path)
    topics = conf.pop("topics", [])
    if topic in topics:
        topics.remove(topic)
        utils.write_conf(conf_path, topics, conf.pop("emails", None), conf)
        print(f"🎊 Topic {topic} removed from {str(conf_path)}", style="green")
    else:
        print(f"Topic {topic} does not exist. Ignoring.")


@remove_app.command("email")
def remove_email(email: str, conf_path: Optional[str] = None):
    """
    Removes an email from the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = utils.get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = utils.load_conf(conf_path)
    emails = conf.pop("emails", [])
    if email in emails:
        emails.remove(email)
        utils.write_conf(conf_path, conf.pop("topics", None), emails, conf)
        print(f"🎊 Email {email} removed from {str(conf_path)}", style="green")
    else:
        print(f"Email {email} does not exist. Ignoring.")


@remove_app.command("default")
def remove_default(key: str, conf_path: Optional[str] = None):
    """
    Removes a default from the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = utils.get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = utils.load_conf(conf_path)
    if key in conf:
        value = conf.pop(key)
        utils.write_conf(
            conf_path, conf.pop("topics", None), conf.pop("emails", None), conf
        )
        print(f"🎊 Default {key}={value} removed from {str(conf_path)}", style="green")
    else:
        print(f"Default {key} does not exist. Ignoring.")


if __name__ == "__main__":
    app()
