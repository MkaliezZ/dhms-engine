"""Model routing for aligned DHMS v2 experiments."""

from typing import Iterable, List

from model_registry import BaseModel, create_model


def parse_model_names(models: str) -> List[str]:
    names = [item.strip().lower() for item in models.split(",") if item.strip()]
    return names or ["mock"]


def select_models(models: str) -> List[BaseModel]:
    return [create_model(name) for name in parse_model_names(models)]


def model_names(selected: Iterable[BaseModel]) -> List[str]:
    return [model.name for model in selected]

