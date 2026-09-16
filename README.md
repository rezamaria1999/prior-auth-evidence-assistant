# Prior Authorization Evidence Assistant

A prototype for a utilization management problem. Coverage requests get denied for
insufficient documentation when the documentation is frequently not missing — it sits
on page nine of a forty-page fax, or in the plan's own claims ledger, because the plan
already paid for the treatment it is now saying wasn't documented.

This assembles that evidence and puts it in front of the clinician reviewing the case,
before the determination rather than after the appeal.

**Case study:** [maria-reza-pm-portfolio.netlify.app](https://maria-reza-pm-portfolio.netlify.app/#humana) ·
**Technical write-up on evaluation:** [same site, evals page](https://maria-reza-pm-portfolio.netlify.app/#evals)

---

## What to look at first

If you have ten minutes and want to judge the engineering rather than the product
narrative, these four in this order:

| File | Why |
|---|---|
| `prompts/extraction-prompt.md` | The prompt the system actually runs, with the reasoning behind each constraint. The safety properties are enforced here and in the two guards below. |
| `scripts/verify_citations.py` | The hallucination guard. Every model quotation is string-matched against its source before display, and failures are discarded. Roughly ten lines of real logic. |
| `scripts/structural_checks.py` | The relevance guard. Catches evidence that is authentic and irrelevant, which the citation guard cannot see. |
| `scripts/evaluate.py` | The offline harness. Scores model output against a labelled probe set, broken out by failure class rather than pooled. |

## Run it

No dependencies beyond Python 3.

```bash
python3 scripts/verify_citations.py    # provenance guard against the cached outputs
python3 scripts/test_guard.py          # negative test: fabricated and drifted quotes
python3 scripts/evaluate.py --compare  # offline eval, with and without the relevance guard
```

The prototype itself is a single self-contained HTML file. Open `index.html` in a
browser; nothing to install and no server required.

---

## How it works

Three layers run in order, and only the last one is a language model.

1. **Claims query** — deterministic. Resolves criterion conditions the plan's own claims
   history already answers. A paid claim is a transaction record, not an inference.
2. **Structured checks** — deterministic. Service codes, diagnosis pointers, prior
   imaging, body-region consistency.
3. **Narrative reading** — the language model. Handles only what layers 1 and 2 could
   not resolve, and receives their results so it does not re-derive or contradict a
   stronger source.

The ordering comes from the coverage rule itself. CMS LCD L34220 reads: *"MRI will be
covered only if the patient has not responded to a reasonable trial of conservative
management lasting at least four weeks."* One sentence, two conditions, completely
different kinds of question. Whether therapy happened and for how long is a database
query. Whether the patient responded to it exists only in prose, in a different
document every time.

Most coverage criteria have that shape, which is why adding a criterion means adding a
document rather than writing code.

### What it cannot do

- **Deny.** No code path runs from the model to an adverse determination. Absent from
  the architecture, not disabled by a setting.
- **Quote something that isn't there.** Verbatim quotation, exact string match, failures
  dropped before display.
- **Settle a disagreement.** When the claims layer and the model contradict each other,
  both are shown and the clinician decides.
- **Imply a denial by going quiet.** The empty state is fixed wording that cannot be
  read as "nothing found, safe to deny."

---

## Two guards, two different properties

The distinction matters more than it looks, and conflating them is the most common way
to think a system is safer than it is.

**Provenance** — does this text exist, verbatim, where the model says it does?
`verify_citations.py` answers that by string equality. No model involved.

**Relevance** — does that authentic text bear on *this* criterion for *this* request?
`structural_checks.py` answers that with lookups: body region, member identity, trial
duration.

The prototype ships with a case that makes the difference concrete. A member's record
holds twenty-one paid therapy claims across eight weeks, fully documented and entirely
real. Every claim carries a diagnosis pointer for a knee replacement. The request is
about a lumbar complaint. The model reports the therapy as supporting evidence, the
quotation verifies perfectly, and the finding is useless.

That case is left in on purpose. The prompt's rule 4 already instructs the model to
check body region, and the cached outputs show it does not reliably comply, which is
the argument for enforcing it outside the model rather than writing a sterner prompt.

One detail in `check_duration` worth reading: it fires only when the ledger shows a
trial that is affirmatively *too short*, never on the absence of claims. Out-of-network,
cash-pay and self-directed therapy are invisible to a claims ledger, so treating "no
claims found" as "no therapy happened" would suppress findings for exactly the members
this is meant to help.

---

## Evaluation

`data/eval-set.json` is a labelled probe set. Each probe exercises one named way the
system can fail: therapy for the wrong body region, a patient who actually got better,
therapy that hasn't happened yet, therapy explicitly declined, a trial too short to
count, a page belonging to a different member, a genuine find buried in illegible
handwriting, plus a clean positive as a control.

`scripts/evaluate.py` scores an outputs file against those labels and reports detection
with Wilson intervals, localisation, citation fidelity, relevance, abstention quality
and concern calibration, broken out per slice.

Running `--compare` shows the result that motivated the relevance guard:

| | Layer 3 alone | + structural checks |
|---|---|---|
| Precision | 25% | 100% |
| Recall | 50% | 50% |
| False positives | 3 | 0 |

Precision moves because every false positive on that slice was catchable by a join.
Recall does not move at all, because it is a different problem: the remaining miss is a
real find in a poor handwritten scan where the model tidied the abbreviations while
quoting, and the provenance guard discarded it for quote drift. Correctly. Loosening
the string match to recover it would trade away the property that makes every other
citation trustworthy, so that one is still open.

### What these numbers are not

The probe set is a **constructed adversarial slice**, not a random sample. Hard
negatives are over-represented deliberately, because failures of that kind are rare in
a random draw and disproportionately destroy reviewer trust. Precision here is a
diagnostic, never a prevalence estimate, and it must not be pooled with the
random-sample queue metrics.

n = 8. Every interval is enormous. A production gold set would be physician-adjudicated
by two independent reviewers with a tracked inter-rater agreement rate, which is the
ceiling on achievable performance and is currently unmeasured here. The harness prints
all of this with its own output rather than leaving it to a footnote.

---

## Data

Every case, member, provider and document in this repository is **synthetic**. No real
records, no protected health information. Coverage criteria are quoted from published
CMS local coverage determinations and are real.

The cached model outputs in `data/model-outputs.json` and `data/eval-outputs.json` were
produced by running the prompt against the case documents. They are recorded as
produced, including the ones that are wrong, and are not hand-authored to a target
score.

## Repository map

```
index.html                     working prototype, self-contained
deck/index.html                presentation version
build.py                       inlines data into the single-file prototype
src/shell.html                 prototype template used by build.py

prompts/extraction-prompt.md   the production prompt

scripts/
  verify_citations.py          provenance guard
  test_guard.py                negative test for the guard
  structural_checks.py         relevance guard
  evaluate.py                  offline eval harness

data/
  criteria.json                CMS LCD L34220, quoted
  cases-hero.json              the three demo cases with full documents
  cases-queue.json             31 generated queue cases
  generate_queue.py            how the queue was composed, and why
  model-outputs.json           cached layer-3 outputs for the demo cases
  eval-set.json                labelled probe set
  eval-outputs.json            model outputs for the probes

deliverables/                  problem brief, service design, roadmap, key tradeoff,
                               data and evaluation strategy, technical appendix
```

---

*Independent product exercise, built to demonstrate product thinking on a publicly
documented problem. Not affiliated with, endorsed by, or reviewed by any health plan.*
