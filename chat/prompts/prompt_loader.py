from pathlib import Path

import yaml


PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "airport_assistant.yaml"
)


def load_system_prompt() -> str:
    with open(PROMPT_PATH, encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data["system_prompt"]