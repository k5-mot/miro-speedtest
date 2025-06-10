from pathlib import Path

__all__ = [file.stem for file in Path(__file__).parent.glob("[a-zA-Z0-9]*.py")]


def main() -> None:
    """Main."""
    from package.common.logger import get_logger

    logger = get_logger()
    logger.debug("Hello from miro-speedtest!")


if __name__ == "__main__":
    main()
