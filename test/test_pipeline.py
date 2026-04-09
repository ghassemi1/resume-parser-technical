import tempfile
from src.stages.rule_based import RuleBasedStage
from src.pipeline import Context


def test_rule_based_simple():
	sample = """
Name: Jane Doe
Email: jane.doe@example.com
Phone: +1-555-123-4567
Skills: Python, NLP, Testing
"""
	stage = RuleBasedStage()
	stage.configure({"mappings": "src/config/mappings.yaml"})
	ctx = Context()
	ctx.raw_text = sample
	stage.run(ctx)
	assert ctx.result.get("name") is not None
	assert "jane.doe@example.com" in ctx.result.get("email")

