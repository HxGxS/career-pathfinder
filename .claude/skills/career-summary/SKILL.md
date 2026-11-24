---
name: career-summary
description: >
  Writes the Career Pathfinder career summary: one plain-English report for the whole
  run, covering every approved profile together: skills translation, career directions
  backed by verified roles, quick wins, a reality check and the tracker counts. Use when
  the merge subagent finishes a run, after a re-run, or whenever the user asks for "the
  summary", "the report", "what did you find" or "my career options". Triggers on:
  summary, report, what did you find, career directions, career options, results overview.
---

# Career summary

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: Purpose · Keyword list · Length and trimming · 1 Skills translation · 2 Career directions · 3 Quick wins · 4 Reality check · 5 Tracker · Writing rules · Important rules*

## Purpose

The summary is the counsellor's advice: it explains what the tracker means for the user (which directions are best supported, why, what's missing, and what to do next). The tracker and dashboard hold the data; the summary is for the user to read and keep.

It is **not** a hand-off or memory: subagents hand over through the profile files, the tracker data file, the seen lists and `workspace/memory.md`, which are exact.

- The merge subagent writes **one summary per run**, covering **all approved profiles together**, after the tracker and dashboard are built.
- Give it in chat **and** save it as `career_summary_YYYY-MM-DD.md` in `workspace/` (`_v2`, `_v3` … for later runs on the same day, never overwritten).
- After a re-run, write a new one if the user asks.

The main instructions always apply, including plain English for everything the user reads.

## Keyword list (before writing the summary)

For each approved profile, run:

```bash
python3 scripts/profile_keywords.py --tracker workspace --profile PN --jd-dir workspace/job_descriptions --out workspace/research/profile_N_keywords.md
```

It counts how many of that profile's verified adverts (Tier 1 and Tier 2) mention each term. Then fill its "Curated keywords" table: keep the 15–20 meaningful terms (skills, tools, qualifications), drop generic phrases, and mark each **supported** (the profile shows it) or **gap**. The base CV subagent uses this list (`.claude/skills/career-cv-cover-letter/SKILL.md`), and the summary may use the gaps (e.g. "14 of 20 adverts ask for SAP, which the profile doesn't show").

## Length and trimming

About **1,200 words**. If it runs long, trim section 2 first, then 3, then 1. **Never cut section 4 or the tracker counts in section 5.**

## 1. Skills translation

3–5 connections between the user's evidence and the roles found, each labelled **demonstrated / self-reported / learning / inferred (confirmed by the user)**. Draw on the skills maps from `.claude/skills/career-job-search/SKILL.md`. Interest is never presented as competence.

## 2. Career directions

5–7 directions across all profiles; if there are fewer, say why. **Every direction must be backed by at least one verified role in the tracker** (Tier 1 or Tier 2); a direction without one is left out. Ghost jobs alone never back a direction.

For each direction:

- **name**, with its category (Direct / Adjacent / Unexpected) and industry
- **why the skills fit**, citing profile evidence
- **essential gaps**
- **entry pathway**, and the verified roles behind it (by tracker #)
- **salary:** labelled *Listing* or *Market estimate*, with location, currency, pay period and source, or "not available" (rules in `.claude/skills/career-verification/SKILL.md`)
- **transition effort:** a **preparation estimate** with its assumptions (time, cost, retraining), never a time-to-offer or a prediction of being hired

## 3. Quick wins

(The keyword gaps from "Keyword list" can point to useful actions.)

Three things the user can do now, each tied to a gap or a promising role, each with a sourced resource (link). These are actions for the user; Claude never applies for jobs or contacts anyone.

## 4. Reality check

(Include the most frequent keyword gaps, with how many adverts ask for each.)

- the best-supported paths, and why
- mandatory constraints that limited the results
- open checks: Eligibility-unclear roles, visa unknowns, salary unknowns
- realistic preparation

Candid and practical: no flattery, no alarm.

## 5. Tracker

- the dashboard file (`career_dashboard_*.html` in `workspace/`), kept in `workspace/` beside the `job_descriptions/`, `cvs/` and `letters/` folders, so its links open; Excel only if the user asks
- **counts:** unique roles · Tier 1 · Tier 2 · ghost jobs shown (not counted) · ghost jobs dropped · Closed
- per-profile coverage against the 20-role target; overlap between profiles
- category counts (Direct / Adjacent / Unexpected)
- rounds and searches used; shortfalls; limitations (sites that failed, scripts that couldn't run, Apify used or not)
- **Ineligible roles:** one quoted line each (from `.claude/skills/career-scoring/SKILL.md`)
- **top three Verified + Eligible roles overall:** title, company, fit score and verdict, a one-line reason, salary type, and source link

The counts must match the data file exactly; `python3 scripts/build_dashboard.py <data file> --check` prints them.

## Writing rules

- Refer to roles by **tracker #**, so the user can find them on the dashboard.
- Cite every outside fact (salary, credentials, demand, legal rules); label anything that is a hypothesis; never invent.
- Scores describe **fit, never the chance of an offer**; visa notes are **not legal advice**.

## Important rules

1. **One summary per run**, covering all profiles; saved to `workspace/` as well as given in chat.
2. **Every direction is backed by a verified role;** none are "exploratory".
3. **Never cut the reality check or the tracker counts.**
4. **Counts match the data file.**
5. **Preparation estimates, never hiring predictions.**
