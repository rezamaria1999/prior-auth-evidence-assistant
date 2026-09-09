# Prior Authorization Evidence Assistant — working prototype

A prototype for a utilization management problem: prior authorization requests get
denied for missing documentation that the plan already holds. This surfaces that
evidence to the reviewing physician *before* the determination, instead of leaving it
to be found on appeal.

Built as a take-home for a Senior AI Technical Product Manager interview.

**Live demo:** https://USERNAME.github.io/REPO/
**Slides:** https://USERNAME.github.io/REPO/deck/

---

## What to look at first

If you have five minutes and want to judge the engineering thinking rather than the
product narrative, read these three files in order:

| File | Why |
|---|---|
| [`prompts/extraction-prompt.md`](prompts/extraction-prompt.md) | The actual prompt the system runs, with the reasoning behind each constraint. The safety properties are enforced here. |
| [`scripts/verify_citations.py`](scripts/verify_citations.py) | The hallucination guard. Every model finding must quote text that provably exists in the source, checked by exact string containment. No model involved. |
| [`scripts/test_guard.py`](scripts/test_guard.py) | The negative test. Injects fabricated and drifted quotations and confirms each is discarded — the guard is demonstrated, not asserted. |

## Architecture

Three layers run in order, and only the last one is a language model.

1. **Claims query** — deterministic. Resolves criterion conditions that the plan's own
   claims history already answers.
2. **Structured checks** — deterministic. Resolves conditions answerable from
   structured fields on the request.
3. **Narrative reading** — the language model. Handles only what layers 1 and 2 could
   not resolve, and receives their results as `ALREADY_RESOLVED` so it does not
   re-derive or contradict a stronger source of evidence.

Two design decisions worth naming:

- **The model never decides.** It locates and quotes evidence bearing on a named
  coverage criterion. It does not assess medical necessity, characterise the strength
  of a case, or describe missing evidence as supporting denial. The physician makes
  every determination.
- **An empty result is a correct result,** and its wording is specified verbatim in the
  prompt. When the system finds nothing, the reviewer proceeds toward denial — so
  silence carries weight in the workflow whether or not that is intended. Wording that
  implied "nothing found, safe to deny" would make the system a participant in adverse
  determinations through the back door.

The prototype's outputs include a case where layer 3 still makes an error the prompt is
written to prevent: a complete, well-formatted therapy record for a *knee* replacement
in a case about a *lumbar* complaint. That failure is left in deliberately. It is why
the deterministic layer runs first and why layer disagreement is surfaced to the
reviewer rather than resolved silently.

## Running it

The demo is a single self-contained file. No server, no dependencies.

```bash
open index.html
```

To rebuild it after editing the data:

```bash
python3 build.py                      # inlines data/*.json into index.html
python3 scripts/verify_citations.py   # check every quotation against its source
python3 scripts/test_guard.py         # confirm fabricated quotations are discarded
```

The data lives as JSON so it stays readable and reviewable; `build.py` inlines it so the
demo is a file you can double-click.

## Repository map

```
index.html                   built demo — open this
build.py                     inlines data into index.html
src/shell.html               demo source (pre-inlining)
data/
  cases-hero.json            full cases with complete source documents
  cases-queue.json           queue-level summaries, calibration, model performance
  criteria.json              coverage criteria, quoted from the CMS determination
  model-outputs.json         model outputs with provenance and prompt version
prompts/
  extraction-prompt.md       the production prompt + design notes
scripts/
  verify_citations.py        citation guard
  test_guard.py              negative test for the guard
deliverables/                written deliverables (problem brief, service design,
                             roadmap, key tradeoff, data & evaluation strategy)
deck/                        presentation slides
```

## A note on the data

Every case, member and document in this repository is **synthetic**. No real member
data, no real claims, no protected health information. Coverage criteria are quoted
from published CMS local coverage determinations; the clinical records around them are
fabricated to exercise the workflow, including the failure cases.
