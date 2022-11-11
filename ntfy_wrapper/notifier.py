"""
Main class for ntfy-wrapper.
"""
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests

from ntfy_wrapper.utils import generate_topic, get_conf_path, load_conf, write_conf


class Notifier:
    """
    The main class in ntfy-wrapper.
    A Notifier(...) will handle both the configuration file and the notifications.
    """

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
        """
        Constructor for the Notifier class.

        Its spirit is to reduce redundancy as much as possible.
        This is why its configuration is saved in a file by default.

        It comes with sane defaults so ``ntfy = Notifier()`` is enough to get started!

        .. warning::
            Remember that a topic is much like a password:
            anyone with that string can subscribe to your notifications so
            it's probably best you do not track any piece of code containing
            your topics. That includes the configuration file this class creates
            automatically (except if ``write`` is False).

        Args:
            topics (Optional[Union[str, List[str]]], optional): String, or list of
                strings describing the default target topics to publish to using
                https://ntfy.sh. Remember that a topic is much like a password:
                anyone with that string can subscribe to your notifications so
                it's probably best you do not track any piece of code containing
                your topics. That includes the configuration file this class creates
                automatically (except if ``write`` is False).
                Defaults to None, meaning a random (uuid) topic will be generated
                for you, and re-used next time, provided you have enabled ``write``.
            emails (Optional[Union[str, List[str]]], optional): String, or list of
                strings describing the emails to send notifications to by default.
                Be aware of the rate limits: https://ntfy.sh/docs/publish/#limitations
                Defaults to None.
            defaults (Optional[Dict], optional): Dict whose keys and values will be
                default keyword arguments for the ``Notifier.notify()`` method so that
                you don't have to write the same stuff again and again throughout
                your code. Defaults to {}.
            conf_path (Optional[Union[str, Path]], optional): String or pathlib.Path
                pointing to where the Notifier should get or create its INI
                configuration file. Defaults to None, meaning ``$CWD/.ntfy.conf``.
            write (Optional[bool], optional): Whether to write the Notifier's state
                to the configuration file after initialization. Defaults to True.
            warnings (Optional[bool], optional): Whether or not to print warnings,
                in particular the version control warning if ``write`` is True (by
                default). Defaults to True.
            verbose (Optional[bool], optional): Whether to describe the Notifier after
                its initialization from your args and the (potentially non-existing)
                conf. Defaults to True.
        """
        if isinstance(topics, str):
            topics = [topics]

        self.topics = topics
        self.emails = emails
        # cwd/.ntfy.conf if conf_path is None
        self.conf_path = get_conf_path(conf_path)
        self.warnings = warnings
        # read ini config if it exists
        # otherwise, gets initialized with default values
        # that can be overwritten by the user in the conf or the init args
        conf = load_conf(self.conf_path)
        conf.update(defaults)
        conf_topics = conf.pop("topics", [generate_topic()])
        conf_emails = conf.pop("emails", [])

        if self.topics is None:
            if self.emails is None:
                self._warn(
                    "No topic set, and no email set."
                    + " Creating a random topic for you."
                )
                self.topics = conf_topics
        if self.emails is None:
            self.emails = conf_emails

        self.defaults = conf

        if write:
            # save the config file
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
        Remove topics from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.
        If a topic does not exist, it is ignored.

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
        Remove emails from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.
        If an email does not exist, it is ignored.

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
            self.write_to_conf()

    def remove_all_topics(self, write: Optional[bool] = True):
        """
        Remove all emails from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.

        Args:
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to True.
        """
        self.topics = []
        if write:
            self.write_to_conf()

    def remove_all_emails(self, write: Optional[bool] = True):
        """
        Remove all emails from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.

        Args:
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to True.
        """
        self.emails = []
        if write:
            self.write_to_conf()

    def write_to_conf(self):
        """
        Write the topics to the configuration file.
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
    ) -> List[str]:
        """
        Send a notification to the given topics and emails.

        .. note::
            Refer to the ntfy documentation more details about all those options:
            https://ntfy.sh/docs/publish/

        The ``defaults`` you may have used in the ``init()`` method are used here.
        You can override them by passing the corresponding arguments.

        If ``topics`` is None, the topics are taken from the configuration file.
        If ``emails`` is not None, the notification is sent by email to the given
        addresses.
        If ``emails`` have been specified in the configuration file, they are used by
        default.
        Set ``emails=""`` to disable emails even if there are some in the configuration.

        .. warning::
            You cannot send both a string message and a file attachment.

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
                file or an URL pointing to one. Defaults to None.
            actions (Optional[Union[str, List[str]]], optional): A string or list of
                strings describing actions as per:
                https://ntfy.sh/docs/publish/#using-a-header
                Defaults to None.
            emails (Optional[List[str]], optional): _description_. Defaults to None.
            icon (Optional[str], optional): The notifications' icon as a URL to a
                remote file. Defaults to None.

        Raises:
            ValueError: The user cannot specify both ``attach`` and ``message``

        Returns:
            List[str]: A list of the urls the notifications have been dispatched to:
                one for each topic and one for each email.
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

        dispatchs = []

        for dtype, dest in [("topic", t) for t in topics] + [
            ("email", e) for e in emails
        ]:
            h = headers.copy()

            if dtype == "email":
                h["Email"] = dest
                url = "https://ntfy.sh/alerts"
            else:
                url = f"https://ntfy.sh/{dest}"

            dispatchs.append(dest)

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
        return dispatchs
