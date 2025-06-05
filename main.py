import os
import sys

from src.converter import Converter


if __name__ == '__main__':
    root_folder = sys.argv[1]
    if not os.path.isdir(root_folder):
        print(f"Error: The specified path '{root_folder}' is not a directory.")
        sys.exit(1)
    conv=Converter(root_folder)
    conv.obsidian_to_anytype()
