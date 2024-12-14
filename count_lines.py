import os


def count_lines_in_files(root_dir, included_extensions, excluded_dirs):
    """
    This is just for a bit of fun.
    Recursively count the lines of files with extensions listed in `included_extensions`
    starting from `root_dir`, excluding any directories listed in `excluded_dirs`.

    :param root_dir: str - The starting directory for recursion.
    :param included_extensions: list[str] - File extensions to include (e.g. ['.py', '.js']).
    :param excluded_dirs: list[str] - Directory names to exclude from traversal (e.g. ['.venv', '__pycache__']).
    :return: int - Total number of lines in all matching files.
    """
    total_lines = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

        for filename in filenames:
            if any(filename.endswith(ext) for ext in included_extensions):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    line_count = sum(1 for _ in f)
                total_lines += line_count

    return total_lines


if __name__ == "__main__":
    root = "."
    exts = [".py", ".js", ".css"]
    excludes = ["venv", "__pycache__", '.git']
    total = count_lines_in_files(root, exts, excludes)
    print(f"Total lines counted: {total}")
