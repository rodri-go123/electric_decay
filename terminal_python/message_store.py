# Provides atomic JSON persistence for submitted user messages.
import json
import os
import time
from pathlib import Path


def load_messages(path: Path) -> list[dict]:
    try:
        with path.open("r", encoding="utf-8") as infile:
            messages = json.load(infile)
            return messages if isinstance(messages, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def append_message(path: Path, name: str, message: str) -> dict:
    new_message = {
        "name": name,
        "message": message,
        "timestamp": time.strftime("%d-%m-%Y %H:%M:%S"),
    }
    messages = load_messages(path)
    messages.append(new_message)
    temp_path = path.with_name(f"{path.name}.tmp")
    with temp_path.open("w", encoding="utf-8") as outfile:
        json.dump(messages, outfile, indent=4)
        outfile.flush()
        os.fsync(outfile.fileno())
    os.replace(temp_path, path)
    return new_message
