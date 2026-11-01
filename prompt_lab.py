from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import sys
import time
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
RUNS = int(os.getenv("RUNS", "2"))                    # repeats per input (to measure consistency)
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))  # >0 on purpose: exposes inconsistency
SLEEP_S = float(os.getenv("SLEEP_BETWEEN_CALLS_S", "2"))  # be gentle with free-tier rate limits

# =====================================================================================
# EXPERIMENT 1: zero-shot vs few-shot (sentiment classification)
# The two prompts are IDENTICAL except for the examples block, so any difference is
# caused by the examples and nothing else.
# =====================================================================================
LABELS = ["positive", "negative", "neutral", "mixed"]

SENTIMENT_CASES = [
    {"id": "S1", "input": "Absolutely love this phone, the camera is stunning!", "gold": "positive"},
    {"id": "S2", "input": "Stopped working after two days. Total waste of money.", "gold": "negative"},
    {"id": "S3", "input": "It arrived on Tuesday in a brown box.", "gold": "neutral"},
    {"id": "S4", "input": "Great screen, but the battery barely lasts half a day.", "gold": "mixed"},
    {"id": "S5", "input": "Oh wonderful, another update that breaks everything. Thanks a lot.", "gold": "negative"},
    {"id": "S6", "input": "Not bad at all, honestly better than I expected.", "gold": "positive"},
    {"id": "S7", "input": "The food was fine. Nothing special, nothing terrible.", "gold": "neutral"},
    {"id": "S8", "input": "Service was painfully slow, yet the pasta was the best I've ever had.", "gold": "mixed"},
    {"id": "S9", "input": "Wish I had bought this sooner. Zero complaints.", "gold": "positive"},
    {"id": "S10", "input": "Would not recommend. The staff were rude and the room was dirty.", "gold": "negative"},
]

_SENT_HEAD = "Classify the sentiment of the following review as one of: positive, negative, neutral, mixed.\n\n"
SENTIMENT_VARIANTS = {
    "zero_shot": _SENT_HEAD + "Review: {input}\nSentiment:",
    "few_shot": _SENT_HEAD
    + "Review: The battery life is amazing and setup took two minutes.\nSentiment: positive\n\n"
    + "Review: Customer support ignored me for a week. Never again.\nSentiment: negative\n\n"
    + "Review: The package contains a charger and a manual.\nSentiment: neutral\n\n"
    + "Review: Loved the design, hated the price.\nSentiment: mixed\n\n"
    + "Review: Yeah, because crashing every hour is exactly what I wanted.\nSentiment: negative\n\n"
    + "Review: {input}\nSentiment:",
}


def score_sentiment(raw: str, case: dict) -> dict:
    text = raw.strip().lower()
    cleaned = text.strip(".!'\"` *")
    format_ok = cleaned in LABELS                      # output is exactly one label word
    positions = {l: m.start() for l in LABELS if (m := re.search(rf"\b{l}\b", text))}
    lenient = min(positions, key=positions.get) if positions else None   # earliest label mentioned
    return {
        "format_ok": format_ok,
        "strict_correct": format_ok and cleaned == case["gold"],
        "lenient_label": lenient,
        "lenient_correct": lenient == case["gold"],
    }


# =====================================================================================
# EXPERIMENT 2: chain-of-thought (multi-step reasoning)
# =====================================================================================
def _nums(s: str) -> list[float]:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s.replace(",", ""))]


