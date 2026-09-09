"""
Bundles the JSON data into a single self-contained index.html.

Why a build step at all: the data lives in JSON so it stays readable and
editable, but the demo has to be a single file you can double-click. This
inlines the former into the latter.

Run:  python3 build.py
Then: open index.html
"""

import json
from pathlib import Path

ROOT = Path(__file__).parent


def load():
    hero = json.load(open(ROOT / "data/cases-hero.json"))
    queue = json.load(open(ROOT / "data/cases-queue.json"))
    criteria = json.load(open(ROOT / "data/criteria.json"))
    outputs = json.load(open(ROOT / "data/model-outputs.json"))

    # Hero cases carry full documents. Queue cases carry summaries only.
    hero_ids = {c["id"] for c in hero["cases"]}
    queue_cases = [c for c in queue["cases"] if c["id"] not in hero_ids]

    return {
        "heroCases": hero["cases"],
        "queueCases": queue_cases,
        "criteria": criteria,
        "modelOutputs": outputs["byCase"],
        "designPrinciples": hero.get("_designPrinciples", []),
        "calibration": queue.get("calibration", {}),
        "modelPerformance": queue.get("modelPerformance", {}),
    }


def main():
    data = load()
    shell = (ROOT / "src/shell.html").read_text()
    payload = json.dumps(data, indent=None, separators=(",", ":"))
    html = shell.replace("/*__DATA__*/null", payload)
    (ROOT / "index.html").write_text(html)

    n_pending = sum(
        1 for c in data["queueCases"]
        if c["review"]["status"] == "pending_medical_director"
    ) + len(data["heroCases"])

    print(f"built index.html  ({len(html):,} bytes)")
    print(f"  hero cases (full documents): {len(data['heroCases'])}")
    print(f"  queue cases (summaries):     {len(data['queueCases'])}")
    print(f"  pending MD review:           {n_pending}")
    print("\nopen index.html in a browser")


if __name__ == "__main__":
    main()
