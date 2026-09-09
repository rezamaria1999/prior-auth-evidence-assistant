# Data and Evaluation Strategy

**Supporting document · Humana AI PM Take-Home**
Answers the question: *what does this thing learn from, and how would you know if it worked?*

---

## 1. The headline: v1 trains nothing

The product assembles evidence against a published coverage rule in three layers, cheapest first, and reports what it found with citations.

| Layer | Method | Answers | Evidential weight |
|---|---|---|---|
| **1. Claims history** | Database query | Did the plan already pay for this treatment, and when? | **Highest** — a paid claim is a transaction record, not an inference |
| **2. Structured fields** | Deterministic checks | Service code, diagnosis pointers, prior imaging, completeness | High |
| **3. Narrative reading** | Language model | Judgments that exist only in prose | Lower — a reading, requiring citation and verification |

Only the third layer involves a model, and it is prompted, not trained. It is also not retrieval-augmented generation in the vector-search sense: a case file is 20–40 pages and fits entirely in context, and the applicable criterion is selected by service code through a deterministic lookup rather than semantic search. There is nothing to retrieve.

**The ordering is a cost decision and an accuracy decision at the same time.** The cheapest layer is also the most reliable one, which is an unusually convenient alignment and worth stating plainly.

**There is no training set. There are no learned weights. Nothing is fit to historical decisions.**

This is a deliberate architectural choice, not a limitation of the prototype, and the reasoning holds in production:

| Property | Consequence |
|---|---|
| No training corpus | No training-set bias to audit, no member records retained for model fitting |
| Output traces to a passage in *this* case | Explainable per decision, not "the model learned it" |
| Criteria are text, not weights | A coverage rule change is a text edit, not a retrain and revalidation cycle |
| No fit to historical denials | The system cannot inherit and reproduce the plan's past errors |

That last row matters most. **A model trained on historical decisions learns to reproduce historical decisions — including the 13% OIG found were wrong.** Not training is what keeps the system from laundering past error into future error.

### What flows at inference time

1. The member's claims history over an 18-month lookback, filtered to the relevant treatment and diagnosis
2. The case documents as submitted — referring note, outside records, medication list, prior imaging
3. The applicable coverage criteria as published text — here, CMS LCD L34220
4. The specific criterion the case is failing on, per the nurse's routing note

All four already exist inside Humana today. Nothing new needs to be collected for the system to run.

### Worked example: how the layers divide LCD L34220

The criterion has two conditions, and they decompose cleanly:

> *"MRI will be covered only if the patient **has not responded** to a reasonable trial of conservative management **lasting at least four weeks**."*

- **"lasting at least four weeks"** — answered by claims. Eight paid therapy claims spanning 5.4 weeks is a fact on the ledger, requiring no reading and no model.
- **"has not responded"** — answered only by narrative. Non-response is a clinical judgment recorded in a discharge summary: *"0 of 3 functional goals met, symptoms essentially unchanged."* No claim can carry it.

Both conditions are required. No single layer answers both. That decomposition is the argument for the architecture, and it generalises — most coverage criteria mix ledger facts with clinical judgments.

### When layers disagree

They will, and the disagreement is informative rather than embarrassing.

The prototype's second hero case makes this concrete: 21 paid therapy claims spanning eight weeks, which looks like documented conservative management until the diagnosis pointers are read — every claim carries Z96.651, right knee arthroplasty. The claims layer gets this right. The narrative layer, presented with a complete and well-formatted therapy record whose lumbar references are incidental postural screening, gets it wrong.

**The system surfaces both findings, marked as conflicting, and does not resolve them.** The reviewer adjudicates. Silently deferring to the claims layer would be simpler and usually correct, but it would suppress precisely the signal that identifies genuinely ambiguous cases.

---

## 2. But you cannot ship without evaluation data

This is the real cost, and it is where the honest work is.

The system makes a claim — *"support for criterion C2 appears on page 9 of the outside records packet."* To know whether it is any good, you need cases where a physician has independently determined what the correct answer was. That is a **gold set**, and it has to be built.

### How to build it — the OIG method

HHS OIG produced its 13% figure by drawing a stratified random sample of denials and having coding experts and physician reviewers adjudicate each one. That is exactly the instrument needed here:

1. Randomly sample denied prior authorization cases in the target service line
2. Two physician reviewers independently determine whether coverage criteria were met and where the supporting evidence sits, if anywhere
3. Adjudicate disagreements with a third reviewer; track inter-rater agreement
4. The resulting labels are the gold set

**Cost is clinician hours, and it belongs in the roadmap as a real budget line rather than an assumption.** A rough order: at roughly 20 minutes per case per reviewer, two reviewers, 500 cases is on the order of 330 clinician-hours.

### Why random sampling is non-negotiable

Sampling from *appealed* cases would be cheaper and faster. It would also be wrong, and in a specific, predictable direction.

