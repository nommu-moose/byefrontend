#!/usr/bin/env python3
import sys
import subprocess
import argparse
import re
from pathlib import Path

def get_current_version(init_file: Path) -> str:
    content = init_file.read_text()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find __version__ in {init_file}")
    return match.group(1)

def bump_version(part: str):
    subprocess.run(
        [sys.executable, "-m", "hatch", "version", part],
        check=True
    )

def git_commit(message: str):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

def git_tag(tag_name: str, message: str):
    subprocess.run(["git", "tag", "-a", tag_name, "-m", message], check=True)


def git_push(branch="HEAD"):
    subprocess.run(["git", "push", "-u", "origin", "HEAD", "--follow-tags"], check=True)

def slugify_tag(part: str, old: str, new: str) -> str:
    # create a simple tag name without spaces
    base = f"bump-{part}-version-{old}-to-{new}"
    # replace dots and arrows for safety
    return base.replace('.', '-').replace('->', '-to-')

def main():
    parser = argparse.ArgumentParser(description="Bump version, commit, tag, and push.")
    parser.add_argument(
        "part", nargs="?", choices=["major", "minor", "patch"], default="patch",
        help="Which part to bump (default: patch)."
    )
    args = parser.parse_args()

    init_path = Path(__file__).parent / "src" / "byefrontend" / "__init__.py"
    old_version = get_current_version(init_path)

    bump_version(args.part)
    new_version = get_current_version(init_path)

    message = f"Bump {args.part} version {old_version}->{new_version}"
    tag_name = slugify_tag(args.part, old_version, new_version)

    git_commit(message)
    git_tag(tag_name, message)
    git_push()

    print(f"✅ {message}, created tag '{tag_name}', and pushed.")


if __name__ == "__main__":
    main()
