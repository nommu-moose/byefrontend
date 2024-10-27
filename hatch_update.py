#!/usr/bin/env python3
# run this with hatch run bump_version patch/minor/major
import sys
import subprocess
from importlib import util


def run_command(command, capture_output=False):
    result = subprocess.run(command, shell=True, check=True, capture_output=capture_output, text=True)
    if capture_output:
        return result.stdout.strip()
    return None


def get_current_version():
    """Dynamically import the module to get __version__."""
    spec = util.spec_from_file_location("byefrontend", "src/byefrontend/__init__.py")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    increment_type = sys.argv[1]

    print(f"Bumping the {increment_type} version...")
    run_command(f"hatch version {increment_type}")

    new_version = get_current_version()

    print(f"New version is {new_version}")

    print("Adding pyproject.toml to git staging area...")
    run_command("git add pyproject.toml")

    commit_message = f"Bump version to {new_version}"
    print(f"Committing changes with message: '{commit_message}'")
    run_command(f'git commit -m "{commit_message}"')

    tag_name = f"v{new_version}"
    print(f"Creating git tag {tag_name}")
    run_command(f"git tag {tag_name}")

    print("Pushing commits and tags to remote repository...")
    run_command("git push")
    run_command(f"git push origin {tag_name}")

    print("Version bump process completed successfully.")


if __name__ == '__main__':
    main()
