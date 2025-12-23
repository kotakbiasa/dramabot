# Copyright (c) 2025 DramaBot
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pathlib import Path

def _list_modules():
    """
    List all Python module filenames (without extension) in the current directory,
    excluding the __init__.py file.

    Returns:
        list: A list of module names as strings.
    """
    mod_dir = Path(__file__).parent
    modules = []
    for file in mod_dir.rglob("*.py"):
        if file.name == "__init__.py":
            continue
        rel_path = file.relative_to(mod_dir)
        module = str(rel_path.with_suffix("")).replace("/", ".")
        modules.append(module)
    return modules

all_modules = frozenset(sorted(_list_modules()))
