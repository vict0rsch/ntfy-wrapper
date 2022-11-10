
<p align="center">
    <a href="https://github.com/vict0rsch/ntfy-wrapper" target="_blank">
        <img src="https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/ntfy-txt.png">
    </a>
</p>

`ntfy-wrapper` is a free and hassle-free customizable notifier for Python. No login, no API token, no fees, no bullshit.

It's actually a simple Python wrapper around [`ntfy`](https://ntfy.sh). Kudos to them ❤️

You can now **send** notification from your Python code and **receive** them on your computer through a [Web App](https://ntfy.sh/app) or a [CLI](https://ntfy.sh/docs/subscribe/cli/), or [on your phone with a dedicated app](https://ntfy.sh/docs/subscribe/phone/)!

Again, all credit to [`ntfy`](https://ntfy.sh).

## Install

Install `ntfy-wrapper` (and its 2 dependencies: `requests` and `typer`) with `pip`:

```bash
pip install ntfy-wrapper
```

## How to use

```python
from ntfy_wrapper import Notifier

if __name__ == "__main__":

    ntfy = Notifier(defaults={"title": "Your Project Name"})
    # grab the topic id that was just printed here ⬆️ in order
    # to subscribe to it on the web app or cli or mobile app
    # (ntfy_wrapper will dump a config file so the same id will be
    # re-used next time. Remember to *exclude* it from version control)

    ntfy.notify("Job has been allocated, starting Model training")

    try:
        results = do_some_stuff()
        if results["metric"] > threshold:
            ntfy.notify(
                f"Great model! Its metric is {results['metric']:.3f}",
                tags="white_check_mark",  # this is the ✅ emoji
                click=results["online_run_url"],
            )
        else:
            ntfy.notify(f"Done, but not great ({results['metric']:.3f})", tags="disappointed")
    except Exception as e:
        ntfy.notify(f"Error! -> {str(e)}", priority=4, emails="you@foo.bar")
```

### Command-line

`ntfy_wrapper` comes with a command-line interface called `py-ntfy`. It uses the great Python CLI tool [`Typer`](https://typer.tiangolo.com/)

* Get help

    ```bash
    $ py-ntfy --help
    Usage: py-ntfy [OPTIONS] COMMAND [ARGS]...

    ╭─ Options ─────────────────────────────────────────────────────────────────────╮
    │ --install-completion          Install completion for the current shell.       │
    │ --show-completion             Show completion for the current shell, to copy  │
    │                               it or customize the installation.               │
    │ --help                        Show this message and exit.                     │
    ╰───────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ────────────────────────────────────────────────────────────────────╮
    │ add     [command sub-group] Add a new notification target or a default        │
    │         notification value. Run `$ py-ntfy add --help` for more info.         │
    │ clean   Removes the configuration file. Use --conf-path to specify a path to  │
    │         the configuration file. Use --force to skip the confirmation prompt.  │
    │ init    Initializes the configuration file. It should NOT be tracked by       │
    │         version control in order to protect the topic ID. Use --conf-path to  │
    │         specify a path to the configuration file. Use --force to overwrite an │
    │         existing configuration file.                                          │
    │ remove  [command sub-group] Remove a notification target or a default         │
    │         notification value. Run `$ py-ntfy remove --help` for more info.      │
    │ send    Sends a notification to the given emails and topics. Optional         │
    │         command-line arguments can be passed to override the defaults in the  │
    │         config file and customize the message options. Refer to               │
    │         https://ntfy.sh/docs/publish to understand the options. Run           │
    │         `py-ntfy send --help` to see the available options.                   │
    ╰───────────────────────────────────────────────────────────────────────────────╯

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
    🔑 Your first topic is `f8e34b7a-74a3-49e7-96fc-4d89eaf6ea6c`.
    Use it to subscribe to notifications!
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

* Send a notification from the command-line with `send`

    ```bash
    $ py-ntfy send "hello" --topics 99e89137-c3a3-47fd-a616-01677b15c5b7 --title "This is Victor" --click "https://9gag.com"
    🎉 Notification sent to 99e89137-c3a3-47fd-a616-01677b15c5b7, you@foo.bar
    ```

* Change the default configuration path for any command with the option `--conf-path`
  * Specify a directory  `--conf-path path/to/conf/directory` and `.ntfy.conf` will be created there
  * Specify a file `--conf-path path/to/file.conf` and that will be used as a configuration file

## Todo

* [x] Better readme and doc
* [x] CLI
* [ ] Screenshots
* [ ] `requests` timeout or non-blocking
