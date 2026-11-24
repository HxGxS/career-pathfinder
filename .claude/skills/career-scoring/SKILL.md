---
name: career-scoring
description: >
  Decides eligibility and fit for every verified Career Pathfinder role: runs the
  right-to-work gate (citizenship, residency, security clearance, sponsorship), checks
  permit limits (weekly hours, start date, visa expiry) and every other mandatory
  constraint, labels the role Eligible / Eligibility unclear / Ineligible, and gives it a
  1–10 fit score and verdict. Also covers a detailed evaluation of one role when the user
  asks. Use before giving any role (including ghost jobs) an eligibility label, score or
  verdict. Triggers on: score, fit score, eligible, eligibility, ineligible, right to
  work, visa, sponsorship, citizenship, security clearance, evaluate this job, is this a
  good fit, tell me more about role.
---

# Eligibility and fit scoring

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: Order · Right-to-work gate · Permit limits · Other mandatory constraints · Eligibility label · Fit score · Verdict · What to record · Detailed evaluation · Important rules*

Used at step 6 of every search round in `.claude/skills/career-job-search/SKILL.md`, after a role passes `.claude/skills/career-verification/SKILL.md`, and for every verified role, including ghost jobs. How visa wording is recorded and sourced is in `.claude/skills/career-verification/SKILL.md` ("Work authorisation"); this file decides what it means. The main instructions always apply.

**Why eligibility comes first:** a strong fit score must never hide a deal-breaker. And the score is a directional guide to fit, never a prediction of being hired.

## Order (every role, every profile)

1. Right-to-work gate
2. Permit limits
3. Other mandatory constraints
4. Eligibility label
5. Fit score and verdict (Eligible and Eligibility unclear roles only)

## 1. Right-to-work gate

Asks: **is the user permitted to hold this job at all?** Skip it if the profile says the user is a citizen or permanent resident of the country the job is in, and record "skipped: citizen/PR".

Otherwise, read the posting's eligibility wording **word for word** and classify:

| Posting says | Result |
|---|---|
| Citizenship or permanent residency required ("must be a citizen of…", "PR required", "full working rights" where it clearly means citizen/PR) | **Fail**: quote the wording |
| A security clearance is required | **Fail** if an official source shows that clearance needs a citizenship the user lacks (cite it); otherwise **Unknown** |
| Names the user's permit type, or "we sponsor", "visa holders considered", "international applicants welcome" | **Pass**: note it as a positive for the application |
| Nothing about citizenship, residency or sponsorship | **Unknown** |

Two traps:

- **Silence is not permission.** Graduate programmes, professional services, government and defence, banking, telecoms and critical infrastructure often set eligibility on their own website, not in the advert. Silence stays Unknown.
- **A company-wide "international applicants welcome" isn't permission for every role.** It's often followed by a named list of programmes it covers; the result is Pass only if this role or programme is on it.

Wording that could mean either (e.g. "full working rights" with no explanation) is Unknown, not Fail. Use the employer's own eligibility page only if it was already fetched; don't spend extra searches here. No further right-to-work check is run later; for Eligibility unclear roles, the CV stage only reminds the user (`.claude/skills/career-cv-cover-letter/SKILL.md`).

## 2. Permit limits

Asks: **can the user work the hours and dates this job needs?** It's a separate question from the gate, with a different answer. Check only what the profile records:

- weekly hour limit vs the role's hours (e.g. a 20-hour term-time cap vs a full-time role)
- earliest start date vs the role's start date
- visa expiry vs the contract length (or a permanent role)
- sponsorship needed vs a posting that's silent on it → Unknown

Permit limits are legal limits, so they're always mandatory: a known conflict is a failure; a missing detail (hours or start date not stated) is Unknown.

## 3. Other mandatory constraints

Check every other mandatory constraint in the profile: salary floor, location, remote or hybrid, relocation, employment type, seniority, hours, travel, required credentials or licences.

- **Location** comes from intake: within the stated commute or an acceptable remote/hybrid pattern is met; needing relocation fails only if the user ruled relocation out; travel beyond what they accept fails if it's mandatory, or is noted if it's only preferred.
- **Salary** is compared like-for-like, following `.claude/skills/career-verification/SKILL.md`.
- **Languages:** an advert written in, or requiring, a language the user doesn't work in (profile field "Languages") is a failure; quote the requirement.
- Unknown salary, remote terms, credentials or sponsorship **never count as met**.

