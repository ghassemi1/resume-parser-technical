PolicyReporter - Hybrid Extraction Skeleton
=========================================

Quickstart
---------

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

2. Run the pipeline on a PDF:

```bash
python cli.py process --input resume/Resume_5_1.pdf --config src/config/pipeline.yaml --out out/Resume_5_1.json
```

3. Toggle stages in `src/config/pipeline.yaml` or edit extraction rules in `src/config/mappings.yaml`.

Files
-----
- `src/pipeline.py` - pipeline orchestration and context
- `src/stages/` - stage implementations (text_extractor, rule_based, ner, postprocess)
- `src/config/` - pipeline and mapping YAML configs
- `src/schema/` - output JSON Schema

