# Service Design — Current State and Future State

**Deliverable 2 of 5 · Humana AI Product Manager Take-Home**
**Subject:** Margaret Ellison, 72, Medicare Advantage HMO. Lumbar MRI (CPT 72148), LCD L34220.

One member, one request, followed end to end. The volume numbers say this happens ~930,000 times a year at Humana. The named case is here because a swimlane diagram does not make anyone feel the 194 days.

---

## Before the request exists

This part is identical in both states. It matters because it establishes that **Margaret qualified from the beginning.**

| Date | What happened |
|---|---|
| Feb 18 | Dr. Whitfield refers her to physical therapy for low back pain |
| Feb 24 – Apr 4 | Eight PT visits over six weeks at Cascade Valley. Humana pays every claim |
| Mar 2 | Meloxicam started, still ongoing |
| Apr 4 | PT discharge: *"0 of 3 functional goals met… symptoms have not responded to conservative management."* Therapist recommends further workup |
| Jul 30 | Lumbar X-ray: degenerative changes, no acute finding |
| Aug 12 | Office visit. Left leg symptoms now progressive. Dr. Whitfield orders MRI |

By August 12, LCD L34220 is satisfied. A four-week trial of conservative management occurred and the patient did not respond. **Humana paid for the therapy that proves it.**

---

## CURRENT STATE

### Timeline

| Day | Date | Member | Provider | Plan |
|---|---|---|---|---|
| 0 | Wed Aug 26 | — | Submits PA request + 14-page fax of outside records | Request received, clock starts |
| 2 | Fri Aug 28 | — | — | **Nurse review.** Referring note says only *"has tried therapy in the past."* No dates, no duration. Cannot substantiate the four weeks. Routes to medical director |
| 6 | Tue Sep 1 | — | — | **Medical director denies.** Reason: insufficient documentation of conservative management (C2) |
| 7 | Wed Sep 2 | — | — | Denial letter issued. **Clock met — this looks like a success in the operating metrics** |
| 8 | Thu Sep 3 | Receives letter. Does not understand it. Calls the office | Receives denial | — |
| 15 | Thu Sep 10 | Waits | Staff assemble appeal packet — the same records, re-sent | Appeal intake |
| 43 | Thu Oct 8 | — | — | **Reconsideration: overturned.** MRI approved |
| 50 | Thu Oct 15 | MRI performed | — | Care paid for |

### What it cost

| | |
|---|---|
| Request to imaging | **50 days** |
| Appeal filed to overturn | 28 days |
| PT discharge to imaging | **194 days** |
| Clinical reviews of the same case | 2 |
| Times the same records were sent | 2 |
| Cost of the care | Identical either way |

### The failure, isolated

The whole thing turns on **Friday, August 28, at the nurse review.**

She reads the referring physician's note. It says *"has tried therapy in the past."* That is unverifiable, so she cannot approve, so she routes to the medical director — correctly, and in accordance with policy.

Meanwhile:

- Page 9 of the 14-page fax is a PT discharge summary documenting six weeks and explicit non-response
- Humana's own claims system holds eight paid therapy claims spanning 5.4 weeks
- The medication list shows meloxicam since March

**Nobody did anything wrong.** The nurse followed policy. The medical director reviewed what was in front of him. The provider submitted the records. The evidence was in the building the entire time, in three places, and the process had no way to surface it inside a seven-day clock.

### The uncomfortable part

**This is the good outcome.**

Margaret's provider filed an appeal. Only ~11.5% of denials are appealed. For the other ~88% — roughly 823,000 Humana denials a year — the journey ends on day 7 with a letter, and the care simply does not happen.

Filing an appeal takes initiative, paperwork, time, and usually an advocate. Margaret had a practice with staff who could do it. **The current-state map is the journey of a member who got lucky.**

---

## FUTURE STATE

Everything before Day 2 is unchanged. Everything after the decision is unchanged. **One screen changes, for one person, at one moment.**

### Timeline

| Day | Date | Member | Provider | Plan |
|---|---|---|---|---|
| 0 | Wed Aug 26 | — | Submits PA request + 14-page fax | Request received, clock starts |
| 2 | Fri Aug 28 | — | — | **Nurse review — unchanged.** Cannot substantiate the four weeks. Routes to medical director |
| — | | | | ↓ *evidence assembled before the case reaches the queue* |
| 5 | Mon Aug 31 | — | — | **Medical director review, with evidence assembled.** Approves |
| 6 | Tue Sep 1 | Receives approval | Receives approval | Authorization issued |
| 9 | Fri Sep 4 | MRI scheduled | — | — |
| 13 | Tue Sep 8 | MRI performed | — | Care paid for |

### What happens between Day 2 and Day 5

Three layers run, cheapest first:

**Layer 1 — Claims query.** Eight paid therapy claims, Feb 26 to Apr 4, 5.4 weeks, all carrying lumbar diagnosis pointers.
→ *Duration condition satisfied, from Humana's own ledger. No reading, no model, no inference.*

