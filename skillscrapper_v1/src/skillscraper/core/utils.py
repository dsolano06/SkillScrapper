import os
import tempfile
from pathlib import Path
from typing import Any, Callable


def atomic_write(path: Path, content_fn: Callable[..., Any], **kwargs):
    """
    Writes content to a temporary file and then renames it to the target path
    to ensure the write is atomic.
    """
    path = Path(path)
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    # Create a temporary file in the same directory as the target path
    with tempfile.NamedTemporaryFile(
        "w", dir=dir_path, delete=False, encoding="utf-8", suffix=".tmp"
    ) as tf:
        temp_name = tf.name
        content_fn(tf, **kwargs)

    try:
        # Replace target path with the temporary file
        os.replace(temp_name, path)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise


def atomic_write_binary(path: Path, content_fn: Callable[..., Any], **kwargs):
    """
    Writes binary content to a temporary file and then renames it to the target path.
    """
    path = Path(path)
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        "wb", dir=dir_path, delete=False, suffix=".tmp"
    ) as tf:
        temp_name = tf.name
        content_fn(tf, **kwargs)

    try:
        os.replace(temp_name, path)
    except Exception:
        if os.path.exists(temp_name):
            os.remove(temp_name)
        raise
