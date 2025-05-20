import os, glob

__all__ = [
    os.path.split(os.path.splitext(file)[0])[1]
    for file in glob.glob(os.path.join(os.path.dirname(__file__), '[a-zA-Z0-9]*.py'))
]

def main() -> None:
    """Main."""
    from package.base.app_logger import get_logger

    logger = get_logger()
    logger.debug("Hello from miro-speedtest!")


if __name__ == "__main__":
    main()
