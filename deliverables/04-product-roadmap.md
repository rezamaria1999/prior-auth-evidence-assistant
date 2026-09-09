# Product Roadmap

**Deliverable 4 of 5 · Humana AI Product Manager Take-Home**

---

## The sequencing principle

Most AI roadmaps put the model first and measurement somewhere around phase three. This one inverts that, for a reason that is specific to this product rather than general good practice:

> **You cannot tell whether this system works without a labelled sample of denials that nobody appealed.** Building that sample is slow, costs clinician hours, and has to happen before anything ships. So it is phase zero, not a later workstream.

Everything else follows from that. The phases are ordered by what each one makes measurable, not by what each one makes possible.

| Phase | What it delivers | What becomes measurable | **Gated by** |
|---|---|---|---|
| **0** | Gold set + claims layer | Whether the deterministic layer is any good | **People** — clinician review hours |
| **1** | Shadow mode, one LCD | Precision and recall on a live distribution | **Volume** — cases accumulating |
| **2** | Assisted review, limited pilot | Override rate — the metric that cannot exist earlier | **Behaviour** — reviewer habits settling |
| **3** | Service line expansion | Whether the approach generalises | **People again** — a gold set per line |
| **4** | Prioritisation model | Whether a trained model beats its baseline | **Label accumulation** |

### A note on why there are no week counts here

An earlier draft of this roadmap carried durations — 8 weeks, 12 weeks, 24 weeks. They were round numbers dressed as a plan, and they hid the thing that actually matters: **three different kinds of constraint govern these phases, and they don't respond to the same levers.**

**Phase 0 is people-bound.** 500 cases × 2 reviewers × ~20 minutes ≈ **333 clinician-hours**. The duration is entirely a staffing decision:

| Staffing | Elapsed |
|---|---|
| 2 physicians at 20% time | ~21 weeks |
| 4 physicians at 25% time | ~8 weeks |
| External review vendor | Faster, at cost |

There is no way to compress this except by buying more clinician time. Saying "8 weeks" without saying "four physicians at quarter time" is asking for a headcount commitment while hiding it inside a Gantt bar.

**Phase 1 is volume-bound.** It ends when ~200 live cases have been evaluated against gold-set labels. How long that takes is a function of lumbar MRI denial flow — a number Humana has by service line and I do not. **That is a data request for week one**, not a number to invent. My expectation is that case volume is *not* the binding constraint here and analysis-and-iteration time dominates, but that should be checked rather than assumed.

**Phase 2 is behaviour-bound**, and this is the one that cannot be rushed with volume. Override rate only means something once reviewers are past the novelty of a new tool. More cases per week does not make that happen faster; only elapsed weeks do.

**Each phase below therefore leads with its exit criteria.** The date falls out of the criteria and the staffing, not the other way round.

---

## Phase 0 — Build the measuring instrument

*Gated by clinician availability. ~333 review hours.*

**No model runs. Nothing ships. This phase exists to make the next four honest.**

### What gets built

**The gold set.** A stratified random sample of denied lumbar MRI prior authorizations. Two physician reviewers independently determine, for each case, whether coverage criteria were met and where the supporting evidence sits if it exists anywhere. A third adjudicates disagreements. Inter-rater agreement is tracked and reported.

At roughly 20 minutes per case per reviewer, 500 cases is on the order of **330 clinician-hours**. That is the real cost of this phase and it belongs on the slide, not in a footnote.

**The claims layer.** A deterministic query against the plan's own claims history — therapy, chiropractic, injections, prior imaging — filtered by diagnosis pointer and lookback window. No model involved. Validated against the gold set for coverage (what share of criterion conditions it can resolve) and correctness.

### Why this is first, and not later

Sampling from *appealed* cases would be faster and cheaper. It would also be systematically wrong: only ~11.5% of denials are appealed, and appealing correlates with health literacy, English proficiency, and having an advocate. A gold set drawn from appeals measures performance for people who fight and says nothing about the ~88% who don't — who are exactly the population this product exists to protect.

