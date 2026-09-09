# Problem Brief

**Deliverable 1 of 5 · Humana AI Product Manager Take-Home**
**Business process area:** Utilization Management — prior authorization decision quality
**Wedge:** Advanced diagnostic imaging (lumbar MRI)

---

## 1. The problem

A Medicare Advantage plan issues on the order of a million coverage denials a year. Roughly four in five of the denials that get challenged are reversed. Fewer than one in eight are ever challenged.

Read those two numbers together and they say something specific: **the first decision is frequently wrong, and the organisation only finds out when somebody fights.**

The appeal is the diagnostic, not the cure. By the time a denial is overturned the member has waited weeks, the provider has done the work twice, and the plan pays for the care anyway. For the ~88% who never appeal, nothing corrects it at all.

So the question is not how to run appeals better. It is why the first decision is wrong so often — and the answer is not that reviewers are bad at medicine:

> **At the moment the decision is made, the evidence that would support approval is frequently already in the plan's possession — and nothing in the process puts it in front of the person deciding.**

Some of it sits in the plan's own claims ledger. Some sits buried in an unitemized fax from a practice the member left months ago. The reviewer has a clock, a queue, and whatever the referring physician chose to summarise.

### What actually goes wrong at the moment of decision

HHS Office of Inspector General reviewed a stratified random sample of 250 MA prior authorization denials and found that **13% met Medicare coverage rules and should have been approved.** Two mechanisms accounted for most of it:

1. Plans applied clinical criteria not contained in Medicare coverage rules.
2. Plans **claimed insufficient documentation when the existing medical records were in fact sufficient** to support medical necessity.

The second mechanism is the one this product addresses, and it is worth stating precisely. It is not that the file was incomplete. **It is that the file contained the answer and the reviewer did not find it.**

That is a search-and-synthesis failure over long, unstructured, multi-source clinical documents, performed under a regulatory clock. It is not a failure of clinical judgment, and it is not a problem a rules engine can solve.

### A concrete instance

CMS Local Coverage Determination **L34220** governs lumbar MRI coverage. It contains this requirement:

> *"MRI will be covered only if the patient has not responded to a reasonable trial of conservative management lasting at least four weeks."*

Whether that four-week trial happened is a matter of fact. It is either documented somewhere in the submitted records or it is not.

In practice it is frequently documented in the *wrong place* — a therapy discharge summary inside an unitemized faxed packet from a different practice, months earlier — while the referring physician's own note says only "the patient has tried therapy in the past." The nurse reviewer reads the referring note, cannot substantiate the four weeks, and routes the case toward denial. The evidence was in the file the entire time.

---

## 2. Target audience

### Primary user: the medical director at the pre-denial review checkpoint

This user is not chosen for convenience. **CMS requires them to exist.** Under the 2024 MA final rule (CMS-4201-F), where a plan expects to issue a partially or fully adverse medical-necessity decision, that determination

> *"must be reviewed by a physician or other appropriate health care professional with expertise in the field of medicine or health care that is appropriate for the services at issue, including knowledge of Medicare coverage criteria, **before** the MA organization issues the organization determination decision."*

A nurse reviewer may approve. A nurse reviewer may not deny. Every denial passes through a clinician, by regulation.

That checkpoint is the intervention point. **This product does not insert AI into a coverage decision. It improves the information available at a review step that already exists and is already legally mandated.** The decision-maker, the accountability, and the workflow position are unchanged.

The information is assembled cheapest-first, and the ordering is deliberate:

| Layer | What it answers | Cost | Evidential weight |
|---|---|---|---|
| **1. Claims history** | Did the plan already pay for the treatment in question, and when? | Database query | **Highest** — a paid claim is the plan's own transaction record, not an inference |
| **2. Structured fields** | Service code, diagnosis, submission completeness, prior imaging | Deterministic checks | High |
| **3. Narrative reading** | The judgments that exist only in prose — did the patient *respond* to treatment? | Language model | Lower — a reading, requiring citation and verification |

The principle is to use the cheapest sufficient tool for each sub-question and reserve the expensive general-purpose one for what genuinely requires judgment. Applied to LCD L34220, the split is exact: **claims can establish that a four-week trial occurred; only the clinical narrative can establish that the patient did not respond to it.** Both conditions are required, and no single layer answers both.

Where layers disagree, the system surfaces the conflict rather than silently resolving it. Disagreement marks the cases that are genuinely ambiguous, and those are the ones a clinician should be looking at.

