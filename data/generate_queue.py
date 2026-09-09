"""
Generates the supporting queue cases (beyond the three hero cases).

Design decisions worth being able to defend in the room:

1. FLAG RATE IS CALIBRATED, NOT ARBITRARY.
   HHS OIG (April 2022) found that 13% of denied Medicare Advantage prior
   authorization requests actually met Medicare coverage rules. The synthetic
   population here carries a true "findable support exists" rate of ~18%,
   slightly above OIG's figure so the demo is legible without being fantasy.

2. THE MODEL IS NOT PERFECT, ON PURPOSE.
   The set includes one false positive (therapy records from an unrelated
   episode) and one false negative (evidence in a poorly legible scanned
   note). Resulting precision and recall land at 80% / 80%. A demo that
   shows 100% is a demo nobody believes.

3. SUBGROUP ATTRIBUTES ARE DELIBERATELY CORRELATED.
   Language and prior-appeal history covary the way they do in reality, so
   the oversight screen can actually detect whether the model behaves
   differently for members least likely to appeal. That is the bias question
   made measurable rather than asserted.

Denominator note: this queue is cases already routed for medical director
review — i.e. heading toward denial. It is not all prior authorization
requests. That is why the flag rate is far higher than it would be against
total PA volume.
"""

import json
import random

random.seed(11)

FIRST_F = ["Eleanor", "Gloria", "Patricia", "Yolanda", "Ruth", "Anita", "Barbara",
           "Josephine", "Carmen", "Doris", "Linh", "Marguerite", "Estelle", "Wanda"]
FIRST_M = ["Harold", "Walter", "Ernest", "Raymond", "Stanley", "Clarence",
           "Desmond", "Arturo", "Leonard", "Hyun", "Gerald", "Vernon", "Otis"]
LAST = ["Okafor", "Delgado", "Brennan", "Nakamura", "Whitfield", "Sandoval",
        "Petrov", "Abernathy", "Castellanos", "Mbeki", "Lindqvist", "Rahman",
        "Duval", "Kowalski", "Ferraro", "Aluko", "Sorensen", "Vargas",
        "Ibarra", "Thistlewood", "Achebe", "Moreau"]

PROVIDERS = [
    ("Aaron Whitfield, MD", "Family Medicine", "Northgate Family Health"),
    ("Priya Raghunathan, MD", "Internal Medicine", "Lakeshore Internal Medicine"),
    ("Daniel Restrepo, MD", "Family Medicine", "Riverbend Community Health"),
    ("Susan Yeoh, DO", "Physical Medicine & Rehab", "Cascade Spine Institute"),
    ("Marcus Bell, MD", "Orthopedic Surgery", "Cascade Valley Orthopedics"),
    ("Ingrid Halvorsen, MD", "Neurology", "Summit Neurology Associates"),
]

# scenario -> (count, criteria_met, correct_action, should_flag, model_flags, note)
COMPOSITION = {
    # --- Support exists and is findable. Model should flag. ---
    "buried_pt_outside_records": (
        3, True, "approve", True, True,
        "Therapy discharge summary present in unitemized outside-records packet; "
        "referring note references prior treatment without dates or duration."),
    "buried_nsaid_trial": (
        1, True, "approve", True, True,
        "Medication list documents an NSAID trial exceeding four weeks with documented "
        "non-response; not carried into the clinical narrative."),

    # --- Support exists but the model misses it. FALSE NEGATIVE. ---
    "missed_buried_evidence": (
        1, True, "approve", True, False,
        "Conservative management documented in a handwritten scanned note of poor "
        "legibility within the outside packet."),

    # --- Model flags but should not. FALSE POSITIVE. ---
    "distractor_wrong_context": (
        1, False, "deny", False, True,
        "Therapy records present but directed at a different body region and a "
        "separate episode of care."),

    # --- Correct denials. Model correctly silent. ---
    "genuinely_no_conservative": (
        8, False, "deny", False, False,
        "Symptom onset under four weeks. No conservative management attempted or "
        "documented. Imaging requested prior to any trial of therapy."),
    "duplicative_imaging": (
        6, False, "deny", False, False,
        "Prior lumbar MRI within 90 days. No documented interval change in symptoms "
        "or examination (C3)."),
    "uncomplicated_ddd": (
        5, False, "deny", False, False,
        "Known degenerative disc disease, clinically stable, no surgical or "
        "interventional decision pending (C4)."),

    # --- Clear approvals. Never reach the MD queue, but sit in the denominator. ---
    "conservative_mgmt_in_chart": (
        4, True, "approve", False, False,
        "Six-week PT course documented directly in the referring physician note with "
        "dates and outcome. C2 satisfied on the face of the submission."),
    "red_flag_documented": (
        2, True, "approve", False, False,
        "History of malignancy documented in the referring note. Red-flag indication "
        "present; the conservative management requirement does not apply (C1)."),
}


