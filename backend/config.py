import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

DEFAULT_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "settings.json"
SETTINGS_ENV_VAR = "ASSETGEN_SETTINGS"


def load_settings(path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    settings_path = Path(path) if path is not None else Path(
        os.environ.get(SETTINGS_ENV_VAR, DEFAULT_SETTINGS_PATH)
    )
    with settings_path.open(encoding="utf-8") as settings_file:
        return json.load(settings_file)
