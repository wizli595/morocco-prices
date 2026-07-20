"""Pipe-and-filter transform chain executor."""

from typing import Any

import structlog

from src.core.ports.transformer import BaseTransformer

logger = structlog.get_logger()


class TransformChain:
    """Execute a sequence of transformers on data."""

    def __init__(self, steps: list[BaseTransformer]) -> None:
        self._steps = steps

    def execute(self, data: list[Any]) -> list[Any]:
        """Run all steps in order, returning final result."""
        result = data
        for step in self._steps:
            count_before = len(result)
            result = step.transform(result)
            logger.info(
                "transform.step.complete",
                step=step.name,
                input_count=count_before,
                output_count=len(result),
            )
        return result

    @property
    def step_names(self) -> list[str]:
        """List all step names in execution order."""
        return [s.name for s in self._steps]