COT_CASES = [
    {"id": "P1", "expected": "12:15 PM",
     "input": "A train leaves a station at 9:15 AM travelling at 60 km/h. A second train leaves the same station on the same track at 10:00 AM, travelling at 80 km/h in the same direction. At what time does the second train catch up with the first?",
     "check": lambda a: re.search(r"\b12[:.]15\b", a) is not None},
    {"id": "P2", "expected": "2000",
     "input": "A shop buys a jacket, marks the price up by 40% over its cost, and then gives a 25% discount on the marked price. The jacket sells for ₹2,100. What did the shop originally pay for the jacket (in ₹)?",
     "check": lambda a: any(abs(n - 2000) < 1e-6 for n in _nums(a))},
    {"id": "P3", "expected": "20",
     "input": "Aman is currently twice as old as Bela. Five years ago, Aman was three times as old as Bela. How old is Aman now?",
     "check": lambda a: any(abs(n - 20) < 1e-6 for n in _nums(a))},
    {"id": "P4", "expected": "4.8",
     "input": "Tap A can fill an empty tank in 6 hours, tap B can fill it in 8 hours, and drain C can empty a full tank in 12 hours. If A, B and C are all opened together on an empty tank, how many hours does it take to fill the tank? Give the answer as a decimal number of hours.",
     "check": lambda a: any(abs(n - 4.8) < 1e-6 for n in _nums(a))},
    {"id": "P5", "expected": "41",
     "input": "How many integers from 1 to 100 inclusive are divisible by 3 or by 5, but NOT divisible by 15?",
     "check": lambda a: any(abs(n - 41) < 1e-6 for n in _nums(a))},
    {"id": "P6", "expected": "9900",
     "input": "Priya invests ₹10,000 at 10% interest compounded annually. At the end of year 1, right after the interest is added, she withdraws ₹2,000. How much is in the account at the end of year 2 (in ₹)?",
     "check": lambda a: any(abs(n - 9900) < 1e-6 for n in _nums(a))},
]

COT_VARIANTS = {
    "direct": "{input}\n\nGive only the final answer with no explanation or working. End with exactly one line in this form:\nFINAL: <answer>",
    "chain_of_thought": "{input}\n\nThink step by step, showing your working. Then end with exactly one line in this form:\nFINAL: <answer>",
}


def score_cot(raw: str, case: dict) -> dict:
    finals = re.findall(r"FINAL:\s*(.+)", raw, flags=re.IGNORECASE)
    if not finals:
        return {"extracted": None, "has_final": False, "correct": False}
    answer = finals[-1].replace("*", "").strip()
    return {"extracted": answer, "has_final": True, "correct": bool(case["check"](answer))}


# =====================================================================================
# EXPERIMENT 3: structured JSON output
# =====================================================================================
KEYS = {"name", "date", "amount", "currency"}
JSON_CASES = [
    {"id": "J1", "input": "hey its priya sharma here, paid the rent yesterday — 15th Oct 2025 — total came to ₹18,500 incl. maintenance",
     "gold": {"name": "Priya Sharma", "date": "2025-10-15", "amount": 18500, "currency": "INR"}},
    {"id": "J2", "input": "INVOICE #4471 // Bill to: Marcus O'Neil // Issued: 2025-03-02 // Amount due: $1,249.99 USD",
     "gold": {"name": "Marcus O'Neil", "date": "2025-03-02", "amount": 1249.99, "currency": "USD"}},
    {"id": "J3", "input": "Received 2,500 euros from Jean-Luc Picard on the fourth of July, 2024. Thanks!!",
     "gold": {"name": "Jean-Luc Picard", "date": "2024-07-04", "amount": 2500, "currency": "EUR"}},
    {"id": "J4", "input": "Dr. Anita Desai - consultation fee Rs. 800/- dated 09/11/2025 (dd/mm/yyyy)",
     "gold": {"name": "Anita Desai", "date": "2025-11-09", "amount": 800, "currency": "INR"}},
    {"id": "J5", "input": "Thomas Idris bought a laptop on March 3, 2025 for £1,199.50 (receipt attached)",
     "gold": {"name": "Thomas Idris", "date": "2025-03-03", "amount": 1199.5, "currency": "GBP"}},
    {"id": "J6", "input": "Ref: refund to Li Wei, 12 January 2026, amount: 75 CAD.",
     "gold": {"name": "Li Wei", "date": "2026-01-12", "amount": 75, "currency": "CAD"}},
    {"id": "J7", "input": "Aisha Khan paid by card on 20 Feb 2025, forgot to note down the total.",
     "gold": {"name": "Aisha Khan", "date": "2025-02-20", "amount": None, "currency": None}},
    {"id": "J8", "input": "Paid ₹500 to Ravi Kumar on 1 Dec 2025 (his bill was ₹650 but he gave a discount of ₹150).",
     "gold": {"name": "Ravi Kumar", "date": "2025-12-01", "amount": 500, "currency": "INR"}},
]

JSON_SCHEMA_TEXT = """{
  "name": string | null,       // full name of the person involved
  "date": string | null,       // ISO format YYYY-MM-DD
  "amount": number | null,     // plain number, no currency symbol or thousands separators
  "currency": string | null    // ISO 4217 code such as INR, USD, EUR
}"""