## 4. Eligibility label

- **Eligible:** evidence supports every mandatory constraint, including the gate and permit limits.
- **Eligibility unclear:** at least one is unknown; none fails.
- **Ineligible:** at least one known failure.

Eligibility is separate from whether the job is still open (that's verification).

**Ineligible roles** aren't scored and don't go in the tracker (unless the user asks for them as labelled comparisons). Record them in the seen list as dropped with the reason, and give each one a single quoted line in the run report and summary, e.g. *"Acme Ltd, Procurement Lead: 'applicants must hold UK citizenship'"*. The user may know something about their own status that the profile doesn't.

## 5. Fit score (1–10)

Score each Eligible and Eligibility-unclear role **per profile**:

| Area | Points | Guide |
|---|---|---|
| **Skills** | 0–3 | 0 fundamental mismatch · 1 partial, significant upskilling needed · 2 most requirements met, 1–2 learnable gaps · 3 core requirements are demonstrated skills |
| **Experience** | 0–2 | Judge by what the work involves, not the job title (a "Data Consultant" and a "Data Scientist" can do the same work). 0 unrelated · 1 adjacent, would need to make the case · 2 direct experience in the same domain and type of role |
| **Career alignment and interests** | 0–2 | 0 conflicts with goals, a backwards step, or unknown · 1 partly aligned with goals or a related interest · 2 clearly builds towards stated goals and/or matches an explicit strong interest. If the tasks are mostly ones the user finds draining, maximum 1 |
| **Preferred conditions** | 0–2 | 0 poor or unknown · 1 partial · 2 strong, evidenced match |
| **Effort** | 0–1 | 0 significant or unresolved preparation · 1 manageable within the user's transition tolerance |

- **Total** = the sum, with a minimum of 1.
- **Unknown** scores 0 but is marked **"U"**: missing information, not incompatibility.
- Scores for **Eligibility unclear** roles are **provisional**.
- Only demonstrated, self-reported or learning skills count, plus inferred skills **the user has confirmed** (`.claude/skills/career-intake-profiles/SKILL.md`). Interest is never competence.
- **A score never overrides a mandatory failure.**

## Verdict

| Score | Verdict |
|---|---|
| 8–10 | Strong fit |
| 6–7 | Good fit |
| 4–5 | Moderate fit |
| 2–3 | Weak fit |
| 1 | Poor fit |

It describes fit, never the chance of an offer. Add "(provisional)" for Eligibility-unclear roles.

## What to record

For each role and profile:

- **Score breakdown**, e.g. `Skills 2 | Experience 1 | Career 2 | Prefs 0U (salary not listed) | Effort 1 = 6 · Good fit (provisional)`
- **Rationale:** one or two sentences citing profile evidence
- **Main gap** and **uncertainty**
- **Right-to-work result:** Pass / Unknown (with quoted wording) / skipped: citizen/PR
- **Permit-limit notes**, if any
- **Ghost-job score**, carried over from `.claude/skills/career-verification/SKILL.md`

## Detailed evaluation (only when the user asks about a specific role)

When the user asks about one role (e.g. "tell me more about role 12"), give:

```
## Job fit evaluation: <role> at <company>

| Area | Result | Notes |
|---|---|---|
| Right to work | Pass / Unknown / skipped | <quoted wording> |
| Permit limits | OK / Unknown / Conflict | |
| Skills | x/3 | |
| Experience | x/2 | |
| Career alignment and interests | x/2 | |
| Preferred conditions | x/2 | |
| Effort | x/1 | |

**Fit: x/10 · <verdict>**

### Key strengths for this role
### Gaps to address
### What would make this clearer
### Recommendation
<1–2 sentences on fit and how to approach it; never the chance of success>
```

Company and culture research belongs to the CV and cover letter stage (`.claude/skills/career-cv-cover-letter/SKILL.md`).

## Important rules

1. **Eligibility before scoring, every time;** the right-to-work gate comes first.
2. **Silence is not permission;** a company-wide welcome isn't permission for a specific role.
3. **Unknowns never count as met;** they score 0 and are marked "U".
4. **A score never overrides a mandatory failure.**
5. **Ineligible roles are reported with their quoted reason,** never silently dropped, and kept out of the tracker.
6. **Fit, never the chance of being hired;** visa notes are never legal advice.
