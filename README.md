# Prompt engineering lab

Experiments on few-shot prompting, chain-of-thought, and structured JSON output, run against the Gemini API.
The report is in **REPORT.md**; every prompt and raw model output is in `results/*.jsonl`.

## Reproduce

```bash
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env, then add your key
python prompt_lab.py        # runs all experiments and writes REPORT.md
```

Options: `--only sentiment|cot|json`, `--report-only` (rebuild the report from saved results),
`--dry-run` (pipeline check with FAKE outputs, written to separate files).

## Files
- `prompt_lab.py`: prompts, test inputs, scoring, and report generator
- `results/`: raw prompt/output records for every API call
- `REPORT.md`: the written report
