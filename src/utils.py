from typing import Any, Dict


def remove_none(dict: Dict[str, Any]):
    return {key: value for key, value in dict.items() if value is not None}
