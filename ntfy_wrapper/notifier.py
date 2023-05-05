"""
Main class for ntfy-wrapper.
"""
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import requests

from ntfy_wrapper.utils import (
    generate_topic,
    get_conf_path,
    load_conf,
    write_conf,
    code,
    print,
    KEYS,
)
import json


class Notifier:
    """
    The main class in ntfy-wrapper.
    A Notifier(...) will handle both the configuration file and the notifications.
    """

    def __init__(
        self,
        topics: Optional[Union[str, List[str]]] = None,
        emails: Optional[Union[str, List[str]]] = None,
        base_url: Optional[Union[str, List[str]]] = None,
        notify_defaults: Optional[Dict] = {},
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
                Defaults to ``None``, meaning a random (uuid) topic will be generated
                for you, and re-used next time, provided you have enabled ``write``.
            emails (Optional[Union[str, List[str]]], optional): String, or list of
                strings describing the emails to send notifications to by default.
                Be aware of the rate limits: https://ntfy.sh/docs/publish/#limitations
                Defaults to ``None``.
            base_url (Optional[str], optional): String or list of strings describing
                the base url to use and send notifications to. It defaults to ``None``,
                *i.e.* ``https://ntfy.sh`` but you can set it to a self-hosted ``ntfy``
                instance for example. ``base_url`` can be a list of comma-separated
                urls, in which case they will all be notified.
            notify_defaults (Optional[Dict], optional): Dict whose keys and values will
                be default keyword arguments for the ``Notifier.notify()`` method so
                that you don't have to write the same stuff again and again throughout
                your code. Defaults to ``{}``.
            conf_path (Optional[Union[str, Path]], optional): String or ``pathlib.Path``
                pointing to where the Notifier should get or create its INI
                configuration file. Defaults to ``None``, meaning ``$CWD/.ntfy.conf``.
            write (Optional[bool], optional): Whether to write the Notifier's config
                if a new topic has to be created because none pre-exist.
                Defaults to ``True``.
            warnings (Optional[bool], optional): Whether or not to print warnings,
                in particular the version control warning if ``write`` is True (by
                default). Defaults to ``True``.
            verbose (Optional[bool], optional): Whether to describe the Notifier after
                its initialization from your args and the (potentially non-existing)
                conf. Defaults to ``True``.
        """

        if isinstance(topics, str):
            topics = [topics]

        assert isinstance(notify_defaults, dict), "notify_defaults must be a dict"
        assert all(
            k in KEYS["notify_defaults"] for k in notify_defaults.keys()
        ), "notify_defaults keys must be in " + str(KEYS["notify_defaults"])

        # cwd/.ntfy.conf if conf_path is None
        self.conf_path = get_conf_path(conf_path)
        self.warnings = warnings
        # read ini config if it exists
        # otherwise, gets initialized with default values
        # that can be overwritten by the user in the conf or the init args
        conf = load_conf(self.conf_path)
        conf.update(notify_defaults)
        if topics is not None:
            conf["topics"] = topics
        if emails is not None:
            conf["emails"] = emails
        if base_url is not None:
            conf["base_url"] = base_url

        self.conf = conf

        if not self.conf.get("topics"):
            if not self.conf.get("emails"):
                self._warn(
                    "No topic set, and no email set."
                    + " Creating a random topic for you."
                )
                self.conf["topics"] = [generate_topic()]
                if write:
                    # save the config file
                    self.write_to_conf()

        assert self.conf.get("topics") or self.conf.get("emails"), (
            "You must specify at least one topic or email.\n" + self.describe()
        )

        if verbose:
            self.describe()

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        Alias for ``Notifier.notify()``.
        """
        return self.notify(*args, **kwds)

    def _warn(self, message: str) -> None:
        """
        Print a warning message if warnings are enabled.

        Args:
            message (str): The message to print.
        """
        if self.warnings:
            print(message, style="yellow")

    def describe(self):
        """
        Describe the notifier.
        """
        if self.conf.get("topics"):
            print(
                f"📬 {code('Notifier')} will push to topics: "
                + ", ".join([code(t) for t in self.conf["topics"]])
            )
        if self.conf.get("emails"):
            print(
                "📧 Notifier will send emails to: "
                + ", ".join([code(e) for e in self.conf["emails"]])
            )
        if self.conf.get("base_url"):
            print(
                "🏡 Notifier will push to base url: "
                + ", ".join([code(e) for e in self.conf["base_url"]])
            )
        keys = [
            k for k in self.conf.keys() if k not in ["topics", "emails", "base_url"]
        ]
        if keys:
            ml = max([len(k) for k in keys])
            print(f"🛠  {code('Notifier.notify(..)')} defaults:")
            for k in keys:
                print(f"  • {code(k):{ml+13}} -> {code(self.conf[k])}")
        print("🗃  Its configuration is in: " + code(self.conf_path))
        return ""

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
                Defaults to ``True``.
        """
        for t in topics:
            if t not in self.conf.get("topics", []):
                self._warn(f"Topic {t} is not in the list of topics")
            else:
                self.conf["topics"].remove(t)
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
                Defaults to ``True``.
        """
        for e in emails:
            if e not in self.conf.get("emails", []):
                self._warn(f"Email {e} is not in the list of emails")
            else:
                self.conf["emails"].remove(e)
        if write:
            self.write_to_conf()

    def remove_base_urls(
        self,
        base_urls: List[str],
        write: Optional[bool] = True,
    ):
        """
        Remove urls from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.
        If an url does not exist, it is ignored.

        Args:
            base_urls (List[str]): The base_urls to remove.
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to ``True``.
        """
        for e in base_urls:
            if e not in self.conf.get("base_url", []):
                self._warn(f"URL {e} is not in the list of base_url")
            else:
                self.conf["base_url"].remove(e)
        if write:
            self.write_to_conf()

    def remove_all_topics(self, write: Optional[bool] = True):
        """
        Remove all emails from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.

        Args:
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to ``True``.
        """
        self.conf["topics"] = []
        if write:
            self.write_to_conf()

    def remove_all_emails(self, write: Optional[bool] = True):
        """
        Remove all emails from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.

        Args:
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to ``True``.
        """
        self.conf["emails"] = []
        if write:
            self.write_to_conf()

    def remove_all_base_urls(self, write: Optional[bool] = True):
        """
        Remove all base urls from the Notifier's targets.
        If ``write`` is True, the configuration file is updated.

        Args:
            write (Optional[bool], optional): Whether to update the config file or not.
                Defaults to ``True``.
        """
        self.conf["base_url"] = []
        if write:
            self.write_to_conf()

    def write_to_conf(self):
        """
        Write the topics to the configuration file.
        """
        self._warn(
            "❗️ Warning: your configuration may contain sensitive data. "
            + "Make sure it is ignored by your version control system "
            + f"(in {code('.gitignore')} for instance)."
            + f" Use {code('warnings=False')} in {code('Notifier.__init__')}"
            + " to disable this warning."
        )
        write_conf(self.conf_path, self.conf)

    def update_notify_defaults(
        self, notify_defaults: Dict[str, Any], write: bool = True
    ):
        """
        Add notify defaults to the Notifier's configuration.
        If a key already exists, it is overwritten.

        Args:
            notify_defaults (Dict[str, Any]): The notify defaults to add.
        """
        assert isinstance(notify_defaults, dict), "notify_defaults must be a dict"
        assert all(
            k in KEYS["notify_defaults"] for k in notify_defaults.keys()
        ), "notify_defaults keys must be in " + str(KEYS["notify_defaults"])
        self.conf.update(notify_defaults)
        if write:
            self.write_to_conf()

    def remove_notify_defaults(self, notify_defaults: List[str], write: bool = True):
        """
        Remove notify defaults from the Notifier's configuration.
        If a key does not exist, it is ignored.

        Args:
            notify_defaults (List[str]): The notify defaults to remove.
        """
        assert isinstance(notify_defaults, list), "notify_defaults must be a list"
        assert all(
            k in KEYS["notify_defaults"] for k in notify_defaults
        ), "notify_defaults keys must be in " + str(KEYS["notify_defaults"])
        for k in notify_defaults:
            if k in self.conf:
                del self.conf[k]
        if write:
            self.write_to_conf()

    def notify(
        self,
        message: str,
        topics: Optional[Union[str, List[str]]] = None,
        emails: Optional[Union[str, List[str]]] = None,
        base_url: Optional[Union[str, List[str]]] = None,
        title: Optional[str] = None,
        priority: Optional[int] = None,
        tags: Optional[Union[str, List[str]]] = None,
        click: Optional[str] = None,
        attach: Optional[str] = None,
        actions: Optional[Union[str, List[str]]] = None,
        icon: Optional[str] = None,
        debug: Optional[bool] = False,
    ) -> List[str]:
        """
        Send a notification to the given topics and emails.

        .. note::
            Refer to the ntfy documentation more details about all those options:
            https://ntfy.sh/docs/publish/

        The ``defaults`` you may have used in the ``init()`` method are used here.
        You can override them by passing the corresponding arguments.

        In other words: ``arg`` > ``self.conf`` > ``defaults``.

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
                Defaults to ``None``.
            emails (Optional[Union[str, List[str]]], optional): Target emails to send
                notifications to. Defaults to ``None``.
            base_url (Optional[Union[str, List[str]]], optional): The base URL to use
                for the API. Can be a coma-separated list of URLs. Defaults to ``None``,
                i.e. ``https://ntfy.sh`` if ``base_url`` is neither an arg nor in the
                config.
            title (Optional[str], optional): The notifications' title.
                Defaults to "From ntfy_wrapper".
            priority (Optional[int], optional): The notifications' priority.
                Defaults to ``None``.
            tags (Optional[Union[str, List[str]]], optional): The notifications' tags.
                Defaults to ``None``.
            click (Optional[str], optional):  URL to open when a notification is
                clicked. Defaults to ``None``.
            attach (Optional[str], optional): Attachment to send: either a local image
                file or an URL pointing to one. Defaults to ``None``.
            actions (Optional[Union[str, List[str]]], optional): A string or list of
                strings describing actions as per:
                https://ntfy.sh/docs/publish/#using-a-header
                Defaults to ``None``.
            icon (Optional[str], optional): The notifications' icon as a URL to a
                remote file. Defaults to ``None``.
            debug (Optional[bool], optional): Whether to print debug information or not.
                Defaults to ``False``.

        Raises:
            ValueError: The user cannot specify both ``attach`` and ``message``

        Returns:
            List[str]: A list of the targets notifications have been dispatched to:
                one for each topic and one for each email.
        """
        defaults = {
            k.capitalize(): v
            for k, v in self.conf.items()
            if k not in {"topics", "emails", "base_url"}
        }
        headers = {**defaults, "priority": priority}
        headers = {k: v for k, v in headers.items() if v is not None}

        if attach and message:
            raise ValueError("You cannot specify both `attach` and `message`")

        use_PUT = False

        if base_url is None:
            base_url = self.conf.get("base_url", ["https://ntfy.sh"])
        if isinstance(base_url, str):
            if "," in base_url:
                base_urls = [u.strip() for u in base_url.split(",")]
            else:
                base_urls = [base_url]
        if not isinstance(base_urls, list) or not base_urls or not base_urls[0]:
            self._warn(
                "\nNo base URL specified in conf or as argument,"
                + " using https://ntfy.sh\n"
            )
            base_urls = ["https://ntfy.sh"]

        for u in base_urls:
            if not u.startswith("http"):
                self._warn(f"\nBe careful, base url does not start with `http` : {u}\n")

        base_urls = [u[:-1] if u.endswith("/") else u for u in base_urls]

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
        else:
            emails = self.conf.get("emails", [])

        if topics is not None:
            if isinstance(topics, str):
                topics = [topics]
        else:
            topics = self.conf.get("topics", [])

        assert isinstance(emails, list)
        assert isinstance(topics, list)
        assert isinstance(base_urls, list)

        dispatchs = []
        for base_url in base_urls:
            for dtype, dest in [("topic", t) for t in topics] + [
                ("email", e) for e in emails
            ]:
                h = headers.copy()

                if dtype == "email":
                    h["Email"] = dest
                    url = f"{base_url}/alerts"
                else:
                    url = f"{base_url}/{dest}"

                dispatchs.append(dest)

                if not use_PUT:
                    if debug:
                        print(f"➡️ Sending `{message}` to `{dest}`:")
                        print("    target url: ", url)
                        print("    message: ", message.encode("utf-8"))
                        print(
                            "    headers: ",
                            "\n    ".join(json.dumps(h, indent=2).splitlines()),
                        )
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

        if debug:
            print(
                "\nDebug mode: make sure the above messages,"
                + " headers and targets are correct."
            )
            print(
                "In particular, no `None` should appear in the headers, and all their"
                + " keys should start with an uppercase letter."
            )
            print(
                "Refer to the `ntfy` documentation for more details about the exact "
                + "syntax for individual headers: https://ntfy.sh/docs/publish/"
            )

        return dispatchs