_V2 = ("Extract payment details from the text below.\n\n"
       "Return ONLY a JSON object (no markdown, no code fences, no commentary) with exactly these keys:\n"
       + JSON_SCHEMA_TEXT + "\n\n"
       "Rules: use null for any field that is not stated in the text. Do not guess. "
       "If several amounts appear, use the amount actually paid.\n\n")
_EXAMPLES = ("Example 1\nText: Invoice for Carla Mendes dated 2024-06-30, total 310.50 USD.\n"
             'Output: {"name": "Carla Mendes", "date": "2024-06-30", "amount": 310.5, "currency": "USD"}\n\n'
             "Example 2\nText: Sanjay paid us on 5 May 2025 but didn't say how much.\n"
             'Output: {"name": "Sanjay", "date": "2025-05-05", "amount": null, "currency": null}\n\n')

JSON_VARIANTS = {
    "v1_naive": "Extract the name, date and amount from this text as JSON.\n\nText: {input}",
    "v2_explicit_schema": _V2 + "Text: {input}",
    "v3_schema_plus_examples": _V2 + _EXAMPLES + "Text: {input}",
    "v4_examples_plus_json_mode": _V2 + _EXAMPLES + "Text: {input}",  # same prompt + API JSON mode
}
JSON_MODE_VARIANTS = {"v4_examples_plus_json_mode"}


def _strip_fences(t: str) -> str:
    return re.sub(r"^```[a-zA-Z]*\s*|\s*```\s*$", "", t.strip())


def _norm(s):
    return re.sub(r"\s+", " ", s.replace("\u2019", "'")).strip().casefold() if isinstance(s, str) else s


