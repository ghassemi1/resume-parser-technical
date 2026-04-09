from __future__ import annotations
import re
from typing import Any, Dict, List
from pathlib import Path
from ruamel.yaml import YAML
from src.stages.base import Stage


class RuleBasedStage(Stage):
	def configure(self, config: Dict[str, Any]) -> None:
		super().configure(config)
		self.mappings_path = Path(self.config.get("mappings", "src/config/mappings.yaml"))
		self.rules = self._load_mappings()

	def _load_mappings(self) -> Dict[str, List[Dict[str, Any]]]:
		yaml = YAML(typ="safe")
		if not self.mappings_path.exists():
			return {}
		with self.mappings_path.open("r", encoding="utf-8") as f:
			content = yaml.load(f) or {}
		return content.get("fields", {})

	def run(self, context) -> None:
		text = context.raw_text or ""
		result = context.result or {}
		for field, rules in self.rules.items():
			for r in rules:
				pattern = r.get("regex")
				if not pattern:
					continue
				flags = re.IGNORECASE
				m = re.search(pattern, text, flags)
				if m:
					val = m.group(1) if m.groups() else m.group(0)
					# apply simple postprocessing
					val = val.strip()
					# don't overwrite if already present
					if field not in result:
						result[field] = val
						break
		context.result = result
		context.meta.setdefault("rule_matches", True)

