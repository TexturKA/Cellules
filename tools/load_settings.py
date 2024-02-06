import yaml
from pathlib import Path


def run(settings_file: Path = Path("./settings.yml")) -> dict:
    with settings_file.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)