def score_json(raw: str, case: dict) -> dict:
    r = {"strict_parse": False, "cleaned_parse": False, "schema_ok": False, "correct": False, "problems": []}
    try:
        json.loads(raw); r["strict_parse"] = True
    except Exception:
        r["problems"].append("raw output is not valid JSON as returned")
    try:
        obj = json.loads(_strip_fences(raw)); r["cleaned_parse"] = True
    except Exception:
        r["problems"].append("not parseable even after stripping code fences")
        return r
    if not isinstance(obj, dict):
        r["problems"].append("top-level value is not an object"); return r
    probs = []
    if set(obj) != KEYS:
        probs.append(f"keys are {sorted(obj)}, expected {sorted(KEYS)}")
    def t_ok(v, kinds): return v is None or (isinstance(v, kinds) and not isinstance(v, bool))
    if not t_ok(obj.get("name"), str): probs.append("name is not string/null")
    if not t_ok(obj.get("currency"), str): probs.append("currency is not string/null")
    if not t_ok(obj.get("amount"), (int, float)): probs.append("amount is not number/null")
    d = obj.get("date")
    if not (d is None or (isinstance(d, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", d))):
        probs.append(f"date {d!r} is not YYYY-MM-DD")
    r["schema_ok"] = not probs
    r["problems"] += probs
    if r["schema_ok"]:
        g, diffs = case["gold"], []
        if _norm(obj["name"]) != _norm(g["name"]): diffs.append(f"name got {obj['name']!r} expected {g['name']!r}")
        if obj["date"] != g["date"]: diffs.append(f"date got {obj['date']!r} expected {g['date']!r}")
        a = obj["amount"]
        if not ((a is None) if g["amount"] is None else (a is not None and abs(a - g["amount"]) < 0.005)):
            diffs.append(f"amount got {a!r} expected {g['amount']!r}")
        cur = obj["currency"].upper() if isinstance(obj["currency"], str) else None
        if cur != g["currency"]: diffs.append(f"currency got {obj['currency']!r} expected {g['currency']!r}")
        r["correct"] = not diffs
        r["problems"] += diffs
    return r


# =====================================================================================
# Model callers
# =====================================================================================
class GeminiCaller:
    def __init__(self):
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            sys.exit("GEMINI_API_KEY is missing. Put it in a .env file (see .env.example).")
        from google import genai
        from google.genai import errors, types
        self.errors, self.types = errors, types
        self.client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=60000))
        # Ladder of ways to switch off / minimise hidden "thinking"; we move down it when the API says 400.
        self.think_options = ["thinking_budget=0", 'thinking_level="minimal"', 'thinking_level="low"', "none (could not reduce thinking)"]
        self.think_idx = 0
        self.thinking_mode = None  # the option that actually worked, recorded in the report

    def _config(self, json_mode: bool, disable_thinking: bool):
        t = self.types
        kw = {"temperature": TEMPERATURE}
        if json_mode:
            S, T = t.Schema, t.Type
            kw["response_mime_type"] = "application/json"
            kw["response_schema"] = S(
                type=T.OBJECT,
                properties={"name": S(type=T.STRING, nullable=True), "date": S(type=T.STRING, nullable=True),
                            "amount": S(type=T.NUMBER, nullable=True), "currency": S(type=T.STRING, nullable=True)},
                required=["name", "date", "amount", "currency"])
        if disable_thinking:
            tc = self._thinking_config()
            if tc is not None:
                kw["thinking_config"] = tc
        return t.GenerateContentConfig(**kw)

    def _thinking_config(self):
        t = self.types
        while self.think_idx < len(self.think_options) - 1:
            try:
                if self.think_idx == 0:
                    return t.ThinkingConfig(thinking_budget=0)
                level = "minimal" if self.think_idx == 1 else "low"
                return t.ThinkingConfig(thinking_level=level)
            except Exception:       # this SDK version does not know the field: skip to next option
                self.think_idx += 1
        return None

    def __call__(self, prompt: str, json_mode=False, disable_thinking=False) -> dict:
        start = time.time()
        for attempt in range(12):
            try:
                resp = self.client.models.generate_content(
                    model=MODEL, contents=prompt, config=self._config(json_mode, disable_thinking))
                text = resp.text or ""
                um = getattr(resp, "usage_metadata", None)
                if disable_thinking:
                    self.thinking_mode = self.think_options[self.think_idx]
                return {"raw_output": text, "error": None if text.strip() else "empty response",
                        "latency_s": round(time.time() - start, 2),
                        "thought_tokens": getattr(um, "thoughts_token_count", None) if um else None}
            except self.errors.APIError as e:
                code, msg = getattr(e, "code", None), str(e)
                if code == 400 and disable_thinking and self.think_idx < len(self.think_options) - 1:
                    print(f"    400 with {self.think_options[self.think_idx]}; trying {self.think_options[self.think_idx + 1]}")
                    self.think_idx += 1
                    continue
                if code in (429, 500, 502, 503, 504) and attempt < 11:
                    wait = min(5 * 2 ** min(attempt, 4), 60)
                    print(f"    API {code}, retrying in {wait}s ...")
                    time.sleep(wait); continue
                return {"raw_output": "", "error": f"{code}: {msg[:300]}",
                        "latency_s": round(time.time() - start, 2), "thought_tokens": None}
            except Exception as e:
                return {"raw_output": "", "error": f"{type(e).__name__}: {str(e)[:300]}",
                        "latency_s": round(time.time() - start, 2), "thought_tokens": None}


class DryRunCaller:
    """Produces FAKE outputs so you can check the pipeline without using API quota."""
    thinking_mode = "dry-run"

    def __init__(self):
        self.rng = random.Random(0)

    def __call__(self, prompt, json_mode=False, disable_thinking=False):
        r = self.rng
        if "FINAL:" in prompt:
            out = "FAKE working...\nFINAL: " + r.choice(["20", "41", "2000", "12:15 PM", "7"])
        elif prompt.rstrip().endswith("Sentiment:"):
            out = r.choice(LABELS + ["**Sentiment: Mixed** (fake long answer)"])
        else:
            body = '{"name": "Fake Name", "date": "2025-01-01", "amount": 1, "currency": "USD"}'
            out = r.choice([body, "```json\n" + body + "\n```", "Sure! Here you go: " + body])
        return {"raw_output": out, "error": None, "latency_s": 0.0, "thought_tokens": None}


# =====================================================================================
# Runner
# =====================================================================================
def run_grid(exp, variants, cases, scorer, caller, out_dir: Path, json_variants=(), disable_thinking=False, dry=False):
    path = out_dir / f"{exp}.jsonl"
    total = len(cases) * RUNS * len(variants)
    done = 0
    with path.open("w", encoding="utf-8") as f:
        for case in cases:
            for run in range(1, RUNS + 1):
                for vname, template in variants.items():
                    prompt = template.replace("{input}", case["input"])
                    res = caller(prompt, json_mode=vname in json_variants, disable_thinking=disable_thinking)
                    pub = {k: v for k, v in case.items() if k != "check"}
                    score = scorer(res["raw_output"], case) if not res["error"] else {"correct": False, "strict_correct": False,
                            "lenient_correct": False, "format_ok": False, "cleaned_parse": False, "strict_parse": False,
                            "schema_ok": False, "has_final": False, "problems": [f"API error: {res['error']}"]}
                    rec = {"exp": exp, "variant": vname, "case_id": case["id"], "run": run, "case": pub,
                           "prompt": prompt, **res, "score": score}
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                    done += 1
                    print(f"[{exp}] {done}/{total} {vname} {case['id']} run{run}" + (f"  ERROR {res['error']}" if res["error"] else ""))
                    if not dry:
                        time.sleep(SLEEP_S)


# =====================================================================================
# Report generation (reads only the saved results)
# =====================================================================================
def fence(text: str, lang: str = "") -> str:
    longest = max([len(m) for m in re.findall(r"`+", text)] or [0])
    f = "`" * max(3, longest + 1)
    return f"{f}{lang}\n{text}\n{f}"


def cell(s, n=48) -> str:
    s = (s or "").replace("\r", "").replace("\n", " ⏎ ").replace("|", "\\|")
    return s if len(s) <= n else s[: n - 1] + "…"


def load(out_dir: Path, exp: str) -> list[dict]:
    p = out_dir / f"{exp}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def pct(n, d) -> str:
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "n/a"


def raw_blocks(recs: list[dict], mark) -> str:
    out = []
    for r in recs:
        out.append(f"<details><summary>{r['variant']} · {r['case_id']} · run {r['run']} · {mark(r)}</summary>\n")
        if r["error"]:
            out.append(f"**API error:** `{r['error']}`\n")
        out.append("**Input:**\n\n" + fence(r["case"]["input"]) + "\n\n**Raw output (unedited):**\n\n" + fence(r["raw_output"]) + "\n")
        out.append("</details>\n")
    return "\n".join(out)


def section_sentiment(recs, analysis_hint) -> str:
    L = ["## 1. Zero-shot vs few-shot: sentiment classification\n",
         "**Task:** classify each review as `positive`, `negative`, `neutral` or `mixed`. Gold labels were written by me, so a few "
         "(sarcasm, mild negation) are debatable. The two prompts are identical except that few-shot adds 5 labelled examples.\n"]
    for v, t in SENTIMENT_VARIANTS.items():
        L.append(f"**Prompt template: `{v}`** (`{{input}}` is replaced by the review)\n\n" + fence(t) + "\n")
    L.append("**Scoring.** *Strict* = output is exactly one label word and it matches gold. *Lenient* = earliest label word "
             "mentioned in the output matches gold. *Consistent* = every run on the same input gave the same lenient label.\n")
    L.append("| Variant | Output is exactly one label | Strict accuracy | Lenient accuracy | Consistent across runs |\n|---|---|---|---|---|")
    for v in SENTIMENT_VARIANTS:
        rs = [r for r in recs if r["variant"] == v]
        if not rs: continue
        cons = 0; cases = {r["case_id"] for r in rs}
        for cid in cases:
            labs = {r["score"].get("lenient_label") for r in rs if r["case_id"] == cid}
            cons += (len(labs) == 1 and None not in labs)
        L.append(f"| {v} | {pct(sum(r['score']['format_ok'] for r in rs), len(rs))} | {pct(sum(r['score']['strict_correct'] for r in rs), len(rs))} "
                 f"| {pct(sum(r['score']['lenient_correct'] for r in rs), len(rs))} | {pct(cons, len(cases))} |")
    L.append("\n**Per-input outputs** (cells truncated; ✓ = strict-correct; complete text is in the raw section below)\n")
    L.append("| ID | Review | Gold | " + " | ".join(SENTIMENT_VARIANTS) + " |\n|---|---|---|" + "---|" * len(SENTIMENT_VARIANTS))
    for c in SENTIMENT_CASES:
        cols = []
        for v in SENTIMENT_VARIANTS:
            rs = sorted([r for r in recs if r["variant"] == v and r["case_id"] == c["id"]], key=lambda r: r["run"])
            cols.append(" / ".join(("✓ " if r["score"]["strict_correct"] else "✗ ") + cell(r["raw_output"], 34) for r in rs))
        L.append(f"| {c['id']} | {cell(c['input'], 60)} | {c['gold']} | " + " | ".join(cols) + " |")
    L.append("\n### Analysis (write this yourself)\n\n" + analysis_hint + "\n")
    L.append("### Complete raw outputs\n\n" + raw_blocks(recs, lambda r: "✓ strict-correct" if r["score"]["strict_correct"] else "✗ not strict-correct"))
    return "\n".join(L)


def section_cot(recs, analysis_hint) -> str:
    L = ["## 2. Chain-of-thought: multi-step reasoning\n",
         "**Task:** six multi-step word problems with known answers. Both prompts ask for the final answer on a `FINAL:` line so it can be checked automatically; "
         "the only difference is whether the model is told to show its working.\n"]
    for v, t in COT_VARIANTS.items():
        L.append(f"**Prompt template: `{v}`**\n\n" + fence(t) + "\n")
    L.append("**Problems and correct answers**\n")
    for c in COT_CASES:
        L.append(f"- **{c['id']}** (answer: `{c['expected']}`): {c['input']}")
    L.append("\n| Variant | Correct | Gave a FINAL line | Avg output length (chars) | Avg hidden thinking tokens |\n|---|---|---|---|---|")
    for v in COT_VARIANTS:
        rs = [r for r in recs if r["variant"] == v]
        if not rs: continue
        th = [r["thought_tokens"] for r in rs if r.get("thought_tokens") is not None]
        L.append(f"| {v} | {pct(sum(r['score']['correct'] for r in rs), len(rs))} | {pct(sum(r['score']['has_final'] for r in rs), len(rs))} "
                 f"| {sum(len(r['raw_output']) for r in rs) // len(rs)} | {(f'{sum(th) / len(th):.0f}' if th else 'not reported')} |")
    L.append("\n**Correct answers per problem** (out of the runs per variant)\n")
    L.append("| Problem | Expected | " + " | ".join(COT_VARIANTS) + " |\n|---|---|" + "---|" * len(COT_VARIANTS))
    for c in COT_CASES:
        cols = []
        for v in COT_VARIANTS:
            rs = [r for r in recs if r["variant"] == v and r["case_id"] == c["id"]]
            cols.append(f"{sum(r['score']['correct'] for r in rs)}/{len(rs)}  (" + ", ".join(cell(str(r['score'].get('extracted')), 14) for r in sorted(rs, key=lambda r: r['run'])) + ")")
        L.append(f"| {c['id']} | {c['expected']} | " + " | ".join(cols) + " |")
    L.append("\n### Analysis (write this yourself)\n\n" + analysis_hint + "\n")
    L.append("### Complete raw outputs\n\n" + raw_blocks(recs, lambda r: ("✓ correct" if r["score"]["correct"] else "✗ wrong") + f" (extracted: {cell(str(r['score'].get('extracted')), 20)})"))
    return "\n".join(L)


def section_json(recs, analysis_hint) -> str:
    L = ["## 3. Structured output: JSON extraction\n",
         "**Task:** extract `{name, date, amount, currency}` from messy text. Test inputs include a missing amount (J7, expected `null`), "
         "a distractor amount (J8), a dd/mm/yyyy date (J4) and a spelled-out date (J3).\n",
         "**Test inputs and gold answers**\n"]
    for c in JSON_CASES:
        L.append(f"- **{c['id']}**: {c['input']}\n  - gold: `{json.dumps(c['gold'], ensure_ascii=False)}`")
    L.append("\n**Prompt variants** (`{input}` is replaced by the text). Variant 4 uses the same text as variant 3 plus the API's JSON mode (`response_mime_type=application/json` with a response schema).\n")
    seen = set()
    for v, t in JSON_VARIANTS.items():
        note = " (same text as v3, plus API JSON mode with a response schema)" if v in JSON_MODE_VARIANTS else ""
        L.append(f"**`{v}`**{note}\n\n" + fence(t) + "\n")
    L.append("**Success levels.** *Strict parse* = the raw output is valid JSON exactly as returned. *Parse after cleanup* = valid after stripping markdown fences. "
             "*Schema OK* = exactly the 4 keys with the right types and `YYYY-MM-DD` date. *All values correct* = schema OK and every value equals the gold answer.\n")
    L.append("| Variant | Strict parse | Parse after cleanup | Schema OK | All values correct |\n|---|---|---|---|---|")
    for v in JSON_VARIANTS:
        rs = [r for r in recs if r["variant"] == v]
        if not rs: continue
        s = lambda k: sum(bool(r["score"].get(k)) for r in rs)
        L.append(f"| {v} | {pct(s('strict_parse'), len(rs))} | {pct(s('cleaned_parse'), len(rs))} | {pct(s('schema_ok'), len(rs))} | {pct(s('correct'), len(rs))} |")
    L.append("\n**Every failure, with the reason**\n")
    fails = [r for r in recs if not r["score"].get("correct")]
    if not fails:
        L.append("_No failures in this run._")
    for r in fails:
        L.append(f"- `{r['variant']}` · {r['case_id']} · run {r['run']}: " + "; ".join(r["score"].get("problems") or ["unknown"]))
    L.append("\n### Analysis (write this yourself)\n\n" + analysis_hint + "\n")
    L.append("### Complete raw outputs\n\n" + raw_blocks(recs, lambda r: "✓ all correct" if r["score"].get("correct") else "✗ failed"))
    return "\n".join(L)


HINT = ("> _TODO: 2-3 honest sentences. Compare the numbers in the table above, say what changed and why you think so, "
        "and say clearly where the technique did NOT help or made things worse. Do not claim anything the tables do not show._")


def build_report(out_dir: Path, dry: bool):
    meta = json.loads((out_dir / "meta.json").read_text()) if (out_dir / "meta.json").exists() else {}
    parts = []
    if dry:
        parts.append("> ⚠️ **DRY RUN: every output below is FAKE. Do not submit this file.**\n")
    parts.append("# Prompt Engineering Report: few-shot, chain-of-thought and structured output\n")
    parts.append("All prompts and outputs below were produced by `prompt_lab.py` and are shown exactly as the model returned them. "
                 "Per-call prompts are also stored in full in `results/*.jsonl`.\n")
    parts.append("| Setting | Value |\n|---|---|")
    parts.append(f"| Model | `{meta.get('model', MODEL)}` |\n| Temperature | {meta.get('temperature', TEMPERATURE)} |\n"
                 f"| Runs per input and variant | {meta.get('runs', RUNS)} |\n| Date | {meta.get('date', dt.date.today().isoformat())} |")
    tm = meta.get("thinking_mode")
    parts.append(f"| Hidden-thinking setting used for the chain-of-thought test | {('`' + tm + '`') if tm else 'not run'} (see the thinking-tokens column: if the direct prompt still shows thinking tokens, it reasoned internally) |\n")
    for exp, fn in (("sentiment", section_sentiment), ("cot", section_cot), ("json", section_json)):
        recs = load(out_dir, exp)
        if recs:
            parts.append(fn(recs, HINT))
    parts.append("## 4. Overall conclusions (write this yourself)\n\n> _TODO: which technique gave the biggest gain, which gave the least, and what you would do differently._\n")
    (out_dir.parent / ("REPORT_DRY_RUN.md" if dry else "REPORT.md")).write_text("\n".join(parts), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["sentiment", "cot", "json"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    root = Path(__file__).resolve().parent
    out_dir = root / ("dry_run_results" if a.dry_run else "results")
    out_dir.mkdir(exist_ok=True)

    if not a.report_only:
        caller = DryRunCaller() if a.dry_run else GeminiCaller()
        todo = [a.only] if a.only else ["sentiment", "cot", "json"]
        if "sentiment" in todo:
            run_grid("sentiment", SENTIMENT_VARIANTS, SENTIMENT_CASES, score_sentiment, caller, out_dir, dry=a.dry_run)
        if "cot" in todo:
            run_grid("cot", COT_VARIANTS, COT_CASES, score_cot, caller, out_dir, disable_thinking=True, dry=a.dry_run)
        if "json" in todo:
            run_grid("json", JSON_VARIANTS, JSON_CASES, score_json, caller, out_dir, json_variants=JSON_MODE_VARIANTS, dry=a.dry_run)
        meta_path = out_dir / "meta.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        meta.update({"model": MODEL, "temperature": TEMPERATURE, "runs": RUNS, "date": dt.date.today().isoformat()})
        if "cot" in todo:
            meta["thinking_mode"] = caller.thinking_mode
        meta_path.write_text(json.dumps(meta, indent=2))
    build_report(out_dir, a.dry_run)
    print("Done. Report written to", "REPORT_DRY_RUN.md" if a.dry_run else "REPORT.md")


if __name__ == "__main__":
    main()