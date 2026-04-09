import argparse
import json
from pathlib import Path
from src.pipeline import Pipeline
from ruamel.yaml import YAML

def load_yaml(path: Path):
	yaml = YAML(typ="safe")
	with path.open("r", encoding="utf-8") as f:
		return yaml.load(f)

def main():
	parser = argparse.ArgumentParser(description="PolicyReporter extraction CLI")
	parser.add_argument("command", choices=["process"], help="command to run")
	parser.add_argument("--input", "-i", required=True, help="Input PDF path")
	parser.add_argument("--config", "-c", default="src/config/pipeline.yaml", help="Pipeline YAML config")
	parser.add_argument("--out", "-o", default="out/result.json", help="Output JSON path")
	parser.add_argument("--no-validate", action="store_true", help="Do not fail on schema validation errors")
	args = parser.parse_args()

	config_path = Path(args.config)
	cfg = load_yaml(config_path)
	pipeline = Pipeline.from_config(cfg)
	result, meta = pipeline.run(input_path=Path(args.input), fail_on_validation=not args.no_validate)

	out_path = Path(args.out)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with out_path.open("w", encoding="utf-8") as f:
		json.dump({"result": result, "meta": meta}, f, indent=2)

	print(f"Wrote output to {out_path}")

if __name__ == "__main__":
	main()
