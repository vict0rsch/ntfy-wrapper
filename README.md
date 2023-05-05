
<p align="center">
    <a href="https://github.com/vict0rsch/ntfy-wrapper" target="_blank">
        <img src="https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/ntfy-txt.png">
    </a>
</p>
<p align="center">
    <a href="https://pypi.org/project/ntfy-wrapper/"><img src="https://img.shields.io/badge/pypi%20package-0.1.7-yellowgreen" alt="PyPI version" height="18"></a>
    <a href="https://ntfy-wrapper.readthedocs.io/en/latest/index.html"><img src="https://img.shields.io/badge/docs-read%20the%20docs-blue" alt="PyPI version" height="18"></a>
    <a href="https://github.com/vict0rsch/ntfy-wrapper/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc"><img src="https://img.shields.io/github/issues-raw/vict0rsch/ntfy-wrapper" alt="Open Issues" height="18"></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/codestyle-black-red" alt="Black code style" height="18"></a>
    <a href="https://github.com/vict0rsch/ntfy-wrapper/blob/main/LICENSE><img src="https://img.shields.io/github/license/vict0rsch/ntfy-wrapper" alt="License" height="18"></a>
</p>

`ntfy-wrapper` is a free and hassle-free customizable notifier for Python. No login, no API token, no fees, no bullshit.

It's actually a simple Python wrapper around [`ntfy`](https://ntfy.sh). Kudos to them ❤️