Only ~11.5% of MA denials are appealed, and appealing correlates with health literacy, English proficiency, having an advocate, and having a provider with dedicated prior-auth staff. **A gold set drawn from appeals would teach you how the system performs for people who fight, and tell you nothing about the ~88% who don't** — who are precisely the population this product exists to protect.

Random sampling of all denials is the only way to get labels for the silent majority. It is more expensive. It is the entire point.

---

## 3. What to measure

### The unit of prediction

Per case, per criterion condition: *does findable supporting evidence exist, and where?*

Not "should this be approved." The system does not opine on the coverage decision. It reports on the contents of the record.

**Evaluate each layer against what it is actually responsible for.** A condition resolved deterministically by claims is not subject to model error and does not belong in the model's denominator. Pooling them would flatter the model by crediting it with the database's work — and would hide a claims-layer failure inside an apparently healthy aggregate. In practice this means three numbers, not one:

- **Claims layer:** coverage (what share of conditions it can resolve) and correctness on those
- **Narrative layer:** precision and recall on the conditions only reading can answer
- **Conflict rate:** how often the layers disagree, and who is right when they do

The third is the most operationally interesting and the one nobody instruments by default. A rising conflict rate is an early warning that something upstream has shifted — a coding practice change, a new document source, a drifting model.

### The two error types and what each costs

| | What happens | Cost |
|---|---|---|
| **False positive** | System flags support; reviewer looks; it isn't really support | A few minutes of reviewer time, plus erosion of trust in the tool |
| **False negative** | System misses buried support; case is denied | A member is wrongly denied care, plus downstream appeal and rework |

These are not symmetric. A false negative is a member harm. A false positive is an inconvenience.

### So: optimize recall, subject to a precision floor

The naive conclusion is "maximise recall, false negatives are worse." That is half right and the other half is where products die.

**If precision falls too low, reviewers stop reading the flags — and an ignored tool has an effective recall of zero, whatever the offline number says.** This is the Epic Sepsis Model failure exactly: alerts on 18% of all hospitalized patients, 12% positive predictive value, and the result was alert fatigue rather than earlier sepsis detection.

The operating rule:

> Tune for recall, subject to a hard precision floor. The floor is an empirical question answered by watching reviewer override behaviour in a pilot — not a number chosen in advance. My starting hypothesis is somewhere around 75–80%, and I would treat a sustained drop below it as a stop-ship condition rather than a tuning opportunity.

### Silence is also a claim, and must not read as endorsement

If the system surfaces nothing, the reviewer proceeds toward denial. That means the absence of a flag carries weight in the workflow whether or not it is intended to.

**Design constraint:** the system must never state or imply that a denial is appropriate. The no-finding state reads:

> *No supporting evidence identified in the submitted record. This is not a coverage recommendation.*

This is what keeps the never-deny property architectural rather than aspirational. A system that says "no support found, safe to deny" has begun making adverse determinations through the back door.

---

## 4. How much data is enough — and the honest limit of the prototype

Sample sizes required to estimate a rate at 95% confidence.

**Method note.** These use the Wilson score interval rather than the normal (Wald)
approximation. Wald is the familiar `w = z·√(p(1−p)/n)` form, and it is fine at large
n — but at small n and extreme rates it produces intervals that run past 100%, which
is a signal it has left its valid range. Every interval below is Wilson. Planning
figures assume p = 0.80 and simple random sampling; a conservative planner would use
p = 0.50, which raises every n.

| Assumed rate | ±10pp | ±5pp | ±3pp |
|---|---|---|---|
| 50% (most conservative) | 97 | 385 | 1,068 |
| 70% | 81 | 323 | 897 |
| 80% | **62** | **246** | 683 |
| 85% | 49 | 196 | 545 |

Precision is estimated on flagged cases. **Recall is estimated only on cases that
actually contain support** — and at an assumed ~18% support rate that denominator
shrinks fast:

| Cases reviewed | With support | 95% CI on recall (Wilson) | Width |
|---|---|---|---|
| **34 (this prototype)** | **6** | **44% – 97%** | **53pp** |
| 200 | 35 | 67% – 92% | 25pp |
| 500 | 88 | 74% – 89% | 16pp |
| 1,000 | 176 | 77% – 88% | 11pp |
| 2,000 | 352 | 79% – 87% | 8pp |

### State this plainly in the presentation

> The prototype reports 83% recall on six cases that contained findable support. The
> 95% confidence interval on that runs from 44% to 97%. That is not a measurement —
> it spans everything from barely better than chance to near-perfect. Knowing recall
> to within about five points requires on the order of a thousand adjudicated cases,
> and that is a phase-one budget line, not an afterthought.

Volunteering this is stronger than being caught by it. It also converts a weakness
into the reason the roadmap is shaped the way it is.

### And it settles the subgroup question

