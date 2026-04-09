from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ruamel.yaml import YAML
import json

# Import concrete stages (registry)
from src.stages.base import Stage
from src.stages.text_extractor import TextExtractorStage
from src.stages.rule_based import RuleBasedStage
from src.stages.ner import NerStage
from src.stages.postprocess import PostprocessStage


@dataclass
class Context:
	input_path: Optional[Path] = None
	raw_text: Optional[str] = None
	intermediate: Dict[str, Any] = field(default_factory=dict)
	result: Dict[str, Any] = field(default_factory=dict)
	meta: Dict[str, Any] = field(default_factory=dict)


class Pipeline:
	registry = {
		"text_extractor": TextExtractorStage,
		"rule_based": RuleBasedStage,
		"ner": NerStage,
		"postprocess": PostprocessStage,
	}

	def __init__(self, config: dict):
		self.config = config
		self.stages: List[Stage] = []
		self._build_stages()

	def _build_stages(self):
		for s in self.config.get("stages", []):
			name = s.get("name")
			params = s.get("params", {}) or {}
			enabled = s.get("enabled", True)
			if not enabled:
				continue
			cls = self.registry.get(name)
			if cls is None:
				raise ValueError(f"Unknown stage: {name}")
			inst = cls()
			inst.configure(params)
			self.stages.append(inst)

	@classmethod
	def from_config(cls, config: dict):
		return cls(config)

	def run(self, input_path: Path, fail_on_validation: bool = True) -> Tuple[Dict[str, Any], Dict[str, Any]]:
		ctx = Context(input_path=input_path)
		for stage in self.stages:
			stage.run(ctx)
		# postprocess stage should have validated; respect fail_on_validation
		if fail_on_validation:
			val_errs = ctx.meta.get("validation_errors")
			if val_errs:
				raise RuntimeError(f"Validation errors: {val_errs}")
		return ctx.result, ctx.meta


def load_pipeline_yaml(path: Path):
	yaml = YAML(typ="safe")
	with path.open("r", encoding="utf-8") as f:
		return yaml.load(f)