You can now **send** notification from your Python code and **receive** them on your computer through a [Web App](https://ntfy.sh/app) or a [CLI](https://ntfy.sh/docs/subscribe/cli/), or [on your phone with a dedicated app](https://ntfy.sh/docs/subscribe/phone/)!

Again, all credit to [`ntfy`](https://ntfy.sh).

## Install

Install `ntfy-wrapper` with `pip`:

```bash
pip install ntfy-wrapper
```

Dependencies:

* `requests` for easy HTTP requests and interacting with the `ntfy.sh` API
* `typer` for a powerful and beautiful CLI
* `xkcdpass` to generate secure but human-friendly topics[^1]

## Why?

Imagine you execute jobs on a shared cluster. They are in a queue. You get notified when they start. You get notified if there's an error. You get notified with the final performance of your model and if you click on the notification, you have access to the online logs from wandb or comet.ml.

That's just one scenario inspired from my work in AI, but really you can use it in any context!

## Getting Started

```python
from ntfy_wrapper import Notifier

if __name__ == "__main__":

    ntfy = Notifier(notify_defaults={"title": "Your Project Name"})
    # IFF this is the first call to `ntfy_wrapper` in your project, this line ^
    # will print a topic id.
    # It will also write the topic id to `.ntfy.conf` so this only happens once!
    #
    # Use one of those methods (from the print or the conf file) to copy the topic id
    # and use it to subscribe to notifications from the web or mobile apps.
    #
    # You can also use the command-line `$ py-ntfy init` before executing your code
    # and the same process will happen (new topic + conf file)
    #
    # Note: anyone with your topic id can subscribe to your notification. It's probably
    # best to *exclude* the configuration file from version control.

    ntfy("Job has been allocated, starting Model training")

    try:
        results = do_some_stuff()
        if results["metric"] > threshold:
            ntfy(
                f"Great model! Its metric is {results['metric']:.3f}",
                tags="white_check_mark",  # this is the ✅ emoji
                click=results["online_run_url"],
            )
        else:
            ntfy(f"Done, but not great ({results['metric']:.3f})", tags="disappointed")
    except Exception as e:
        ntfy.notify(f"Error! -> {str(e)}", priority=4, emails="you@foo.bar")
```

Note `ntfy(message)` is equivalent to `ntfy.notify(message)`, the former is an alias of the latter.

**If you do not receive notifications** after you've made sure you've subscribed to the exact topic used by your `Notifier`, it's probably because the request being sent out is malformed. Investigate using `debug=True` in the `notify()` call (*e.g.* : `ntfy(message, debug=True)`).

## User Guide

The central concept is **"topics"**. It's basically an ID used to publish/subscribe to notifications. You should keep it secret and not easily guessable because ***anyone with the topic id can subscribe to your notifications***. In particular, you should add `.ntfy.conf` to `.gitignore`.

In short, `ntfy-wrapper` will *publish* to a *topic* and you'll have to *subscribe* to that same topic in order to receive the notification. You can receive your notification:

* On your computer
  * By opening a [local web app](https://ntfy.sh/app) <a href="https://ntfy.sh/app"><img src="https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/webapp.png" height="400"></a>
  * By setting up the [`ntfy` CLI tool](https://ntfy.sh/docs/subscribe/cli/)
* On your phone
  * By installing [a mobile app](https://ntfy.sh/docs/subscribe/phone/)

### How to use

1. Create topics in one of the following ways:
   1. configure one manually
   2. In a Python console use `ntfy_wrapper.utils.generate_topic()` to get a secure unique and human-readable topic (eg: `winter-abide-dinghy-wand`)
   3. From the command-line use `$ py-ntfy new-topic` to get a similar topic. Add `--save` to add it to the configuration.
2. Tell the `Notifier` to use this topic in one of the following ways:
   1. In your code `Notifier(topics=your_topic)` or `Notifier(topics=[topic1, topic2])`
   2. Using a **configuration file**
      1. A configuration file will be created by default when constructing a `Notifier` *except* if you add `write=False` to the `Notifier.__init__` arguments
      2. The configuration file is used to hold default values for:
         1. `targets`, i.e. a list of comma-separated `topics` and a list of comma-separated `emails`
         2. `message_defaults` which are default values used when calling `.notify(...)`
      3. You can also use `$ py-ntfy init` to initialize your `ntfy-wrapper` configuration
   3. From the command-line with `$ py-ntfy add topic your-topic`
3. Setup defaults in one of the following ways
   1. By editing the config file
   2. By using the [`py-ntfy` command-line tool](#command-line)
4. Explore notification options by referring to the original [`ntfy` docs](https://ntfy.sh/docs/publish/)

<a href="https://ntfy.sh/app"><img src="https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/mermaid.png"></a>

## Configuration file

`ntfy-wrapper` uses the INI standard along with `configparser` to parse the configuration file. It expects 2 sections:

1. `[notifier_init]` with optional fields `emails = `, `topics = ` and `base_url = ` to define systematic targets for the notification instead of putting them in your Python code. `base_url` allows to push to a different `ntfy` server than the default `https://ntfy.sh`.
2. `[notify_defaults]` with optional fields listed below, which will define default parameters used by `Notifier.notify(...)`. For instance you can set default `title` and `tags` for your code's `.notify(...)` calls and override them at specific locations with keyword arguments `.notify(title="Non-default title")`
   1. The behavior of the `title`, `priority`, `tags`, `click`, `attach`, `actions` and `icon` keys is described in the [`ntfy` docs](https://ntfy.sh/docs/publish/)

```ini
# For Notifier(emails=..., topics=...)
[notifier_init]
topics = my-secret-topic-1, mysecrettopic2
emails = you@foo.bar
base_url = https://custom-ntfy-instance.io

# For Notifier.notify(title=..., priority=..., etc.)
[notify_defaults]
title = Message from ntfy-wrapper
priority = 0
tags = fire
click =
attach =
actions =
icon = https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/logo.png
```

## Command-line

`ntfy_wrapper` comes with a command-line interface called `py-ntfy`. It uses the great Python CLI tool [`Typer`](https://typer.tiangolo.com/). Its goal is to interact with `ntfy-wrapper`'s configuration in a user-friendly way. It is different in that sense to the original [`ntfy` CLI tool](https://ntfy.sh/docs/subscribe/cli/) which is more generic.

* Get help

    ```bash
    $ py-ntfy --help
    Usage: py-ntfy [OPTIONS] COMMAND [ARGS]...

    ╭─ Options ────────────────────────────────────────────────────────────────────────────────╮
    │ --install-completion          Install completion for the current shell.                  │
    │ --show-completion             Show completion for the current shell, to copy it or       │
    │                               customize the installation.                                │
    │ --help                        Show this message and exit.                                │
    ╰──────────────────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────────────────╮
    │ add        [command sub-group] Add a new notification target or a default notification   │
    │            value. Run `$ py-ntfy add --help` for more info.                              │
    │ clean      Removes the configuration file. Use --conf-path to specify a path to the      │
    │            configuration file. Use --force to skip the confirmation prompt.              │
    │ init       Initializes the configuration file. It should NOT be tracked by version       │
    │            control in order to protect the topic ID. Use --conf-path to specify a path   │
    │            to the configuration file. Use --force to overwrite an existing configuration │
    │            file.                                                                         │
    │ new-topic  Generates a random topic name and saves it to the config file if you use the  │
    │            --save option.                                                                │
    │ remove     [command sub-group] Remove a notification target or a default notification    │
    │            value. Run `$ py-ntfy remove --help` for more info.                           │
    │ send       Sends a notification to the given emails and topics. Optional command-line    │
    │            arguments can be passed to override the defaults in the config file and       │
    │            customize the message options. Refer to https://ntfy.sh/docs/publish to       │
    │            understand the options. Run `py-ntfy send --help` to see the available        │
    │            options.                                                                      │
    ╰──────────────────────────────────────────────────────────────────────────────────────────╯

    $ py-ntfy add --help
    (similar output)

    $ py-ntfy add default --help
    (similar output)

    $ py-ntfy remove --help
    (similar output)
    ```

* Initialize the configuration file

    ```bash
    $ py-ntfy init
    🔑 Your first topic is `aloe-corset-stream-alto`. Use it to subscribe to notifications!
    🎉 Config file created at /path/to/repo/.ntfy.conf
    ```

* Add a topic or an email

    ```bash
    $ py-ntfy add topic some-secret-string-for-your-topic
    🎉 Topic `some-secret-string-for-your-topic` added to /path/to/repo/.ntfy.conf

    $ py-ntfy add email you@foo.bar
    🎉 Email you@foo.bar added to /Users/.../vict0rsch/ntfy-wrapper/.ntfy.conf
    ```

* Add a default value for the `.notify(...)` calls

    ```bash
    $ py-ntfy add default key value
    🎉 Default key=value added to /Users/.../vict0rsch/ntfy-wrapper/.ntfy.conf
    ```

* Remove items by simply replacing `add` by `remove`

    ```bash
    $ py-ntfy remove default key
    🎉 Default key=value removed from /Users/.../vict0rsch/ntfy-wrapper/.ntfy.conf

    $ py-ntfy remove email hello@you.com
    Email hello@you.com does not exist. Ignoring.
    ```

* Generate a new topic with `new-topic` and add it to your configuration with `--save`

    ```bash
    $ py-ntfy new-topic --save
    🎉 Topic nutty-tiling-clear-parlor added to /Users/.../vict0rsch/ntfy-wrapper/.ntfy.conf
    ```

* Send a notification from the command-line with `send`

    ```bash
    $ py-ntfy send "hello" --topics frays-errant-acting-huddle --title "This is Victor" --click "https://9gag.com"
    🎉 Notification sent to frays-errant-acting-huddle, you@foo.bar
    ```

* Change the default configuration path for any command with the option `--conf-path`
  * Specify a directory  `--conf-path path/to/conf/directory` and `.ntfy.conf` will be created there
  * Specify a file `--conf-path path/to/file.conf` and that will be used as a configuration file

## Todo

* [x] Better readme and doc
* [x] CLI
* [ ] Screenshots
* [ ] `requests` timeout or non-blocking

<br/>

---

<br/>

[^1]: cf [xkcd936](https://xkcd.com/936/)

<p align="center"><img src="https://imgs.xkcd.com/comics/password_strength.png"></p>