### Who benefits

| Stakeholder | What changes for them |
|---|---|
| **The member** | The correctness of their first decision stops depending on whether they have the health literacy, language, energy, or advocate to appeal. |
| **The requesting provider** | Less work done twice. Physicians currently spend ~13 hours a week on prior authorization; 40% of practices employ staff who do nothing else. |
| **The nurse reviewer** | Referrals to the medical director arrive with the record already searched rather than as an unsorted packet. |
| **The medical director** | Sees the relevant evidence and the criterion side by side instead of hunting for it against a clock. |
| **Appeals & grievances** | Fewer avoidable cases arriving thirty days later as rework. |
| **Humana** | Lower rework cost, fewer IRE auto-forwards, better provider experience, and defensible decision quality at a moment when those metrics are public. |

### The equity dimension is structural, not decorative

Appealing a denial requires initiative, paperwork, time, and usually an advocate. Members with limited English proficiency appeal at markedly lower rates. **A system whose accuracy is rationed by who fights hardest will be least accurate for the members least equipped to fight.** That is a Section 1557 exposure and a Stars/CAHPS exposure, and it is the clearest argument that first-decision accuracy is not merely an efficiency question.

---

## 3. Current pain points

### The decision moment

| Condition | Consequence |
|---|---|
| Records are unstructured, long, multi-source, often faxed | Relevant evidence exists but must be *found* |
| 7-day standard / 72-hour expedited clock (CMS-0057-F, 2026) | Time per case is bounded and shrinking |
| Reviewer sees this case, not the pattern | No signal that similar cases were reversed |
| Criteria are layered — NCD, LCD, internal, evidence base | Wrong criterion easily applied (OIG mechanism #1) |
| Appeal outcomes arrive weeks later to a different team | The loop never closes |

### Downstream

- **Members:** 95% of physicians report prior authorization delays necessary care; 79% report patients abandoning treatment; **26% report prior authorization has led to a serious adverse event.**
- **Providers:** ~40 prior authorization requests per physician per week, ~13 hours of physician and staff time. Only 33% believe the industry's 2025 reform pledge will make a meaningful difference.
- **The plan:** every overturned denial is a denial letter, an appeal intake, a clinical re-review, and sometimes an IRE referral — all spent on care that is ultimately approved and paid for anyway.

### Why the industry's current answer has run out

The sector's response so far has been **subtraction** — removing prior authorization requirements. Humana removed 340+ codes across 2024–2025, roughly a third of outpatient diagnostic prior authorization. Industry-wide the AHIP/BCBSA pledge produced an 11% reduction, about 6.5 million fewer requirements.

And yet 95% of hospitals report spending *more* time on prior authorization than before.

Subtraction has hit its practical limit, and the requests that remain are the ones nobody was willing to delete — the judgment-dependent, documentation-heavy, clinically ambiguous cases. **The residual is the hard core.** It cannot be subtracted away. It can only be decided better.

---

## 4. Why Humana, and why now

### The Humana-specific picture

Humana's numbers do not fit the "insurers deny too much" narrative, and the brief is stronger for saying so plainly.

| | Humana | UnitedHealth Group |
|---|---|---|
| Prior auth requests per enrollee (2024) | **2.2** | 1.0 |
| Denial rate (2024) | **5.8%** | 12.8% |

Humana runs the **highest prior authorization volume per member among major MA insurers and denies at less than half UnitedHealth's rate.** The opportunity here is not "deny less." It is that enormous volume combined with a low denial rate means the surviving denials are concentrated in precisely the hard cases where error is most likely — and Humana has already deleted the easy ones.

### Five clocks running at once

1. **CMS-0057-F operational provisions are live in 2026.** Prior authorization decisions in 7 calendar days standard / 72 hours expedited. Specific denial reasons required. Public reporting of approval, denial, appeal-overturn, and turnaround metrics began **March 31, 2026.** Less time per decision, permanent visibility into the result.
2. **Four FHIR APIs land January 1, 2027**, including the Prior Authorization API. Structured, machine-readable prior authorization data is about to exist at scale.
3. **Humana's own commitments bind now.** ≥95% of complete electronic requests decided within one business day; gold carding launching 2026; a third of outpatient prior authorization already removed.
4. **Humana is becoming the largest MA insurer** — roughly 7.3 million members expected at the end of 2026, up from 5.8 million. Every per-member rate scales with it.
5. **Star Ratings.** Members in 4+ star plans fell from 94% (2024) to 25% (2025) to 20% (2026), with billions in revenue at stake. Appeals timeliness and member experience measures feed Stars directly.

### The sharpest version of "why now"

**Humana has publicly committed to being fast, and has simultaneously begun publishing how often it is right.**

Those two commitments are in tension. Speed and accuracy normally trade against each other, and nobody has built the thing that resolves them. That tension is the opening — and it did not exist eighteen months ago, because the accuracy half was not public.

---

## 5. Market opportunity

Sizing for Humana. **Every assumption below is contestable and stated deliberately.**

| Step | Assumption | Result |
|---|---|---|
| MA members, end of 2026 | Humana guidance | 7.3M |
| × prior auth requests per enrollee | 2.2 (KFF, 2024) | ~16M requests/yr |
| × denial rate | 5.8% (KFF, 2024) | **~930,000 denials/yr** |
| × appeal rate | 11.5% (KFF, MA average) | ~107,000 appealed |
| × overturn rate | ~80% (KFF, MA average) | ~86,000 overturned |
| **Denials never appealed** | remainder | **~823,000** |
| If OIG's wrongful-denial rate holds | 13% | **~120,000 denials/yr that should not have been issued** |

**Caveats, stated on the slide rather than in the footnotes.** Per-enrollee and denial rates are 2024 figures applied to 2026 membership. Appeal and overturn rates are MA-wide averages, not Humana's. The OIG 13% derives from a one-week 2019 sample across 15 organizations, not from Humana. This is an order-of-magnitude estimate, not a forecast.

**A reporting discrepancy worth naming before someone else does:** KFF reports ~80.7% appeal overturn from CMS plan-reported MA data (2024) and 67% from the new CMS-0057-F public metrics (2025 data). Different reporting regimes, different denominators. This brief uses the CMS plan-reported figure and acknowledges the other exists.

### What this is actually worth — and where the argument gets uncomfortable

The sizing above says how big the problem is. It does not say what fixing it is worth, and that gap is the first thing a business leader will press on. Here is the model, built conditionally so it works without Humana's internal numbers.

**Per 10,000 denials in a service line:**

| | |
|---|---|
| Wrongly denied, if OIG's 13% holds | **1,300** |
| ...of which are appealed (11.5%) | 150 |
| ...of which are overturned (80%) | **120** — corrected today, at the cost of a full appeal cycle |
| ...never appealed | **1,150** — never corrected at all |

**The addressable pool is roughly ten times the appeal pool.** Everything the current process catches, it catches through appeals — and appeals reach one wrongly-denied member in ten.

### The part worth volunteering before anyone asks

Priced purely as cost avoidance, **this business case is weak.** Avoiding 120 appeal cycles per 10,000 denials is worth somewhere between $12,000 and $60,000 depending on Humana's cost per appeal — a number Humana has and I do not.

And there is a harder point. Those 1,150 members who never appeal? **Today the plan does not pay for their care.** Approving them correctly *increases* near-term medical spend. On a direct-cost ledger, this product plausibly runs negative in year one.

So the case is not cost savings, and pretending otherwise invites a CFO to kill it in one question. The case is:

- **Star Ratings.** Appeals and member-experience measures feed Stars, against a rating position that has already cost billions.
- **Regulatory standing.** Decision-quality metrics became public in March 2026. They are now comparable across plans, permanently.
- **Litigation exposure.** A system architecturally incapable of producing an unreviewed denial is the opposite of the fact pattern currently in discovery.
- **Provider abrasion.** Directly supports the stated goal of a more consistent provider experience.

**The honest framing: this is a quality and risk investment that carries a modest direct cost, not a savings play.** Any pitch that says otherwise is arguing that Humana should want to be wrong less often *and* spend less money, and those two things point in opposite directions here.

### Where the value lands

- **Avoided rework** — denial letter, appeal intake, clinical re-review, and IRE referral, on care that gets approved and paid anyway
- **Regulatory standing** — decision quality is now a published, comparable metric
- **Stars** — appeals and member-experience measures, against a rating position that has cost billions
- **Provider relations** — directly supports the stated goal of a more consistent provider and member experience
- **Litigation posture** — a system architecturally incapable of producing a denial is the opposite of the fact pattern currently in discovery in *Barrows v. Humana*

---

## 6. What this does not solve

Scope discipline, stated up front so the boundaries are mine rather than the panel's.

- **It does not decide anything.** It surfaces evidence and criteria. A licensed clinician makes every determination, exactly as CMS requires.
- **It does not use a language model where a database query will do.** The model is the third layer, not the first, and it handles only the judgments that require reading.
- **It cannot deny.** The system has no path to producing or recommending an adverse determination. This is an architectural constraint, not a policy.
- **It does not reduce prior authorization volume.** That is a benefit-design lever, and Humana is already pulling it.
- **It does not touch post-acute or concurrent review.** Deliberately out of scope.
- **It does not replace the appeals process.** It aims to reduce avoidable traffic into it.
- **It starts on one service line.** Advanced imaging, beginning with lumbar MRI, where coverage criteria are public, codified, and turn on documented facts. The wedge is narrow on purpose, and it generalises for a structural reason: **most coverage criteria mix ledger facts with clinical judgments** — a duration, a prior trial, a documented non-response — and that split is what the layered design is built around. Adding a criterion is adding a document, not writing code. What limits expansion is validation capacity, not engineering.
- **It does not assume clean claims data.** In production, diagnosis pointers are miscoded, out-of-network and cash-pay care is invisible, and adjudication lags. The claims layer is noisier than this prototype's synthetic version implies, which is part of why the narrative layer exists rather than being an optimisation over it.

---

## 7. The problem statement, one sentence

> When a Humana medical director is about to deny an advanced imaging request, the evidence that would support approval is often already in Humana's possession — some of it in the plan's own claims ledger, some buried in an unitemized fax from a practice the member left months ago. This product assembles it cheapest-first, shows the clinician where every piece came from, and lets the clinician decide.

---

### Sources

- HHS OIG, *Some Medicare Advantage Organization Denials of Prior Authorization Requests Raise Concerns About Beneficiary Access to Medically Necessary Care*, April 2022 — [oig.hhs.gov](https://oig.hhs.gov/reports/all/2022/some-medicare-advantage-organization-denials-of-prior-authorization-requests-raise-concerns-about-beneficiary-access-to-medically-necessary-care/)
- KFF, *Medicare Advantage Insurers Made Nearly 53 Million Prior Authorization Determinations in 2024* — [kff.org](https://www.kff.org/medicare/medicare-advantage-insurers-made-nearly-53-million-prior-authorization-determinations-in-2024/)
- KFF, *Prior Authorization Metrics Provide New Insights into Insurer Practices, but Gaps Remain* — [kff.org](https://www.kff.org/patient-consumer-protections/prior-authorization-metrics-provide-new-insights-into-insurer-practices-but-gaps-remain/)
- CMS, *2024 Medicare Advantage and Part D Final Rule (CMS-4201-F)* — [cms.gov](https://www.cms.gov/newsroom/fact-sheets/2024-medicare-advantage-and-part-d-final-rule-cms-4201-f)
- CMS, *Interoperability and Prior Authorization Final Rule (CMS-0057-F)* fact sheet — [cms.gov](https://www.cms.gov/files/document/fact-sheet-cms-interoperability-and-prior-authorization-final-rule-cms-0057-f.pdf)
- CMS, *LCD L34220 — Lumbar MRI*, Noridian Healthcare Solutions, effective October 23, 2025 — [cms.gov](https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?LCDId=34220)
- CMS, *Parts C & D Enrollee Grievances, Organization/Coverage Determinations and Appeals Guidance* — [cms.gov](https://www.cms.gov/medicare/appeals-and-grievances/mmcag/downloads/parts-c-and-d-enrollee-grievances-organization-coverage-determinations-and-appeals-guidance.pdf)
- AMA, *2025 Prior Authorization Physician Survey*, released May 2026 — [ama-assn.org](https://www.ama-assn.org/press-center/ama-press-releases/ama-survey-prior-authorization-reform-pledge-falls-short-physicians)
- Humana, *Accelerating Efforts to Eliminate Prior Authorization Requirements*, July 2025 — [policy.humana.com](https://policy.humana.com/news-and-resources/news-press/2025/humana-accelerates-efforts-to-eliminate-prior-authorization)
- Healthcare Dive, *Humana could end 2026 as the largest Medicare Advantage insurer*, February 2026 — [healthcaredive.com](https://www.healthcaredive.com/news/humana-medicare-advantage-2026-growth/811917/)
- Healthcare Dive, *Humana's Medicare Advantage star ratings slip for 2026* — [healthcaredive.com](https://www.healthcaredive.com/news/humana-2026-medicare-advantage-star-ratings-slip/801839/)