**Random sampling is the whole point, and it is why this phase is expensive.**

### Exit criteria
- Gold set of ≥500 adjudicated cases, inter-rater agreement reported
- Claims-layer coverage and correctness measured against it
- If the claims layer alone resolves most conditions, the language model may not be needed for this service line at all — and that is a legitimate outcome, not a failure

---

## Phase 1 — Shadow mode

*Gated by case volume, then by analysis time.*

**The system runs on live cases. No clinician sees anything.**

Outputs are logged and compared against the gold set and against the decisions reviewers actually made without it.

### Why shadow before visible

Precision and recall can be measured on a real case distribution — not a synthetic one, not a curated sample — while exposing zero members to a new failure mode. If the system performs worse in the wild than on the gold set, which it will to some degree, this is where that shows up and costs nothing.

This phase also produces the first honest answer to a question the prototype cannot address: **does the language model beat the claims layer alone?** If the narrative reading adds little over the deterministic layer, the model does not ship for this service line.

### Exit criteria
- ≥200 live cases evaluated against gold-set labels
- Precision above the floor (starting hypothesis 75–80%, confirmed or revised here)
- Narrative layer demonstrably adds value over claims-alone
- No evidence of differential flag rates by member subgroup — noting this is directional at this volume, not conclusive

---

## Phase 2 — Assisted review, limited pilot

*Gated by reviewer behaviour settling. Cannot be compressed with volume.*

**Live, visible, a small number of reviewers, one service line.**

### What this phase is actually for

Override rate. It is the single most important metric in the system and **it cannot be measured before this phase, because it requires clinicians using the tool.** No amount of offline evaluation produces it.

- Near 0% override means reviewers have stopped reading and are rubber-stamping. That is automation bias, and it is the failure mode that turns human-in-the-loop into a liability rather than a safeguard.
- Above roughly 60% means the model is not ready for this workflow.
- There is no target number in between. The pilot tells you where this system actually lands.

Alongside it: time-per-case, reviewer-reported usefulness, and — the counter-metric — whether approval rates move in a way that suggests the tool has become a rubber stamp in the other direction.

### Guardrails
- No bulk actions. Every case opens individually.
- Every finding carries a one-click disagreement path with a captured reason. Those reasons are the loop closing.
- Weekly review of overridden findings; patterns feed prompt and criteria revisions.

### Exit criteria
- Override rate inside a defensible band, with the band justified from observed behaviour rather than assumed
- No increase in inappropriate approvals
- Reviewers report the tool saves time rather than adding a step

---

## Phase 3 — Service line expansion

*Gated by clinician availability again — one gold set per service line.*

**Add coverage criteria in order of denial volume × appeal overturn rate.**

### Why expansion is cheaper than it looks — and more expensive than it looks

Cheaper: **criteria are text.** Adding an LCD is adding a document and a service-code mapping, not writing code. There is no per-criterion engineering cost of consequence.

More expensive: **every new service line needs its own gold set.** That is the same 330-clinician-hour instrument, repeated. Expansion is gated by validation capacity, not by engineering capacity, and the roadmap should be honest that this is what limits the rate.

Denials concentrate. A small number of service categories account for most of them. The sequence is set by where the volume and the overturn rate are highest, not by where the criteria are easiest.

### Exit criteria
- Three to five service lines live, each independently validated
- Per-line performance reported separately — pooled metrics would hide a failing line inside a healthy average

---

## Phase 4 — Prioritisation

*Gated by unbiased label accumulation. Earliest realistic start is a year of gold-set collection in.*

**Now, and only now, a trained model.**

Phases 0–3 find evidence. They do not decide which cases to look at first. Phase 4 adds prioritisation: predicting which pending cases are most likely to be wrongly denied, so the queue orders itself.

This is the first phase that needs training labels, and by now three sources exist:

