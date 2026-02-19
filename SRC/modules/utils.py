import os
import sys

def get_project_root():
    """Returns the root directory of the project."""
    # Assuming this file is in SRC/modules/
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def normalize_path(path):
    """Normalizes a path to be absolute and use correct separators."""
    if not os.path.isabs(path):
        path = os.path.join(get_project_root(), path)
    return os.path.normpath(path)
