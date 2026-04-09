from __future__ import annotations
from pathlib import Path
import re
from pdfminer.high_level import extract_text
from src.stages.base import Stage


def _extract_docx(path: Path) -> str:
	try:
		from docx import Document
	except Exception:
		raise RuntimeError("python-docx is required to extract .docx files")
	doc = Document(path)
	paras = [p.text for p in doc.paragraphs]
	return "\n".join(paras)


class TextExtractorStage(Stage):
	def configure(self, config):
		super().configure(config)

	def run(self, context):
		input_path: Path = context.input_path
		if input_path is None:
			raise ValueError("No input path provided to TextExtractorStage")
		if input_path.suffix.lower() in ".docx .doc".split():
			raw = _extract_docx(input_path)
		else:
			raw = extract_text(str(input_path))

		# Preserve line boundaries but strip trailing whitespace on each line
		lines = [ln.strip() for ln in raw.splitlines()]
		# remove empty lines
		text = "\n".join([ln for ln in lines if ln])
		context.raw_text = text
		context.meta["text_extracted"] = True

