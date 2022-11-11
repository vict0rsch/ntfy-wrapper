"""
A module containing utility functions for ntfy-wrapper.
"""
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Union

from xkcdpass import xkcd_password as xp

DOCSTRING = """
This INI config file contains 2 sections:
[targets], and [message_defaults].
Values in [targets] can be strings or lists of strings (comma separated).
Values in [message_defaults] can be best understood from the ntfy documentation:
https://ntfy.sh/docs/publish/
⚠️
Nota Bene: the 'topic' is kind of a password: anyone with
The topic ID can send messages to your device, so protect it and make
sure to remove this config file from the version control system.
⇩
Example:
---------------------------------------
[targets]
topics: my-secret-topic-1, mysecrettopic2
emails: you@foo.bar
#
[message_defaults]
title=
priority=
tags=
click=
attach=
actions=
icon=
----------------------------------------
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
        if config.has_section("targets"):
            if "topics" in config["targets"]:
                conf["topics"] = [
                    t.strip() for t in config.get("targets", "topics").split(",")
                ]
            if "emails" in config["targets"]:
                conf["emails"] = [
                    e.strip() for e in config.get("targets", "emails").split(",")
                ]
        if config.has_section("message_defaults"):
            conf.update(dict(config["message_defaults"]))
        return conf

    return {
        "title": "Message from ntfy-wrapper",
        "tags": "fire",
        "icon": "https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/logo.png",  # noqa E501
    }


def write_conf(
    conf_path: Path,
    topics: Optional[List] = [],
    emails: Optional[List] = [],
    defaults: Optional[Dict] = {},
) -> None:
    """
    Write the configuration file as an INI file.
    Always prepend the file with comments and example.

    Args:
        conf_path (Path): The path to the configuration file.
        topics (Optional[List], optional): Topics to record . Defaults to [].
        emails (Optional[List], optional): Emails to record. Defaults to [].
        defaults (Optional[Dict], optional): Additional message defaults.
            Defaults to {}.
    """
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section("about")
    for line in DOCSTRING.split("\n")[1:]:
        config.set("about", ("# " + line).strip())
    config.add_section("targets")
    if topics:
        config.set("targets", "topics", ",".join(topics))
    if emails:
        config.set("targets", "emails", ",".join(emails))
    config.add_section("message_defaults")
    for k, v in defaults.items():
        config.set("message_defaults", k, v)

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
