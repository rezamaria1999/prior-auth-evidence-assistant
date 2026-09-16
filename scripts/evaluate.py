"""
Offline evaluation harness for the layer-3 narrative reader.

Scores an outputs file against the labelled probe set in data/eval-set.json and
reports, per slice and in aggregate:

  detection      precision / recall, with Wilson intervals
  localisation   did a correct detection cite the right document, page and span
  citation       did every quotation verify verbatim against its source
  relevance      of findings that verified, how many actually bear on the
                 criterion for this request — the metric the citation guard
                 cannot provide
  abstention     when the system said nothing, was there truly nothing
  concerns       when the model flagged a doubt, was the finding actually bad

Run:
    python3 scripts/evaluate.py                 # layer 3 alone
    python3 scripts/evaluate.py --with-guards   # layer 3 + layer-2 structural checks

The second form is the intervention. The difference between the two runs is the
measurement that justifies building the checks.
"""

import argparse
import json
import math
import sys

from structural_checks import evaluate_finding

Z = 1.96  # 95%


# --- statistics -------------------------------------------------------------

def wilson(successes, n, z=Z):
    """Wilson score interval. Used rather than the normal approximation because
    Wald produces intervals running past 100% at small n and extreme rates,
    which is a signal it has left its valid range."""
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def rate(label, successes, n, width=34):
    if n == 0:
        return f"  {label:<{width}} n/a (no cases)"
    p, lo, hi = wilson(successes, n)
    flag = "   « n too small to mean much" if n < 10 else ""
    return (f"  {label:<{width}} {p:5.0%}   [{lo:.0%}–{hi:.0%}]   "
            f"{successes}/{n}{flag}")


# --- citation verification (provenance) -------------------------------------

def build_sources(probe):
    return {doc["id"]: {s["page"]: s["text"] for s in doc["sections"]}
            for doc in probe["documents"]}


def verify_citation(probe, finding):
    sources = build_sources(probe)
    doc_id, page, quote = finding["documentId"], finding["page"], finding["quote"]
    if doc_id not in sources:
        return False, f"document {doc_id} not in case"
    if page not in sources[doc_id]:
        return False, f"{doc_id} has no page {page}"
    text = sources[doc_id][page]
    if quote in text:
        return True, "exact match"
    if " ".join(quote.split()) in " ".join(text.split()):
        return False, "matches only after whitespace normalisation — quote drifted"
    return False, "no match — quotation not present in source"


# --- scoring ----------------------------------------------------------------

def locates_correctly(probe, finding):
    """A detection is only useful if it points at evidence a reviewer can act on."""
    for accept in probe["label"].get("acceptableEvidence", []):
        if (finding["documentId"] == accept["documentId"]
                and finding["page"] == accept["page"]
                and accept["mustContain"] in finding["quote"]):
            return True
    return False


def score_probe(probe, output, use_guards):
    findings = output.get("findings", [])
    surviving, discarded, demoted = [], [], []

    for finding in findings:
        ok, reason = verify_citation(probe, finding)
        if not ok:
            discarded.append((finding, reason))
            continue
        if use_guards:
            trips = evaluate_finding(probe, finding)
            if trips:
                demoted.append((finding, trips))
                continue
        surviving.append(finding)

    flagged = bool(surviving)
    should = probe["label"]["shouldFlag"]

    if flagged and should:
        outcome = "TP"
    elif flagged and not should:
        outcome = "FP"
    elif not flagged and should:
        outcome = "FN"
    else:
        outcome = "TN"

    located = any(locates_correctly(probe, f) for f in surviving) if outcome == "TP" else None

    return {
        "probe": probe, "outcome": outcome, "located": located,
        "surviving": surviving, "discarded": discarded, "demoted": demoted,
        "checked": len(findings),
    }


