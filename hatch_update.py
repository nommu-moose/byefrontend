#!/usr/bin/env python3

import sys
import subprocess
import toml
import os


def run_command(command, capture_output=False):
    result = subprocess.run(command, shell=True, check=True, capture_output=capture_output, text=True)
    if capture_output:
        return result.stdout.strip()
    return None


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ['major', 'minor', 'patch']:
        print("Usage: python bump_version.py [major|minor|patch]")
        sys.exit(1)

    increment_type = sys.argv[1]

    # Step 1: Bump the version using Hatch
    print(f"Bumping the {increment_type} version...")
    run_command(f"hatch version {increment_type}")

    # Step 2: Read the new version from pyproject.toml
    with open('pyproject.toml', 'r') as f:
        pyproject_data = toml.load(f)
    new_version = pyproject_data['project']['version']

    print(f"New version is {new_version}")

    # Step 3: Add pyproject.toml to git
    print("Adding pyproject.toml to git staging area...")
    run_command("git add pyproject.toml")

    # Step 4: Commit the change with the message
    commit_message = f"Bump version to {new_version}"
    print(f"Committing changes with message: '{commit_message}'")
    run_command(f'git commit -m "{commit_message}"')

    # Step 5: Create a git tag
    tag_name = f"v{new_version}"
    print(f"Creating git tag {tag_name}")
    run_command(f"git tag {tag_name}")

    # Step 6: Push the commit and tag to the remote repository
    print("Pushing commits and tags to remote repository...")
    run_command("git push origin main")  # Adjust branch name if necessary
    run_command(f"git push origin {tag_name}")

    print("Version bump process completed successfully.")

if __name__ == '__main__':
    main()