**Layer 2 — Structured checks.** No prior lumbar MRI in the lookback. No red-flag indicators. Meloxicam active since Mar 2.
→ *No exclusion applies.*

**Layer 3 — Narrative reading.** The LCD also requires *non-response*, which no claim can establish. The model reads the full packet and returns a verbatim quotation from page 9 with its document and page reference. The quoted string is verified against the source before it is displayed.
→ *Non-response condition satisfied.*

**What the medical director sees:** the criterion, both conditions marked satisfied, the claims ledger for one, the quoted passage for the other, and a click that jumps to page 9 with the sentence highlighted. He reads the actual therapist's words, not a confidence score.

He approves. The case took about four minutes.

### What changed and what didn't

| | Current | Future |
|---|---|---|
| Member does | Nothing different | Nothing different |
| Provider submits | Same packet | Same packet |
| Nurse reviews | Same criteria, same routing | **Unchanged** |
| Who decides | Medical director | **Medical director** |
| What the MD sees | An unsorted 14-page fax | Assembled evidence with sources |
| Time to imaging | 50 days | **13 days** |
| Clinical reviews | 2 | 1 |
| Appeal | Filed, overturned | Never needed |

**Nobody's job changes. One person's screen changes.** That is the point, and it is worth saying out loud — service designs that require six teams to work differently do not ship.

---

## The other two journeys

A single happy path is not a service design. Two more, deliberately.

### Robert Cheng — the layers disagree

Lumbar radiculopathy, five weeks. Nurse routes for no documented conservative management.

- **Claims layer:** 21 paid therapy claims over eight weeks — but every one carries diagnosis pointer Z96.651, *right knee arthroplasty*. No lumbar conservative management. **Correct.**
- **Narrative layer:** finds a complete, well-formatted PT discharge summary with formal goals and lumbar mentions in the postural assessment. Flags it as documented conservative management. **Wrong** — the therapy treated his knee.

**The system shows both, marked as conflicting, and resolves nothing.** The medical director reads the diagnosis pointers, sees the error in seconds, overrides, and records the reason: *therapy was post-operative knee rehabilitation, not conservative management for the lumbar complaint.*

The denial is correct and the override is captured as a labelled example.

Two things this journey proves: the model's errors are **legible** — a context mistake a clinician spots immediately, not a fabrication — and the human is a decision-maker rather than a rubber stamp. Silently deferring to the claims layer would have been simpler and usually right, and would have hidden the case worth looking at.

### Dolores Ramírez — the system stays silent

Repeat lumbar MRI, six weeks after the last one. Symptoms explicitly unchanged, no new findings, no surgical consideration.

- **Claims layer:** a paid claim for MRI lumbar spine on Jul 15. Criterion C3, duplicative imaging, established from the ledger with no reading at all.
- **Narrative layer:** no supporting evidence. Nothing to find, because nothing is there.

The panel reads:

> *No supporting evidence identified in the submitted record. This is not a coverage recommendation.*

The wording matters. If the system stays silent the reviewer proceeds toward denial, so **silence carries weight in the workflow whether or not that is intended.** A system that said "no support found, safe to deny" would be making adverse determinations through the back door. It reports on the record; it never endorses a denial.

The denial is correct. The system contributed nothing to it, which is exactly right.

**And Dolores has limited English and no prior appeals** — the profile least likely to ever challenge a decision. She is the reason first-decision accuracy matters more than appeal accessibility.

---

## Where the solution sits

```
   Provider          Intake         Nurse review        MD review          Decision
   submits    ──►    checks    ──►  vs. criteria   ──► (CMS-mandated) ──►  issued
                                          │                  ▲
                                     routes for              │
                                    adverse determ.   ┌──────┴──────┐
                                          └──────────►│  1 claims   │
                                                      │  2 fields   │
                                                      │  3 narrative│
                                                      └─────────────┘
                                                       assembled evidence,
                                                       every source citable
```

One insertion point. It is the review step **CMS already requires** before any adverse medical-necessity determination — not a new gate, not a new approver, not a new handoff.

The system can surface support. It has no path to producing, recommending, or implying a denial. That is architecture, not policy: there is no code path from the model to an adverse determination.

---

## What this does not fix

- **Margaret still waits 13 days.** Faster, not instant. The remaining time is scheduling and the standard clock.
- **The four-week trial still happened.** This changes whether it was *counted*, not whether it was required.
- **Bad submissions are still bad submissions.** If the evidence is nowhere — in claims, in fields, or in the narrative — nothing surfaces, correctly.
- **Real claims data is messier than this.** Miscoded diagnosis pointers, invisible out-of-network and cash-pay care, adjudication lag. The claims layer would be noisier in production, which is part of why the narrative layer exists rather than being an optimisation over it.
- **The upstream problem is untouched.** The cheapest fix is structured submission so nothing is buried in the first place — and CMS-0057-F's Prior Authorization API pushes that way from January 2027. Some of this product's value decays as that lands. Unstructured outside records will not disappear for years, and the API standardises the envelope, not the clinical narrative inside it.
