
<p align="center">
    <img src="https://raw.githubusercontent.com/vict0rsch/ntfy-wrapper/main/assets/ntfy-wrapper.png">
</p>

`ntfy-wrapper` is a free and hassle-free customizable notifier for Python. No login, no API token, no fees, no bullshit.

It's actually a simple Python wrapper around [`ntfy`](https://ntfy.sh). Kudos to them ❤️

You can now **send** notification from your Python code and **receive** them on your computer through a [Web App](https://ntfy.sh/app) or a [CLI](https://ntfy.sh/docs/subscribe/cli/), or [on your phone with a dedicated app](https://ntfy.sh/docs/subscribe/phone/)!

Again, all credit to [`ntfy`](https://ntfy.sh).

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
        success = do_some_stuff()
        if success:
            ntfy.notify(
                f"All good!",
                tags="white_check_mark",  # this is the ✅ emoji
                click=success["online_run_url"],
            )
        else:
            ntfy.notify("Oh no, it's not working", tags="disappointed")
    except Exception as e:
        ntfy.notify(f"Error! -> {str(e)}", priority=4, emails="you@foo.bar")
```

## Todo

* [ ] Better readme and doc
* [ ] CLI
* [ ] Screenshots
* [ ] `requests` timeout or non-blocking