| Source | Volume | Bias |
|---|---|---|
| Plan appeal outcomes | High | Heavily biased — reflects who appeals |
| IRE decisions | Lower | Cleaner — adjudicated externally |
| Accumulated gold sets | Whatever was funded | **Unbiased** — the only source covering non-appealers |

**The trap, stated before anyone asks:** a model trained naively on appeal outcomes learns to predict *who fights*, not *which decisions are wrong*. Since appealing correlates with literacy, language and advocacy, such a model would direct extra scrutiny toward members who already had advocates — and away from those who did not. Same structural failure as Obermeyer et al. (*Science*, 2019), where cost stood in for health need.

The mitigation is not clever weighting. It is the gold set — which is why it was funded in phase 0, eighteen months before the model that needs it.

**And build the boring baseline first.** A gradient-boosted model over structured features — service code, criterion, requesting specialty, packet page count, presence of unitemized outside records — will capture real signal. Build it deliberately as the thing the language model has to beat. If it doesn't beat it, ship the baseline and say so.

By this phase, volume also makes **subgroup performance measurable for the first time** — roughly 2,000 cases to detect a ±5 point difference between language subgroups. The fairness question the prototype had to decline finally has enough data to answer.

---

## Who is involved, and when

A roadmap written as though the PM does everything is a roadmap that has never shipped. The dependencies that actually gate this work:

| Function | Engaged | Why then, specifically |
|---|---|---|
| **Privacy / legal** | **Before phase 0** | Member records cannot be pulled for a gold set without review. This gates everything and is the most commonly forgotten item on this list. |
| **Model governance** | **Before phase 0** | Whatever body signs off on AI use should see the design before it runs, not after it has results. Going to them early is also how "AI in coverage decisions" stops being a surprise. |
| **Clinical operations** | Phase 0 | Recruiting and scheduling physician reviewer time is the critical path for phase 0. This is a staffing negotiation, not a request. |
| **Data engineering** | Phase 0 | The claims query is the first thing built and it is real engineering — diagnosis-pointer filtering, lookback windows, adjudication lag. |
| **Backend engineering** | Late phase 0 → phase 1 | Pipeline, logging, and the citation verification step. |
| **Design** | **Phase 1 — not phase 2** | Shadow mode has no interface. But the moment the system becomes visible, the interface *is* the product: what silence looks like, whether disagreement resolves, what the reviewer sees first. Bringing design in at phase 2 means shipping a PM's wireframes. |
| **Security** | Before any PHI reaches a model | Particularly if the narrative layer calls an external model API. |
| **Procurement / vendor** | Phase 0 | If the model is a third-party API, contracting reliably takes longer than the engineering. |
| **UM leadership** | Phase 2 | They own the reviewers whose time the pilot consumes, and they own the override-rate conversation. |

**The one worth saying out loud: design starts in phase 1.** Every question that matters in this product — what an empty state implies, whether the system resolves a conflict or hands it over, what a reviewer's eye lands on first — is a design question, and it needs to be answered while shadow mode is still running.

---

## What the sequencing argument is, in five lines

1. **Measurement before feature.** The gold set is phase 0 because nothing downstream is interpretable without it.
2. **Shadow before visible.** Live performance can be measured without exposing a single member to a new failure mode.
3. **The pilot is not optional.** Override rate is the most important metric in the system and only a pilot produces it.
4. **Expansion is gated by validation, not engineering.** Criteria are text; gold sets are clinician-hours.
5. **The trained model is last because its labels take a year to accumulate honestly.** Anything faster means training on who appeals.

---

## What would make me stop

A roadmap without kill criteria is a wish. Three points where this should stop rather than continue:

- **End of phase 1:** if the narrative layer does not beat the claims layer alone, the language model does not ship. The claims query does, on its own.
- **During phase 2:** if override rate sits near zero, reviewers have stopped reading. That is worse than not shipping, and it is a stop condition rather than a tuning problem.
- **Any phase:** if flag rates differ materially by member subgroup once volume permits the measurement, the system stops until that is explained.
