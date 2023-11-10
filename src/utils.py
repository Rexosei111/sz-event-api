import os
import time
import uuid
from typing import Any, Dict, Optional


def remove_none(dict: Dict[str, Any]):
    return {key: value for key, value in dict.items() if value is not None}


def generate_unique_filename(prefix="", length=8):
    # Generate a UUID
    unique_id = uuid.uuid4()

    # Convert the UUID to a hexadecimal string and remove hyphens
    unique_string = unique_id.hex

    # Add an optional prefix to the unique string
    if prefix:
        unique_string = f"{prefix}_{unique_string}"
    # Return the first 'length' characters of the unique string
    return unique_string[:length]


def delete_file(file_path: str, seconds: Optional[float] = 300):
    time.sleep(seconds)
    if os.path.exists(file_path):
        # Attempt to delete the file
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file '{file_path}': {e}")
    else:
        print(f"File '{file_path}' does not exist.")
