"""
``py-ntfy`` command-line interface.
"""
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.theme import Theme

from ntfy_wrapper import utils, Notifier

custom_theme = Theme({"code": "grey70 bold italic"})
print = Console(theme=custom_theme).print

app = typer.Typer()
add_app = typer.Typer()
remove_app = typer.Typer()
app.add_typer(
    add_app,
    name="add",
    help="[command sub-group] Add a new notification target or a default "
    + "notification value. Run `$ py-ntfy add --help` for more info.",
)
app.add_typer(
    remove_app,
    name="remove",
    help="[command sub-group] Remove a notification target or a default "
    + "notification value. Run `$ py-ntfy remove --help` for more info.",
)


def code(value: Any) -> str:
    """
    Turns an object into a string and wraps it in a ``rich`` ``code`` block.
    A pathlib Path will be shortened to the 3 last parts of the path.

    Args:
        value (Any): Object to convert to string and wrap in
            a ``rich`` ``code`` block.

    Returns:
        str: Code-wrapped value: ``[code]{str(value)}[/code]``
    """
    if isinstance(value, Path):
        if len(value.parts) > 3:
            value = Path(*value.parts[:2], "...", *value.parts[-3:])
    return f"[code]{str(value)}[/code]"


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
        print(f"Config file already exists at {code(conf_path)}")
        raise typer.Abort()
    topic = utils.generate_topic()
    base_conf = utils.load_conf()
    base_conf.pop("emails", None)
    base_conf.pop("topics", None)
    utils.write_conf(
        conf_path,
        topics=[topic],
        defaults=base_conf,
    )
    print(
        f"🔑 Your first topic is {code(topic)}."
        + " Use it to subscribe to notifications!",
        style="yellow",
    )
    print(f"🎉 Config file created at {code(conf_path)}", style="green")


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
        print(f"Config file does not exist at {code(conf_path)}")
        raise typer.Abort()
    print(f"🎉 Config file removed from \n {code(conf_path)}", style="green")


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
    topics = conf.pop("topics", [])
    if topic not in topics:
        topics.append(topic)
    else:
        print(f"Topic {topic} already exists.")
        raise typer.Abort()
    utils.write_conf(conf_path, topics, conf.pop("emails", None), conf)
    print(f"🎉 Topic {code(topic)} added to {code(conf_path)}", style="green")


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
    emails = conf.pop("emails", [])
    if email not in emails:
        emails.append(email)
    else:
        print(f"email {email} already exists.")
        raise typer.Abort()
    utils.write_conf(conf_path, conf.pop("topics", None), emails, conf)
    print(f"🎉 Email {code(email)} added to {code(conf_path)}", style="green")


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
        print(
            f"Default {code(key)} already exists: {code(conf[key])}."
            + "\nOverwriting.",
        )
    conf[key] = value
    utils.write_conf(
        conf_path, conf.pop("topics", None), conf.pop("emails", None), conf
    )
    print(
        f"🎉 Default {code(str(key)+'='+str(value))} added to {code(conf_path)}",
        style="green",
    )


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
        print(f"🎉 Topic {code(topic)} removed from {code(conf_path)}", style="green")
    else:
        print(f"Topic {code(topic)} does not exist. Ignoring.")


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
        print(f"🎉 Email {code(email)} removed from {code(conf_path)}", style="green")
    else:
        print(f"Email {code(email)} does not exist. Ignoring.", style="yellow")


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
        print(
            f"🎉 Default {code(str(key)+'='+str(value))} removed from {code(conf_path)}",
            style="green",
        )
    else:
        print(f"Default {code(key)} does not exist. Ignoring.")


@app.command()
def send(
    message: str,
    conf_path: Optional[str] = None,
    emails: Optional[str] = None,
    topics: Optional[str] = None,
    title: Optional[str] = None,
    priority: Optional[int] = None,
    tags: Optional[str] = None,
    click: Optional[str] = None,
    attach: Optional[str] = None,
    actions: Optional[str] = None,
    icon: Optional[str] = None,
):
    """
    Sends a notification to the given emails and topics. Optional command-line arguments
    can be passed to override the defaults in the config file and customize
    the message options. Refer to https://ntfy.sh/docs/publish to understand the
    options. Run `py-ntfy send --help` to see the available options.


    Args:
        message (str): The message to send
        conf_path (Optional[str], optional): Where to load the configuration from.
            Defaults to ``None`` which means ``$CWD/.ntfy.conf``.
        emails (Optional[str], optional): Single email or comma-separated list of
            emails to dispatch the notification to. Defaults to ``None``.
        topics (Optional[str], optional): Single topic or comma-separated list of
            topics to dispatch the notification to. Defaults to ``None``.
        title (Optional[str], optional): The notification's title. Defaults to ``None``.
        priority (Optional[int], optional): The notification's priority. Defaults to
            ``None``.
        tags (Optional[str], optional): The notification's tags. Defaults to ``None``.
        click (Optional[str], optional): The notification's click option
            (url for instance). Defaults to ``None``.
        attach (Optional[str], optional): The notification's attachment.
            Defaults to ``None``.
        actions (Optional[str], optional): The notification's actions as per
            https://ntfy.sh/docs/publish/#using-a-header. Defaults to ``None``.
        icon (Optional[str], optional): _description_. Defaults to ``None``.
    """
    dispatchs = Notifier(
        topics=topics,
        emails=emails,
        defaults={},
        conf_path=conf_path,
        write=False,
        warnings=False,
        verbose=False,
    ).notify(
        message,
        title=title,
        priority=priority,
        tags=tags,
        click=click,
        attach=attach,
        actions=actions,
        icon=icon,
    )
    print(
        "🎉 Notification sent to " + ", ".join([code(d) for d in dispatchs]),
        style="green",
    )


@app.command()
def new_topic(save: Optional[bool] = False):
    """
    Generates a random topic name and saves it to the config file if
    you use the --save option.
    """
    topic = utils.generate_topic()
    if save:
        conf_path = utils.get_conf_path()
        conf = utils.load_conf(conf_path)
        topics = conf.pop("topics", [])
        emails = conf.pop("emails", [])
        if topic not in topics:
            topics.append(topic)
            utils.write_conf(conf_path, topics, emails, conf)
            print(
                f"🎉 Topic {code(topic)} added to {code(conf_path)}",
                style="green",
            )
    else:
        print(f"🎉 Topic: {code(topic)}", style="green")


if __name__ == "__main__":
    app()
