"""
Layer-2 structural checks — the relevance guard.

The citation guard (scripts/verify_citations.py) proves PROVENANCE: the quoted
text really exists in the document it claims to come from. It says nothing about
RELEVANCE: whether that authentic text bears on this criterion for this request.

Hero case PA-2026-115003 is the failure that distinction names. The quote was
real, verbatim, correctly page-cited — and described therapy for a knee
replacement in a case about a lumbar complaint. Provenance passed. Relevance was
never checked, because nothing checked it.

These are the deterministic checks that do. They run before the model's output
reaches a reviewer, and they are boring on purpose: a body region is a join, not
a judgment, and there is no reason to ask a language model to be careful about
something a lookup can settle.

Rule 4 of the extraction prompt already instructs the model to check this. The
prompt's own design notes record that it does not reliably work, which is the
argument for enforcing it outside the model rather than inside it.
"""

import re

DURATION_THRESHOLD_DAYS = 28  # "at least four weeks", LCD L34220 criterion C2

# ICD-10 prefix → body region. Small on purpose: this is the lumbar-MRI wedge,
# not a general anatomical ontology. Expanding to a new service line means
# extending this table, which is a data change rather than a code change.
ICD10_REGION = {
    "M54.5": "lumbar", "M54.4": "lumbar", "M51.": "lumbar", "M48.0": "lumbar",
    "M43.1": "lumbar", "M47.8": "lumbar", "S33.": "lumbar",
    "M75.": "shoulder", "S43.": "shoulder",
    "M17.": "knee", "Z96.65": "knee", "S83.": "knee",
    "M16.": "hip", "Z96.64": "hip",
    "M25.5": "unspecified_joint",
}

REGION_KEYWORDS = {
    "lumbar": ["lumbar", "low back", "lumbosacral", "lbp"],
    "shoulder": ["shoulder", "rotator cuff", "glenohumeral"],
    "knee": ["knee", "patell", "arthroplasty of the knee", "tkа", "tka"],
    "hip": ["hip", "acetabul"],
    "cervical": ["cervical", "neck"],
}

ICD10_PATTERN = re.compile(r"\b([A-TV-Z][0-9][0-9AB](?:\.[0-9A-TV-Z]{1,4})?)\b")
MEMBER_ID_PATTERN = re.compile(r"\b[Hh]\d{7,10}\b")


def region_from_codes(text):
    """Return the first body region implied by an ICD-10 code in the text."""
    for code in ICD10_PATTERN.findall(text):
        for prefix, region in ICD10_REGION.items():
            if code.startswith(prefix):
                return region, code
    return None, None


def region_from_keywords(text):
    """Fall back to anatomical vocabulary when no code is present."""
    lowered = text.lower()
    hits = {r for r, words in REGION_KEYWORDS.items() if any(w in lowered for w in words)}
    # Only decisive when the document points at exactly one region.
    return (hits.pop(), "keyword") if len(hits) == 1 else (None, None)


def document_text(probe, document_id):
    for doc in probe["documents"]:
        if doc["id"] == document_id:
            return "\n".join(s["text"] for s in doc["sections"])
    return ""


def page_text(probe, document_id, page):
    for doc in probe["documents"]:
        if doc["id"] == document_id:
            for section in doc["sections"]:
                if section["page"] == page:
                    return section["text"]
    return ""


# --- the checks -------------------------------------------------------------

def check_body_region(probe, finding):
    """Does the cited evidence concern the same body region as the request?

    Looks at the whole cited DOCUMENT rather than the single page: a therapy
    discharge summary carries its treating diagnosis on its header page, while
    the clinical language a reader latches onto sits further in.
    """
    requested = probe["request"].get("bodyRegion")
    if not requested:
        return None

    claims_region = probe["claimsLayer"].get("evidenceRegion")
    text = document_text(probe, finding["documentId"])
    doc_region, evidence = region_from_codes(text)
    if doc_region is None:
        doc_region, evidence = region_from_keywords(text)

    observed = doc_region or claims_region
    if observed and observed != requested:
        src = f"code {evidence}" if evidence and evidence != "keyword" else "anatomical terms"
        return ("body_region_mismatch",
                f"request is {requested}; cited document indicates {observed} ({src})")
    return None


def check_member_identity(probe, finding):
    """Is the cited page actually this member's record?

    Misfiled pages inside a faxed bundle are routine. The citation guard cannot
    see this at all — the page really is in the bundle, so the quote verifies.
    """
    member_id = probe["request"].get("memberId")
    if not member_id:
        return None  # in production the request always carries identity

    text = page_text(probe, finding["documentId"], finding["page"])
    ids_on_page = set(MEMBER_ID_PATTERN.findall(text))
    foreign = {i for i in ids_on_page if i.upper() != member_id.upper()}
    if foreign:
        return ("member_identity_mismatch",
                f"cited page carries member id {sorted(foreign)[0]}, request is {member_id}")
    return None


def check_duration(probe, finding):
    """Does the ledger affirmatively show a trial shorter than the criterion requires?

    Fires ONLY when claims found records and their span is under threshold.

    It must not fire on the absence of claims. Out-of-network, cash-pay and
    self-directed conservative management are invisible to the ledger, so
    treating 'no claims found' as 'no therapy happened' would suppress findings
    for exactly the population this product exists to protect. Absence of
    evidence is the normal case here, not a red flag.
    """
    claims = probe["claimsLayer"]
    if not claims.get("recordsFound"):
        return None
    span = claims.get("observedSpanDays")
    if span is not None and span < DURATION_THRESHOLD_DAYS:
        return ("duration_below_threshold",
                f"ledger shows a {span}-day episode against a "
                f"{DURATION_THRESHOLD_DAYS}-day requirement")
    return None


CHECKS = (check_body_region, check_member_identity, check_duration)


def evaluate_finding(probe, finding):
    """Return a list of (check_name, reason) for every check this finding trips."""
    return [r for r in (check(probe, finding) for check in CHECKS) if r is not None]


def demo():
    import json
    probes = {p["id"]: p for p in json.load(open("data/eval-set.json"))["probes"]}
    outputs = json.load(open("data/eval-outputs.json"))["byProbe"]

    print("STRUCTURAL CHECKS — relevance guard\n" + "=" * 68)
    for probe_id, result in outputs.items():
        probe = probes[probe_id]
        for finding in result.get("findings", []):
            trips = evaluate_finding(probe, finding)
            verdict = "DEMOTE " if trips else "PASS   "
            print(f"[{verdict}] {probe_id:<7} {probe['slice']}")
            for name, reason in trips:
                print(f"           └─ {name}: {reason}")
    print("=" * 68)
    print("A demoted finding does not appear as supporting evidence. It is not")
    print("deleted — it moves to a 'needs judgment' tier with its reason attached,")
    print("because a suppressed finding a reviewer cannot see is its own failure mode.")


if __name__ == "__main__":
    demo()
