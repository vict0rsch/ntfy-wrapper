"""
``py-ntfy`` command-line interface.
"""
from typing import Optional

import typer


from ntfy_wrapper import Notifier
from ntfy_wrapper.utils import (
    generate_topic,
    load_conf,
    write_conf,
    code,
    print,
    get_conf_path,
    KEYS,
)


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


@app.command()
def init(conf_path: Optional[str] = None, force: bool = False):
    """
    Initializes the configuration file. It should NOT be tracked by version
    control in order to protect the topic ID.
    Use --conf-path to specify a path to the configuration file.
    Use --force to overwrite an existing configuration file.
    """
    conf_path = get_conf_path(conf_path)
    if conf_path.exists() and not force:
        print(f"Config file already exists at {code(conf_path)}")
        raise typer.Abort()
    topic = generate_topic()
    base_conf = load_conf()
    base_conf["topics"] = [topic]
    write_conf(conf_path, base_conf)
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
    conf_path = get_conf_path(conf_path)
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
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.BadParameter(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    topics = conf.get("topics", [])
    if topic not in topics:
        topics.append(topic)
        conf["topics"] = topics
    else:
        print(f"Topic {topic} already exists.")
        raise typer.Abort()

    write_conf(conf_path, conf)
    print(f"🎉 Topic {code(topic)} added to {code(conf_path)}", style="green")


@add_app.command("email")
def add_email(email: str, conf_path: Optional[str] = None):
    """
    Adds an email to the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.Abort(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    emails = conf.get("emails", [])
    if email not in emails:
        emails.append(email)
        conf["emails"] = emails
    else:
        print(f"email {email} already exists.")
        raise typer.Abort()
    write_conf(conf_path, conf)
    print(f"🎉 Email {code(email)} added to {code(conf_path)}", style="green")


@add_app.command("default")
def add_default(key: str, value: str, conf_path: Optional[str] = None):
    """
    Adds a default to the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    if key not in KEYS["notify_defaults"]:
        raise typer.BadParameter(
            f"key must be one of {KEYS['notify_defaults']}, not '{key}'"
        )
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.BadParameter(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    if key in conf:
        print(
            f"Default {code(key)} already exists: {code(conf[key])}."
            + "\nOverwriting.",
        )
    conf[key] = value
    write_conf(conf_path, conf)
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
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.BadParameter(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    topics = conf.get("topics", [])
    if topic in topics:
        topics.remove(topic)
        conf["topics"] = topics
        write_conf(conf_path, conf)
        print(f"🎉 Topic {code(topic)} removed from {code(conf_path)}", style="green")
    else:
        print(f"Topic {code(topic)} does not exist. Ignoring.")


@remove_app.command("email")
def remove_email(email: str, conf_path: Optional[str] = None):
    """
    Removes an email from the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.BadParameter(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    emails = conf.get("emails", [])
    if email in emails:
        emails.remove(email)
        conf["emails"] = emails
        write_conf(conf_path, conf)
        print(f"🎉 Email {code(email)} removed from {code(conf_path)}", style="green")
    else:
        print(f"Email {code(email)} does not exist. Ignoring.", style="yellow")


@remove_app.command("default")
def remove_default(key: str, conf_path: Optional[str] = None):
    """
    Removes a default from the config file.
    If --conf-path is not given, the current working directory will be used.
    """
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.BadParameter(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    if key in conf:
        value = conf.pop(key)
        write_conf(conf_path, conf)
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
        notify_defaults={},
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
    topic = generate_topic()
    if save:
        conf_path = get_conf_path()
        conf = load_conf(conf_path)
        topics = conf.get("topics", [])
        if topic not in topics:
            topics.append(topic)
            conf["topics"] = topics
            if not conf_path.exists():
                confirm = typer.confirm(
                    "Config file not found. Do you want to create it?"
                )
                if confirm:
                    write_conf(conf_path, conf)
                    print(
                        f"🎉 Topic {code(topic)} added to {code(conf_path)}",
                        style="green",
                    )
                else:
                    print(f"Attempted topic: {code(topic)}", style="yellow")
                    typer.Abort()
    else:
        print(f"🎉 Topic: {code(topic)}", style="green")


@app.command()
def describe(conf_path: Optional[str] = None):
    """Describes the ntfy-wrapper configuration: topics, targets and defaults."""
    conf_path = get_conf_path(conf_path)
    if not conf_path.exists():
        raise typer.BadParameter(f"Config file not found at {str(conf_path)}")
    conf = load_conf(conf_path)
    defaults = code(
        "\n   • ".join(
            [""]
            + [
                str(k) + " = " + str(v)
                for k, v in conf.items()
                if k not in ["topics", "emails"]
            ]
        )
    )
    print(f"🎉 Configuration file: {code(conf_path)}", style="green")
    print(f"   Topics: {code(', '.join(conf.get('topics', [])))}", style="green")
    print(f"   Emails: {code(', '.join(conf.get('emails', [])))}", style="green")
    print(f"   Defaults:{defaults}", style="green")


if __name__ == "__main__":
    app()
