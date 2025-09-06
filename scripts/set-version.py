import argparse
import pathlib
import re


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    args = parser.parse_args()

    version = args.version.lstrip("v")

    target = pathlib.Path("kubeflow/__init__.py")
    content = target.read_text()
    new_content = re.sub(r'__version__\s*=\s*"[^"]*"', f'__version__ = "{version}"', content)
    if content != new_content:
        target.write_text(new_content)


if __name__ == "__main__":
    main()
