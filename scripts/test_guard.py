"""
Negative test for the citation guard.

A guard that always passes is not a guard. This injects three fabricated or
drifted quotations and confirms each is discarded, so the safety property is
demonstrated rather than asserted.

Run:  python3 scripts/test_guard.py
"""
import json, sys
sys.path.insert(0, "scripts")
from verify_citations import load_sources, verify

sources = load_sources("data/cases-hero.json")
CASE = "PA-2026-114872"

cases = [
    ("fabricated quotation (plausible but never written)", {
        "documentId": "DOC-3", "page": 9,
        "quote": "The patient failed twelve weeks of aggressive conservative therapy including epidural injections."}),
    ("real sentence, wrong page", {
        "documentId": "DOC-3", "page": 4,
        "quote": "GOALS: 0 of 3 functional goals met."}),
    ("drifted quote — model tidied the wording", {
        "documentId": "DOC-3", "page": 9,
        "quote": "Patient completed a 6 week course of skilled physical therapy without meaningful improvement."}),
    ("genuine quotation (control — must pass)", {
        "documentId": "DOC-3", "page": 9,
        "quote": "GOALS: 0 of 3 functional goals met."}),
]

print("CITATION GUARD — NEGATIVE TEST\n" + "="*62)
failures = 0
for label, finding in cases:
    ok, reason = verify(finding, sources, CASE)
    should_pass = label.startswith("genuine")
    correct = (ok == should_pass)
    if not correct: failures += 1
    print(f"\n{label}")
    print(f"  quote:  \"{finding['quote'][:64]}{'...' if len(finding['quote'])>64 else ''}\"")
    print(f"  result: {'PASS' if ok else 'DISCARD'} — {reason}")
    print(f"  {'correct' if correct else 'GUARD FAILED'}")

print("\n" + "="*62)
print("guard behaved correctly on all 4 probes" if not failures
      else f"{failures} probe(s) mishandled — guard is not sound")
sys.exit(1 if failures else 0)
