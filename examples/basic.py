"""
About: Run a basic notification to an ntfy instance on localhost.

Prerequisites::

    docker run --name=ntfy --rm -it --publish=5555:80 \
    binwiederhier/ntfy serve \
        --base-url="http://localhost:5555" \
        --attachment-cache-dir="/tmp/ntfy-attachments" --attachment-expiry-duration="168h"

    open http://localhost:5555/testdrive

Synopsis::

    pip install ntfy-wrapper
    wget https://github.com/vict0rsch/ntfy-wrapper/raw/main/examples/basic.py
    python basic.py

References:
- https://ntfy.sh/
- https://ntfy-wrapper.readthedocs.io
"""
from ntfy_wrapper import Notifier


def main():
    notifier = Notifier(base_url="http://localhost:5555")
    notifier.notify(topics="testdrive", message="Hello, world.")


if __name__ == "__main__":
    main()
