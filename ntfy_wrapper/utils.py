"""
A module containing utility functions for ntfy-wrapper.
"""
import configparser
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.theme import Theme
from xkcdpass import xkcd_password as xp

custom_theme = Theme({"code": "grey70 bold italic"})
print = Console(theme=custom_theme).print
KEYS = {
    "notifier_init": {"topics", "emails"},
    "notify_defaults": {
        "message",
        "topics",
        "emails",
        "title",
        "priority",
        "tags",
        "click",
        "attach",
        "actions",
        "icon",
    },
}


DOCSTRING = """
This INI config file contains 2 sections:
[notifier_init], and [notify_defaults].
Values in [notifier_init] can be strings or lists of strings (comma separated).
Values in [notify_defaults] can be best understood from the ntfy documentation:
https://ntfy.sh/docs/publish/
⚠️
Nota Bene: a 'topic' is kind of a password: anyone with The topic id can send messages
to your device, so protect it and make sure to remove this config file from the version
control system.
⇩
Example:
-----------------------------------------------------------------------------------------
# For Notifier(emails=..., topics=...)
[notifier_init]
topics = my-secret-topic-1, mysecrettopic2
emails = you@foo.bar

# For Notifier.notify(title=..., priority=..., etc.)
[notify_defaults]
title = Message from ntfy-wrapper
priority = 0
tags = fire
click =
attach =
actions =
icon = https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/logo.png
----------------------------------------------------------------------------------------
"""


def get_conf_path(conf_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Finds a path to the configuration file.
    If a directory is provided, the config file will be named ".ntfy.conf"
    If the path is not provided, it will look for the file in the
    current working directory,

    Args:
        conf_path (Optional[Union[str, Path]], optional): Where to look for the config
            file. Defaults to None.

    Returns:
        Path: _description_
    """
    if conf_path is None:
        path = Path.cwd()
    elif isinstance(conf_path, str):
        path = Path(conf_path)
    else:
        path = conf_path

    if path.is_dir():
        path = path / ".ntfy.conf"

    return path


def load_conf(conf_path: Optional[Union[str, Path]] = None) -> dict:
    """
    Loads a config file from the given path.
    Expects the INI format and will use configparser.

    Args:
        conf_path (Optional[Union[str, Path]], optional): Where to load the conf
        from. Defaults to None.

    Returns:
        dict: The configuration as a dictionary.
    """
    path = get_conf_path(conf_path)
    if path.exists():
        config = configparser.ConfigParser()
        config.read(path)
        conf = {}
        if config.has_section("notifier_init"):
            if "topics" in config["notifier_init"]:
                conf["topics"] = [
                    t.strip() for t in config.get("notifier_init", "topics").split(",")
                ]
            if "emails" in config["notifier_init"]:
                conf["emails"] = [
                    e.strip() for e in config.get("notifier_init", "emails").split(",")
                ]
        if config.has_section("notify_defaults"):
            conf.update(dict(config["notify_defaults"]))
        return conf

    return {
        "title": "Message from ntfy-wrapper",
        "tags": "fire",
        "icon": "https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/logo.png",  # noqa E501
    }


def write_conf(
    conf_path: Path,
    conf: Dict[str, Union[str, List[str]]],
) -> None:
    """
    Write the configuration file as an INI file.
    Always prepend the file with comments and example.

    Args:
        conf_path (Path): The path to the configuration file.
        conf (Dict[str, Union[str, List[str]]]): The configuration to write.
    """
    conf = deepcopy(conf)
    topics = conf.pop("topics", None)
    emails = conf.pop("emails", None)

    config = configparser.ConfigParser(allow_no_value=True)

    config.add_section("about")
    for line in DOCSTRING.split("\n")[1:]:
        config.set("about", ("# " + line).strip())

    config.add_section("notifier_init")
    if topics:
        config.set("notifier_init", "topics", ",".join(topics))
    if emails:
        config.set("notifier_init", "emails", ",".join(emails))

    config.add_section("notify_defaults")
    for k, v in conf.items():
        config.set("notify_defaults", k, v)

    config.write(conf_path.open("w"))


def generate_topic():
    """
    Generate a cryptographically secure topic id using ``xkcdpass``.
    See https://xkcd.com/936/ for illustration

    Returns:
        str: dash-separated topic id
    """
    wordfile = xp.locate_wordfile()
    words = xp.generate_wordlist(wordfile=wordfile, min_length=3, max_length=6)
    return "-".join(xp.generate_xkcdpassword(words, numwords=4).split())


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
