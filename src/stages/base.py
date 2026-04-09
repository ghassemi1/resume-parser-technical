from __future__ import annotations
from typing import Any, Dict


class Stage:
	"""Base Stage interface. Subclasses should implement `configure` and `run`."""

	def __init__(self) -> None:
		self.name = self.__class__.__name__
		self.config: Dict[str, Any] = {}

	def configure(self, config: Dict[str, Any]) -> None:
		self.config = config or {}

	def run(self, context) -> None:  # pragma: no cover - implemented in subclasses
		raise NotImplementedError()

