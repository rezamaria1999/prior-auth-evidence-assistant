"""
Citation verification — the hallucination guard.

Every model finding must quote text that provably exists in the source document.
This checks each quotation by exact string containment against the document it
claims to come from. No model is involved. A finding whose quote does not match
is DISCARDED before it can reach a reviewer.

This is deliberately boring code. That is the point: the safety property is
enforced by string equality, not by trusting the model to be honest.

Run:  python3 scripts/verify_citations.py
"""

import json
import sys


def load_sources(hero_path):
    """Flatten every case's documents into {case_id: {doc_id: {page: text}}}."""
    data = json.load(open(hero_path))
    sources = {}
    for case in data["cases"]:
        docs = {}
        for doc in case["documents"]:
            pages = {}
            if "content" in doc:
                pages[1] = doc["content"]
            for section in doc.get("sections", []):
                pages[section["page"]] = section["text"]
            docs[doc["id"]] = pages
        sources[case["id"]] = docs
    return sources


def verify(finding, sources, case_id):
    """Return (passed, reason)."""
    doc_id, page, quote = finding["documentId"], finding["page"], finding["quote"]

    if case_id not in sources:
        return False, f"unknown case {case_id}"
    if doc_id not in sources[case_id]:
        return False, f"document {doc_id} not in case"
    if page not in sources[case_id][doc_id]:
        return False, f"{doc_id} has no page {page}"

    source_text = sources[case_id][doc_id][page]
    if quote in source_text:
        return True, "exact match"

    # Diagnose the failure so it is actionable rather than mysterious.
    norm_q = " ".join(quote.split())
    norm_s = " ".join(source_text.split())
    if norm_q in norm_s:
        return False, "matches only after whitespace normalisation — quote drifted"
    head = norm_q[:40]
    if head in norm_s:
        return False, f"opening matches but quote diverges after: '{head}...'"
    return False, "no match — quotation not present in source"


def main():
    sources = load_sources("data/cases-hero.json")
    outputs = json.load(open("data/model-outputs.json"))

    total = passed = discarded = 0
    print("CITATION VERIFICATION\n" + "=" * 62)

    for case_id, result in outputs["byCase"].items():
        findings = result.get("findings", [])
        print(f"\n{case_id}  ({result['demoRole']})")
        if not findings:
            stmt = result.get("noFindingStatement", "")
            expected = ("No supporting evidence identified in the submitted record. "
                        "This is not a coverage recommendation.")
            ok = stmt == expected
            print(f"  no findings — empty-state wording {'OK' if ok else 'WRONG'}")
            if not ok:
                print(f"    expected: {expected}")
                print(f"    got:      {stmt}")
            continue

        kept = []
        for f in findings:
            total += 1
            ok, reason = verify(f, sources, case_id)
            mark = "PASS" if ok else "DISCARD"
            print(f"  [{mark}] {f['documentId']} p{f['page']} — {reason}")
            print(f"          \"{f['quote'][:72]}{'...' if len(f['quote']) > 72 else ''}\"")
            if ok:
                passed += 1
                kept.append(f)
            else:
                discarded += 1
        result["verifiedFindings"] = kept

    print("\n" + "=" * 62)
    print(f"{total} quotations checked · {passed} passed · {discarded} discarded")

    if discarded:
        print("\nDiscarded findings never reach a reviewer.")
        return 1
    print("\nAll citations trace to text that provably exists in the source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
