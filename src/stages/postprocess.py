from __future__ import annotations
from typing import Any, Dict
from pathlib import Path
import json
from jsonschema import validate, ValidationError
from src.stages.base import Stage


class PostprocessStage(Stage):
	def configure(self, config: Dict[str, Any]) -> None:
		super().configure(config)
		self.schema_path = Path(self.config.get("schema", "src/schema/resume_schema.json"))
		self.fail_on_error = bool(self.config.get("fail_on_error", True))

	def run(self, context) -> None:
		# basic normalization
		result = context.result or {}
		for k, v in list(result.items()):
			if isinstance(v, str):
				result[k] = v.strip()
			if isinstance(v, list):
				result[k] = [x.strip() if isinstance(x, str) else x for x in v]

		# fallback heuristic: if name missing, try to take first non-empty line
		if "name" not in result:
			raw = (context.raw_text or "").strip()
			if raw:
				for line in raw.splitlines():
					s = line.strip()
					if not s:
						continue
					# skip lines that look like email or phone
					import re
					digits_only = re.sub(r"\D", "", s)
					if "@" in s or (len(digits_only) > 3):
						continue
					# prefer lines containing at least a space (first + last)
					if " " in s and len(s) <= 120:
						result["name"] = s
						context.meta.setdefault("name_fallback", "first_line")
						break

		# validate
		if self.schema_path.exists():
			with self.schema_path.open("r", encoding="utf-8") as f:
				schema = json.load(f)
			try:
				validate(instance=result, schema=schema)
				context.meta["validation_errors"] = None
			except ValidationError as e:
				context.meta["validation_errors"] = str(e)
				if self.fail_on_error:
					raise

		context.result = result
		context.meta.setdefault("postprocess", "done")