def make_case(seq, scenario, spec):
    _, criteria_met, correct_action, should_flag, model_flags, note = spec

    sex = random.choice(["F", "M"])
    name = f"{random.choice(FIRST_F if sex == 'F' else FIRST_M)} {random.choice(LAST)}"
    provider, specialty, facility = random.choice(PROVIDERS)

    language = random.choices(
        ["English", "Spanish", "Vietnamese", "Mandarin", "Russian", "Korean"],
        weights=[78, 11, 4, 3, 2, 2],
    )[0]
    # Members with limited English proficiency appeal at markedly lower rates.
    if language == "English":
        prior_appeals = random.choices([0, 1, 2], weights=[84, 13, 3])[0]
    else:
        prior_appeals = random.choices([0, 1], weights=[97, 3])[0]

    reaches_md = correct_action == "deny" or should_flag

    return {
        "id": f"PA-2026-{115200 + seq * 7}",
        "scenario": scenario,
        "member": {
            "name": name,
            "age": random.randint(66, 89),
            "sex": sex,
            "memberId": f"H{random.randint(700000000, 999999999)}",
            "plan": random.choice(["Medicare Advantage HMO", "Medicare Advantage PPO"]),
            "language": language,
            "priorAppeals": prior_appeals,
        },
        "request": {
            "cpt": random.choice(["72148", "72149", "72158"]),
            "description": "MRI lumbar spine",
            "icd10": random.choice([
                {"code": "M54.50", "description": "Low back pain, unspecified"},
                {"code": "M54.16", "description": "Radiculopathy, lumbar region"},
                {"code": "M51.36", "description": "Other intervertebral disc degeneration, lumbar region"},
                {"code": "M48.061", "description": "Spinal stenosis, lumbar region without neurogenic claudication"},
            ]),
            "requestingProvider": provider,
            "specialty": specialty,
            "facility": facility,
            "submittedDate": f"2026-08-{random.randint(20, 31):02d}",
            "urgency": random.choices(["standard", "expedited"], weights=[88, 12])[0],
        },
        "review": {
            "status": "pending_medical_director" if reaches_md else "nurse_approved",
            "nurseReviewer": random.choice(["K. Osei, RN", "M. Tran, RN", "D. Whitlock, RN"]),
            "nurseNote": note,
            "proposedAction": "deny" if reaches_md else "approve",
        },
        "documentBundle": {
            "documentCount": random.randint(2, 6),
            "totalPages": random.randint(3, 41),
            "hasUnitemizedOutsideRecords": scenario.startswith("buried")
            or scenario in ("distractor_wrong_context", "missed_buried_evidence"),
        },
        "groundTruth": {
            "criteriaMet": criteria_met,
            "correctAction": correct_action,
            "shouldFlag": should_flag,
        },
        "modelBehavior": {"flags": model_flags},
    }


def confusion(cases):
    tp = sum(c["groundTruth"]["shouldFlag"] and c["modelBehavior"]["flags"] for c in cases)
    fp = sum((not c["groundTruth"]["shouldFlag"]) and c["modelBehavior"]["flags"] for c in cases)
    fn = sum(c["groundTruth"]["shouldFlag"] and (not c["modelBehavior"]["flags"]) for c in cases)
    tn = sum((not c["groundTruth"]["shouldFlag"]) and (not c["modelBehavior"]["flags"]) for c in cases)
    return tp, fp, fn, tn


def main():
    cases, seq = [], 0
    for scenario, spec in COMPOSITION.items():
        for _ in range(spec[0]):
            cases.append(make_case(seq, scenario, spec))
            seq += 1
    random.shuffle(cases)

    # The hero case that contains findable support counts toward the totals too.
    tp, fp, fn, tn = confusion(cases)
    tp += 1  # PA-2026-114872, Margaret Ellison
    total = len(cases) + 3  # + three hero cases

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)

    out = {
        "_note": "Synthetic queue cases supporting the three hero cases in cases-hero.json. "
                 "Composition is fixed and documented in generate_queue.py, not randomly drawn, "
                 "so the flag rate and the model's error profile are both defensible.",
        "calibration": {
            "anchor": "HHS OIG, April 2022: 13% of denied MA prior authorization requests met Medicare coverage rules.",
            "anchorUrl": "https://oig.hhs.gov/reports/all/2022/some-medicare-advantage-organization-denials-of-prior-authorization-requests-raise-concerns-about-beneficiary-access-to-medically-necessary-care/",
            "trueSupportRate": round((tp + fn) / total, 3),
        },
        "modelPerformance": {
            "truePositives": tp, "falsePositives": fp,
            "falseNegatives": fn, "trueNegatives": tn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "note": "Deliberately imperfect. One false positive (unrelated therapy episode) "
                    "and one false negative (illegible scanned note).",
        },
        "totals": {"queueCases": len(cases), "heroCases": 3, "total": total},
        "cases": cases,
    }
    with open("data/cases-queue.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"generated {len(cases)} queue cases (+3 hero = {total} total)")
    print(f"true support rate: {(tp+fn)/total:.1%}  (OIG anchor: 13%)")
    print(f"confusion: TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"precision: {precision:.0%}   recall: {recall:.0%}")

    langs = {}
    for c in cases:
        langs[c["member"]["language"]] = langs.get(c["member"]["language"], 0) + 1
    print("\nlanguage mix:", ", ".join(f"{k} {v}" for k, v in sorted(langs.items(), key=lambda x: -x[1])))

    lep = [c for c in cases if c["member"]["language"] != "English"]
    eng = [c for c in cases if c["member"]["language"] == "English"]
    print(f"prior-appeal rate — English: {sum(c['member']['priorAppeals'] > 0 for c in eng)/max(len(eng),1):.0%}"
          f"   limited English: {sum(c['member']['priorAppeals'] > 0 for c in lep)/max(len(lep),1):.0%}")


if __name__ == "__main__":
    main()
