import os


def remove_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[0]
