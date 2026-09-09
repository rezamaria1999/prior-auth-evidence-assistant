# Key Tradeoff

**Deliverable 5 of 5 · Humana AI Product Manager Take-Home**
*Written as presentation content. Roughly three minutes spoken.*

---

## The tradeoff in one line

> **I built a system that can only ever argue for approval — never for denial. That asymmetry is the reason it works, and it is also the reason it raises near-term medical spend.**

The design choice and the financial consequence are the same decision seen from two sides. That is what makes this one tradeoff rather than two.

---

## What I gave up

**Half the use cases.** A symmetric tool — one that also surfaced support for *denial* — would help a reviewer act on cases that genuinely should be denied but arrive as a disorganised 40-page packet. That is real reviewer value and this product cannot deliver it. There is no code path from the model to an adverse determination, deliberately.

**The cost-savings story.** And this is the part worth saying out loud rather than waiting to be asked.

Per 10,000 denials in a service line:

| | |
|---|---|
| Wrongly denied, if OIG's 13% holds | 1,300 |
| Appealed → overturned | ~120 — corrected today, at the cost of an appeal cycle |
| **Never appealed** | **~1,150 — never corrected** |

Today Humana does not pay for the care of those 1,150. **Approving them correctly increases medical spend.** A symmetric tool would recoup some of that on the denial side. This one, by construction, cannot. **On a pure medical-cost ledger, this product runs negative.**

---

## What I bought

**Revenue, through Stars — but the argument has to be made carefully, because the obvious version of it is wrong.**

### The near-term mechanism is real, and it runs backwards from how it sounds

**Reviewing Appeals Decisions** is the percentage of the time the Independent Review Entity **upholds the plan's denial.** Higher is better. Five stars requires 100%, and a single overturn at a small denominator drops you three stars.

Wrong denials are precisely what the IRE overturns. Prevent one at the first decision and that case never enters the denominator at all. **The product improves the measure by removing the losing cases from the pool, not by winning them.** It carries a weight of 2, the same as the CAHPS measures.

### And it has an expiry date, which I would rather state than be caught on

The CY2027 final rule removes **eleven administrative-process measures beginning with the 2027 measurement year and 2029 Star Ratings** — both appeals measures among them. CMS's stated reason is that they no longer distinguish between plans: industry performance moved 88%→95% and 90%→96%.

Run that against the roadmap honestly and the conclusion is uncomfortable: **the appeals measures are retired before this product could plausibly move them.**

### So the durable argument is the one CMS just made itself

**CMS deleted the measures about whether you processed the appeal correctly, and kept the measure about whether the member got the care.** *Getting Needed Care* survives, and its relative influence in the composite rises as the administrative measures come out — CMS said explicitly that the intent was to refocus on "clinical care, outcomes, and patient experience where meaningful performance differences exist."

That is this product's thesis, arrived at independently by the regulator. The appeal is the diagnostic, not the cure.

**The honest weakness, and it should be said out loud:** "a member who gets appropriate imaging in 13 days instead of 50 answers a CAHPS survey differently" is a looser causal chain than the uphold-rate mechanism. This trade gives up a tight mechanism with a deletion date for a looser one that persists. I would rather own that than have it found.

### On scale — the version that survives a CFO

Humana's share of members in 4+ star plans went from 94% to 20%, the company has said the cumulative impact runs to billions, and has publicly targeted top quartile for 2027.

**I am not claiming this product recovers that.** One service line moving one measure among dozens is a small contribution to a large recovery, and anyone who presents it otherwise is overselling. The claim is narrower and it is enough: the medical-spend increase at one service line is order-of-magnitude single-digit millions, which is small enough that this does not need to move billions to be worth doing. It needs to move the right measure in the right direction at a cost that does not require a business case to justify.

**Plus one thing that is real but harder to price:** a system structurally incapable of producing an unreviewed denial is the opposite of the fact pattern currently in discovery across the industry.

---

## Why I made it

Not because of the litigation. Because **the error costs are already asymmetric, so the tool should be too.**

| If the system is wrong… | Cost |
|---|---|
| It surfaces support for approval that doesn't hold up | A few minutes of a clinician's time |
| *(hypothetical)* It surfaced support for denial that didn't hold up | A member loses care they were entitled to |

Those are not the same magnitude and no threshold tuning makes them the same. When the consequences of error are asymmetric, building a symmetric tool means accepting the worse error to gain the lesser benefit.

Three things follow from that rather than driving it:

- **Regulatory fit.** California SB 1120 and the direction of state AI-in-UM legislation point at exactly this line — AI may inform, a licensed clinician must decide.
- **Adoption.** Reviewers will use a tool that helps them. They resist one that appears to be auditing them. An approve-only system is unambiguously on their side.
- **Litigation posture.** Falls out of the above rather than motivating it.

---

## What would change my mind

A tradeoff without a reversal condition is a preference.

**If shadow mode showed that inappropriate *approvals* were also common**, the symmetric case gets stronger and this becomes a genuine debate rather than a settled question. I'd want to see the rate before defending the asymmetry any further.

**If the medical spend increase at full scale exceeded the Stars recovery attributable to these measures**, the business case inverts. That attribution is the weakest number in this analysis and I'd want it modelled properly with Humana's own actuarial input rather than my estimate.

---

## The second-order effect

The asymmetry does something beyond limiting the product's scope: **it constrains what the system can be used for later.**

A tool that surfaces evidence in both directions can, under cost pressure, be tuned toward denial. A tool with no code path to an adverse determination cannot — not by a configuration change, not by a threshold adjustment, not by a future product manager under different pressure.

**That constraint is worth more than the use cases it costs**, and it is the reason I would defend it even if the cost analysis came out neutral.

---

## Speaking notes

**Open:** *"The tradeoff I want to talk about is one that costs Humana money, and I'd rather raise it than have you find it."*

**The turn:** after naming the cost, pivot immediately to Stars. Don't leave the negative hanging.

**The line to land:** *"When the consequences of error are asymmetric, the tool should be too."*

**If pressed on cost:** *"At one service line it's single-digit millions. I'm not claiming this recovers the Stars position on its own — one measure among dozens at one service line doesn't do that, and I'd be overselling if I said otherwise. I'm saying the cost is small enough that it doesn't have to."*

**If they know about the measure deletion — and someone might:** get there first. *"Both appeals measures come out from the 2029 Star Ratings, so the near-term mechanism has a deletion date and I'd rather say that than have you find it. What CMS kept is Getting Needed Care. They deleted the measures about processing the appeal and kept the one about whether the member got the care — which is the same judgment I'm making."*

**If asked whether you'd ever build the symmetric version:** *"I'd want to see the inappropriate-approval rate from shadow mode first. If it's material, that's a real debate. But I'd want the approve-only version running and measured before anyone touches the other direction, because once a system can argue both ways it can be tuned, and tuning tends to follow cost pressure."*