Detecting differential behaviour for members with limited English proficiency. **The ~12% population share below is my working assumption and is not yet sourced — verify before presenting it.**

| Cases | LEP members | 95% CI (Wilson) | Width |
|---|---|---|---|
| 500 | 60 | 72% – 91% | 19pp |
| 2,000 | 240 | 78% – 88% | 9pp |
| 5,000 | 600 | 80% – 86% | 6pp |

At the prototype's scale there are a handful of such members. **That is not a measurement.** The prototype therefore reports no subgroup performance at all, and no monitoring surface was built into it: at this volume there is nothing honest to put on one. The metrics that *are* legitimate here — the confusion matrix, flag rate, and the interval on recall — are presented in the deliverables rather than dressed up as a product dashboard.

Fabricating a plausible-looking subgroup dashboard would be inventing evidence that the fairness property holds. Declining to report it is the correct answer.

---

## 5. When training data does enter — phase 2

V1 finds evidence. It does not decide which cases to look at first. Phase 2 adds **prioritisation**: predicting which pending cases are most likely to be wrongly denied, so the queue orders itself.

That is a supervised problem, and it needs labels. Three sources, in ascending order of quality and cost:

| Label source | Volume | Bias | Cost |
|---|---|---|---|
| **Plan appeal outcomes** | High — already generated daily | **Heavily biased.** Reflects who appeals, not which decisions were wrong | Free |
| **IRE decisions** | Lower | Cleaner — adjudicated by an outside entity, not the plan | Free |
| **Random audit sample** | Whatever you fund | **Unbiased** — the only source covering non-appealers | Clinician hours |

**The trap, stated before anyone asks:** a model trained naively on appeal outcomes learns to predict *who fights*, not *which decisions are wrong*. Since appealing correlates with literacy, language, and advocacy, such a model would direct extra scrutiny toward members who already had advocates — and away from those who did not. Same structural failure as Obermeyer et al. (*Science*, 2019), where cost stood in as a proxy for health need and systematically under-referred Black patients at equal illness levels.

The mitigation is not clever weighting. It is the audit sample — the same instrument that produces the gold set. **One investment, two jobs.** That is why it appears in phase one of the roadmap even though the model that needs it does not arrive until phase two.

### Also worth saying: build the boring baseline first

A gradient-boosted model over structured features — service code, criterion, requesting specialty, submission completeness, packet page count, presence of unitemized outside records — will capture a real share of the signal.

Build it first, deliberately, as the thing the language model has to beat. If reading the chart does not outperform it, ship the baseline and say so. A feature that cannot beat its own baseline should not ship because it is the exciting one.

---

## 6. Prototype data governance

- **All data is synthetic.** No real members, providers, or facilities. No PHI touches the prototype at any point.
- **Clinical structure is realistic:** real CPT and ICD-10 codes, multi-source documents, unitemized faxed packets, evidence buried where it is actually buried.
- **Coverage criteria are real** — CMS LCD L34220, public, quoted verbatim. The system checks against genuine Medicare coverage language, not invented rules.
- **The case mix is calibrated, not arbitrary.** The ~18% true support rate is anchored to OIG's finding that 13% of denied MA prior authorization requests met coverage rules.
- **The model is deliberately imperfect** — one false positive from an unrelated therapy episode, one false negative from an illegible scanned note. A demo reporting perfect performance is a demo nobody believes.

---

## 7. The one-paragraph version

> Version one trains on nothing. It assembles evidence in three layers — the plan's own claims ledger first, structured checks second, and a language model reading the clinical narrative only for judgments the first two cannot answer. There is no training-set bias to audit, and every output traces either to a paid claim or to a verified passage in that specific case. What it does require is an evaluation set — randomly sampled denials, physician-adjudicated — because sampling from appeals would measure performance only for members who fight. That gold set is a clinician-hours line item in phase one, and it does double duty as the unbiased label source for the phase-two prioritisation model. The prototype's own recall figure rests on six cases and carries a 95% confidence interval running from 44% to 97%, which is why it is presented as an illustration of the measurement rather than as evidence of performance.

---

### Sources

- HHS OIG, April 2022 — [oig.hhs.gov](https://oig.hhs.gov/reports/all/2022/some-medicare-advantage-organization-denials-of-prior-authorization-requests-raise-concerns-about-beneficiary-access-to-medically-necessary-care/)
- KFF, MA prior authorization determinations 2024 — [kff.org](https://www.kff.org/medicare/medicare-advantage-insurers-made-nearly-53-million-prior-authorization-determinations-in-2024/)
- Wong et al., *External Validation of a Widely Implemented Proprietary Sepsis Prediction Model in Hospitalized Patients*, JAMA Internal Medicine, 2021 — [jamanetwork.com](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2781307)
- Obermeyer et al., *Dissecting racial bias in an algorithm used to manage the health of populations*, Science, 2019
- CMS LCD L34220 — [cms.gov](https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?LCDId=34220)
