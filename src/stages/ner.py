from __future__ import annotations
from typing import Any, Dict
from src.stages.base import Stage
from pathlib import Path
from ruamel.yaml import YAML
from collections import defaultdict
import logging

log = logging.getLogger(__name__)


class NerStage(Stage):
	def configure(self, config: Dict[str, Any]) -> None:
		super().configure(config)
		self.enabled = bool(self.config.get("enabled", True))
		self.model = self.config.get("model", "en_core_web_sm")
		self.mappings_path = Path(self.config.get("mappings", "src/config/mappings.yaml"))
		self.overwrite = bool(self.config.get("overwrite", False))
		self.label_map = self._load_mappings()

	def _load_mappings(self) -> Dict[str, str]:
		yaml = YAML(typ="safe")
		if not self.mappings_path.exists():
			return {}
		with self.mappings_path.open("r", encoding="utf-8") as f:
			content = yaml.load(f) or {}
		return content.get("ner_mappings", {})

	def run(self, context) -> None:
		if not self.enabled:
			context.meta.setdefault("ner", "skipped")
			return

		try:
			import spacy
		except Exception:
			context.meta.setdefault("ner_error", "spaCy not installed")
			return

		text = context.raw_text or ""

		# Try to load the model, attempt download if missing
		try:
			nlp = spacy.load(self.model)
		except Exception as e:
			try:
				log.info("spaCy model %s not found, attempting to download", self.model)
				from spacy.cli import download

				download(self.model)
				nlp = spacy.load(self.model)
			except Exception as e2:
				context.meta.setdefault("ner_error", f"failed to load spaCy model: {e2}")
				return

		doc = nlp(text)
		mapped = defaultdict(list)
		unmapped = defaultdict(list)
		for ent in doc.ents:
			label = ent.label_
			text_val = ent.text.strip()
			if label in self.label_map:
				mapped[self.label_map[label]].append(text_val)
			else:
				unmapped[label].append(text_val)

		# Merge mapped entities into result according to overwrite policy
		for field, vals in mapped.items():
			if not vals:
				continue
			existing = context.result.get(field)
			if existing and not self.overwrite:
				# keep existing
				continue
			# if single value, set string, else list
			context.result[field] = vals[0] if len(vals) == 1 else vals

		# store unmapped label buckets under ner_{label}
		for label, vals in unmapped.items():
			key = f"ner_{label.lower()}"
			context.result.setdefault(key, vals)

		context.meta.setdefault("ner", "done")

