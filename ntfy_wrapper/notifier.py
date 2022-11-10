from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

import requests

from ntfy_wrapper.utils import get_conf_path, load_conf, write_conf


class Notifier:
    def __init__(
        self,
        topics: Optional[Union[str, List[str]]] = None,
        emails: Optional[Union[str, List[str]]] = None,
        defaults: Optional[Dict] = {},
        conf_path: Optional[Union[str, Path]] = None,
        write: Optional[bool] = True,
        warnings: Optional[bool] = True,
        verbose: Optional[bool] = True,
    ):
        if isinstance(topics, str):
            topics = [topics]

        self.topics = topics
        self.emails = emails
        self.conf_path = get_conf_path(conf_path)
        self.warnings = warnings

        conf = load_conf(self.conf_path)
        conf.update(defaults)

        if self.topics is None:
            self.topics = conf.pop("topics", [str(uuid4())])
        if self.emails is None:
            self.emails = conf.pop("emails", [])

        self.defaults = conf

        if write:
            self.write_to_conf()

        assert (
            self.topics or self.emails
        ), "You must specify at least one topic or email"

        if verbose:
            self.describe()

    def _warn(self, message: str) -> None:
        """
        Print a warning message if warnings are enabled.

        Args:
            message (str): The message to print.
        """
        if self.warnings:
            print(message)

    def describe(self):
        """
        Describe the notifier.
        """
        if self.topics:
            print("📬 Notifier will push to topics: " + ", ".join(self.topics))
        if self.emails:
            print("📧 Notifier will send emails to: " + ", ".join(self.emails))
        print("🛠 Its configuration is in: " + str(self.conf_path))

    def remove_topics(
        self,
        topics: List[str],
        write: Optional[bool] = True,
    ):
        """
        Remove topics from the configuration file.
        If the topic is not in the configuration file, it is ignored.

        Args:
            topics (List[str]): The topics to remove.
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to True.
        """
        for t in topics:
            if t not in self.topics:
                self._warn(f"Topic {t} is not in the list of topics")
            else:
                self.topics.remove(t)
        if write:
            self.write_to_conf()

    def remove_emails(
        self,
        emails: List[str],
        write: Optional[bool] = True,
    ):
        """
        Remove emails from the configuration file.
        If the topic is not in the configuration file, it is ignored.

        Args:
            emails (List[str]): The emails to remove.
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to True.
        """
        for e in emails:
            if e not in self.emails:
                self._warn(f"Email {e} is not in the list of emails")
            else:
                self.emails.remove(e)
        if write:
            self.write_emails(overwrite=True)

    def remove_all_topics(self, write: Optional[bool] = True):
        """
        Remove all topics from the configuration file.

        Args:
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to True.
        """
        self.topics = []
        if write:
            self.write_to_conf()

    def write_to_conf(self):
        """
        Write the topics to the configuration file.

        Args:
            overwrite (Optional[bool], optional): Whether the potentially existing
                topics should be extended or overwritten. Defaults to False.
        """
        self._warn(
            "⚠️ Warning: your configuration may contain sensitive data. "
            + "Make sure it is ignored by your version control system "
            + "(in .gitignore for instance)."
        )
        write_conf(self.conf_path, self.topics, self.emails, self.defaults)

    def notify(
        self,
        message: str,
        topics: Optional[Union[str, List[str]]] = None,
        emails: Optional[List[str]] = None,
        title: Optional[str] = "From ntfy_wrapper",
        priority: Optional[int] = None,
        tags: Optional[Union[str, List[str]]] = None,
        click: Optional[str] = None,
        attach: Optional[str] = None,
        actions: Optional[Union[str, List[str]]] = None,
        icon: Optional[str] = None,
    ):
        """
        Send a notification to the given topics.
        Refer to the documentation of the specific notifier for more details.
        https://ntfy.sh/docs/publish/

        If topics is None, the topics are taken from the configuration file.
        If emails is not None, the notification is sent by email to the given addresses.
        If emails have been specified in the configuration file, they are used by
        default.
        Set emails="" to disable emails even if there are some in the configuration.

        NB: you cannot send both a string message and a file attachment.

        Args:
            message (str): The message to send.
            topics (Optional[Union[str, List[str]]], optional): Target topics to notify.
                Defaults to None.
            title (Optional[str], optional): The notifications' title.
                Defaults to "From ntfy_wrapper".
            priority (Optional[int], optional): The notifications' priority.
                Defaults to None.
            tags (Optional[Union[str, List[str]]], optional): The notifications' tags.
                Defaults to None.
            click (Optional[str], optional):  URL to open when a notification is
                clicked. Defaults to None.
            attach (Optional[str], optional): Attachment to send: either a local image
                file or an URL. Defaults to None.
            actions (Optional[Union[str, List[str]]], optional): A string or list of
                strings describing actions as per:
                    https://ntfy.sh/docs/publish/#using-a-header
                Defaults to None.
            emails (Optional[List[str]], optional): _description_. Defaults to None.
            icon (Optional[str], optional): The notifications' icon as a URL to a
                remote file. Defaults to None.
        """
        headers = {**self.defaults, "priority": priority}

        if attach and message:
            raise ValueError("You cannot specify both `attach` and `message`")

        use_PUT = False

        if title is not None:
            headers["Title"] = title

        if click is not None:
            headers["Click"] = click
        if icon is not None:
            headers["Icon"] = icon

        if tags is not None:
            if isinstance(tags, str):
                tags = [tags]
            headers["Tags"] = ",".join(tags)

        if attach is not None:
            if not attach.startswith("http"):
                use_PUT = True
            else:
                headers["Attach"] = attach

        if actions is not None:
            if isinstance(actions, str):
                actions = [actions]
            headers["Actions"] = ",".join(actions)

        if emails is not None:
            if isinstance(emails, str):
                emails = [emails]
            assert isinstance(emails, list)
        else:
            if self.emails:
                emails = self.emails
            else:
                emails = [None]

        if topics is None:
            topics = self.topics
        else:
            if isinstance(topics, str):
                topics = [topics]

        assert isinstance(topics, list)

        for dtype, dest in [("topic", t) for t in topics] + [
            ("email", e) for e in emails
        ]:
            h = headers.copy()

            if dtype == "email":
                h["Email"] = dest
                url = "https://ntfy.sh/alerts"
            else:
                url = f"https://ntfy.sh/{dest}"

            if not use_PUT:
                requests.post(
                    url,
                    data=message.encode("utf-8"),
                    headers=h,
                )
            else:
                h["Filename"] = Path(attach).name
                requests.put(
                    url,
                    data=open(attach, "rb"),
                    headers=h,
                )