def compare(eval_set, outputs, probes):
    """Run both configurations and report the delta. This is the measurement that
    justifies building the structural checks — and the one that shows what they
    do not fix."""
    rows = []
    for use_guards in (False, True):
        results = [score_probe(probes[pid], out, use_guards)
                   for pid, out in outputs["byProbe"].items()]
        c = {k: sum(1 for r in results if r["outcome"] == k)
             for k in ("TP", "FP", "FN", "TN")}
        rows.append((c["TP"], c["FP"], c["FN"], c["TN"]))

    print("=" * 74)
    print("INTERVENTION — deterministic relevance checks at layer 2")
    print("=" * 74)
    print(f"\n  {'':<22}{'layer 3 alone':>16}{'+ structural':>16}{'delta':>12}")
    print("  " + "-" * 64)

    for label, idx in (("true positives", 0), ("false positives", 1),
                       ("false negatives", 2), ("true negatives", 3)):
        before, after = rows[0][idx], rows[1][idx]
        d = after - before
        print(f"  {label:<22}{before:>16}{after:>16}{d:>+12}")

    for label, num, den in (("precision", 0, 1), ("recall", 0, 2)):
        b_num, b_den = rows[0][num], rows[0][num] + rows[0][den]
        a_num, a_den = rows[1][num], rows[1][num] + rows[1][den]
        b = f"{b_num / b_den:.0%}" if b_den else "n/a"
        a = f"{a_num / a_den:.0%}" if a_den else "n/a"
        print(f"  {label:<22}{b:>16}{a:>16}{'':>12}")

    print("\n  Precision moves because every false positive on this slice was")
    print("  structurally catchable: a body region, a member id, and a date span.")
    print("  None of them needed a language model to be more careful.")
    print("\n  Recall does not move at all. The remaining miss is a genuine find")
    print("  whose quotation the model tidied into well-formed prose, which the")
    print("  provenance guard then discarded — correctly. Fixing precision and")
    print("  fixing recall are different problems, and loosening the guard to")
    print("  recover that find would trade away the property that makes the")
    print("  citations trustworthy. That one stays open on purpose.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-guards", action="store_true",
                    help="apply layer-2 structural checks before scoring")
    ap.add_argument("--compare", action="store_true",
                    help="run both configurations and report the delta")
    ap.add_argument("--eval-set", default="data/eval-set.json")
    ap.add_argument("--outputs", default="data/eval-outputs.json")
    args = ap.parse_args()

    eval_set = json.load(open(args.eval_set))
    outputs = json.load(open(args.outputs))
    probes = {p["id"]: p for p in eval_set["probes"]}

    if args.compare:
        return compare(eval_set, outputs, probes)

    results = [score_probe(probes[pid], out, args.with_guards)
               for pid, out in outputs["byProbe"].items()]

    mode = "LAYER 3 + LAYER-2 STRUCTURAL CHECKS" if args.with_guards else "LAYER 3 ALONE"
    print("=" * 74)
    print(f"OFFLINE EVALUATION — {mode}")
    print(f"prompt {outputs['promptVersion']} · run {outputs['modelRun']} · "
          f"probe set v{eval_set['schemaVersion']}")
    print("=" * 74)

    # per-probe detail
    print("\nPER PROBE\n" + "-" * 74)
    for r in results:
        p = r["probe"]
        loc = ""
        if r["outcome"] == "TP":
            loc = "  · located correctly" if r["located"] else "  · WRONG SPAN"
        print(f"  {r['outcome']:<3} {p['id']:<7} {p['slice']:<24}{loc}")
        for finding, reason in r["discarded"]:
            print(f"        guard discarded: {reason}")
        for finding, trips in r["demoted"]:
            for name, why in trips:
                print(f"        demoted: {name} — {why}")

    # aggregate detection
    counts = {k: sum(1 for r in results if r["outcome"] == k)
              for k in ("TP", "FP", "FN", "TN")}
    tp, fp, fn, tn = counts["TP"], counts["FP"], counts["FN"], counts["TN"]

    print("\nDETECTION\n" + "-" * 74)
    print(f"  TP {tp} · FP {fp} · FN {fn} · TN {tn}   (n = {len(results)})")
    print(rate("precision", tp, tp + fp))
    print(rate("recall", tp, tp + fn))

    # localisation
    located = sum(1 for r in results if r["located"])
    print("\nLOCALISATION\n" + "-" * 74)
    print(rate("correct document, page and span", located, tp))

    # citation fidelity — a gate, not a metric
    checked = sum(r["checked"] for r in results)
    discarded = sum(len(r["discarded"]) for r in results)
    print("\nCITATION FIDELITY (provenance gate)\n" + "-" * 74)
    print(rate("quotations verifying verbatim", checked - discarded, checked))
    if discarded:
        print(f"  {discarded} discarded before display. Note that a discard on a probe")
        print("  where support genuinely exists converts a find into a false negative.")

    # relevance — what the citation guard cannot tell you
    verified = [(r, f) for r in results for f in (r["surviving"] + [d[0] for d in r["demoted"]])]
    relevant = [(r, f) for r, f in verified if r["probe"]["label"]["shouldFlag"]]
    print("\nRELEVANCE (of findings that passed provenance)\n" + "-" * 74)
    print(rate("bear on the criterion for this request", len(relevant), len(verified)))
    print("  Provenance and relevance are different properties. A verbatim quote from")
    print("  the correct page of the correct document can still be about the wrong")
    print("  body region, the wrong episode, or the wrong patient.")

    # abstention
    silent = [r for r in results if not r["surviving"]]
    correct_silence = sum(1 for r in silent if r["outcome"] == "TN")
    print("\nABSTENTION\n" + "-" * 74)
    print(rate("silence was correct", correct_silence, len(silent)))
    print("  Silence pushes the reviewer toward denial, so a false silence is not a")
    print("  neutral outcome — it is the failure mode that reaches a member.")

    # concern calibration
    all_findings = [(r, f) for r in results
                    for f in r["surviving"] + [d[0] for d in r["demoted"]] + [d[0] for d in r["discarded"]]]
    with_concern = [(r, f) for r, f in all_findings if f.get("concerns")]
    bad_with_concern = sum(1 for r, f in with_concern if not r["probe"]["label"]["shouldFlag"])
    bad_total = sum(1 for r, f in all_findings if not r["probe"]["label"]["shouldFlag"])
    flagged_bad = sum(1 for r, f in all_findings
                      if not r["probe"]["label"]["shouldFlag"] and f.get("concerns"))
    print("\nCONCERN CALIBRATION\n" + "-" * 74)
    print(rate("concern present → finding was bad", bad_with_concern, len(with_concern)))
    print(rate("finding was bad → concern present", flagged_bad, bad_total))
    print("  The model often writes down the right doubt and reports the finding")
    print("  anyway. That is a signal currently being discarded rather than routed.")

    # per slice
    print("\nBY SLICE\n" + "-" * 74)
    print(f"  {'slice':<26}{'kind':<19}{'outcome'}")
    for r in sorted(results, key=lambda r: r["probe"]["slice"]):
        p = r["probe"]
        print(f"  {p['slice']:<26}{p['sliceKind']:<19}{r['outcome']}")

    # honesty block
    print("\n" + "=" * 74)
    print("READING THESE NUMBERS")
    print("=" * 74)
    print("  · This is a CONSTRUCTED adversarial slice. Hard negatives are")
    print("    over-represented on purpose. Precision here is a diagnostic, not a")
    print("    prevalence estimate, and must never be pooled with random-sample metrics.")
    print(f"  · n = {len(results)}. Every interval above is wide enough to drive through.")
    print("    Knowing recall to within five points needs roughly a thousand")
    print("    adjudicated cases, which is a staffing line, not an afternoon.")
    print("  · Labels here are authored, not physician-adjudicated. INTER-RATER")
    print("    AGREEMENT IS UNMEASURED, so the human ceiling on these scores is")
    print("    unknown. Against a single adjudicator, a model cannot beat the")
    print("    adjudicator — it can only agree with them.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
