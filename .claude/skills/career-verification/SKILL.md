---
name: career-verification
description: >
  Decides whether a fetched vacancy counts as Verified for Career Pathfinder, screens it
  for scams, scores reposted adverts for ghost-job risk, flags vague or oversized
  descriptions, and sets the rules for recording dates, salary, visa and work-rights
  notes, and sources. Use whenever a research or merge subagent checks a posting, records
  its details, compares pay with the user's floor, or writes anything about work
  authorisation. Triggers on: verify, verified, is this job real, still open, scam,
  legitimate, ghost job, reposted, vague job description, salary, pay, market rate, visa,
  sponsorship, right to work.
---

# Verification, legitimacy and record-keeping

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: What counts as Verified · Red flags · Ghost jobs · Warning flags · What to record · Salary · Work authorisation · Citing sources · Important rules*

Used at step 6 of every search round in `.claude/skills/career-job-search/SKILL.md`, and by the merge subagent. Recency (14 days), fetching, duplicates and recruiter details live in `.claude/skills/career-job-search/SKILL.md`; this file doesn't repeat them. The main instructions always apply.

**Why this matters:** the user may spend hours on an application, and a fake listing can cost them money or personal data. Only roles that pass this file are shown, listed or counted.

## What counts as Verified

All of these must be true when you check:

- **A specific, accessible job page** for this vacancy. Search previews, generic careers pages, talent pools ("register your interest") and reposts you can't trace to the employer don't qualify.
- **Open when checked:** an active way to apply, no closure notice, and no deadline in the past.
- **A legitimate employer:** no red flags (below).

Prefer the employer's own site or application system; reputable, active job boards are acceptable. Record the source type. "Verified" means observed open when checked, not guaranteed to stay open; say so when it matters.

If any point is uncertain after the fetch escalation in `.claude/skills/career-job-search/SKILL.md`, **drop the role** and record why in the seen list. Never add a newly found Closed role; if a role already in the tracker is found closed, mark it Closed and keep it.

## Red flags (drop the role)

Drop the role, record "failed legitimacy check: <reason>" in the seen list, and count it in the run report:

- the applicant is asked to pay (application, training or equipment fees)
- commission-only pay, or a pyramid or multi-level-marketing structure
- the employer can't be identified
- the application link's domain doesn't match the employer
- bank details or ID documents requested before an interview

Describe what you saw; never call an employer a scam or fraud. The user decides what it means.

## Ghost jobs

A ghost job is an advert that stays up, or keeps being reposted, with no real intention to hire soon. Reposting is the clearest sign, so every verified role gets a **ghost-job score**:

| Points | For |
|---|---|
| 1 per repost | each repost (the original post is not a repost) |
| 1 per full 3 weeks | time since the **earliest version** of the advert was posted (3 weeks = 1, 6 weeks = 2, 9 weeks = 3 …) |
| 1 per unchanged repost | each repost whose description matches the version before it |

| Total | Result |
|---|---|
| **0** | Normal role |
| **1–4** | **Ghost job:** keep it in the tracker, marked with its score and the likely reason (e.g. "Ghost job (3): reposted once, first posted 4 weeks ago, description unchanged"). It is **not counted** towards the profile's 20 roles |
| **5+** | Treat as unverified: **drop it**, and record "ghost-job score <N>" as the reason in the seen list |

Worked examples:

| Advert | Reposts | Age | Unchanged | Total | Result |
|---|---|---|---|---|---|
| Posted once, 5 days ago | 0 | 0 | 0 | 0 | Normal |
| Reposted once, first posted 2 weeks ago, description changed | 1 | 0 | 0 | 1 | Ghost job |
| Reposted once, first posted 4 weeks ago, unchanged | 1 | 1 | 1 | 3 | Ghost job |
| Reposted twice, first posted 7 weeks ago, both unchanged | 2 | 2 | 2 | 6 | Dropped |

- **Evidence only, no extra searches.** Count reposts and dates from what's already at hand: a "Reposted" label on the page, the seen lists and saved files in `job_descriptions/`, and earlier dated copies found in this run's searches. Reposts you never saw can't be counted; the score is "based on evidence found".
- **No earlier text to compare:** add 0 points for "unchanged". Never guess.
- The 14-day recency rule in `.claude/skills/career-job-search/SKILL.md` applies to the **current** advert; age points measure the **earliest** version.

## Warning flags (keep the role, but flag it)

A role can be real and open and still deserve caution. Keep it, add a one-line flag to the role's Notes and the run report, don't change its score, and let the user decide.

1. **Vague description:** you can't tell what the job holder would do day to day or what's required (no concrete duties, no requirements, only generic phrases, or basics like employer, location or contract type missing). Flag: "Vague description: <what's missing>".
2. **Oversized scope:** the duties and requirements would normally be split across **more than three** distinct roles (e.g. procurement lead + software developer + graphic designer + HR + bookkeeper). Flag it and **name the roles it spans**. This can signal unrealistic expectations, an underpaid catch-all, or a listing that isn't a real vacancy.
3. **No dates at all:** neither a posting date nor a deadline.

## What to record

- Canonical URL, source type, posting date **and the advert's original wording** (e.g. "3 days ago"), date found, date verified, deadline.
- Anything missing: "not listed".
- A calculated date: "approx., based on retrieval date <YYYY-MM-DD>". Never use the date you found a role as its posting date.
- Dates as YYYY-MM-DD.

## Salary

- Keep **Listing Salary** (what the posting says) separate from **Market Salary Estimate** (what sources suggest).
- Keep currency, pay period, location, seniority, full-time equivalent, and base vs total pay.
- Estimates need credible, dated, local sources (within the 3 extra salary searches in `.claude/skills/career-job-search/SKILL.md`'s budget); otherwise "not available". Never assume a country; use the posting's location.
- Compare with the user's salary floor only like-for-like. If you convert currency or pay period, state the rate, source and date, and mark it approximate; otherwise treat the comparison as unknown (scored "U" in `.claude/skills/career-scoring/SKILL.md`).
- Never present an estimate as what the employer will pay.

## Work authorisation

- Keep three things separate: the user's stated rights (from the profile), the posting's sponsorship wording, and the legal rules.
- A posting that says nothing about sponsorship means **unknown**, not "no". Existing rights may mean no sponsorship is needed.
- Take legal rules from current official government sources, cited and dated.
- Always say "not legal advice". Never confirm that the user is eligible. If eligibility is unknown, the role is "Eligibility unclear" (`.claude/skills/career-scoring/SKILL.md`).

## Citing sources

- Every role has a source link.
- Outside facts (salary, credentials or licences, demand, legal rules) are cited with link and date. Interpretations cite profile evidence. Hypotheses are labelled.
- **Search previews are leads, not sources:** open the page before using any fact from it.

## Important rules

1. **Verified means observed open when checked;** anything uncertain is dropped.
2. **Red flags and ghost-job scores of 5+ drop the role; ghost jobs scoring 1–4 are shown but never counted; warning flags keep the role with a clear note.** Describe, never accuse.
3. **"Not listed" beats guessing;** the date found is never the date posted.
4. **Salary comparisons are like-for-like, or unknown.**
5. **Visa: never confirm eligibility; always "not legal advice".**
6. **Every outside fact is cited;** previews are never sources.
