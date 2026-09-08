"""Command-line entrypoint."""

import logging

from src import constants as cons
from src.pipeline import run


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=cons.LOG_FORMAT,
    )
    run()


if __name__ == "__main__":
    main()
