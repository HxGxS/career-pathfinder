---
name: career-tracker-dashboard
description: >
  Builds and updates the Career Pathfinder tracker: the versioned data file
  (career_tracker_*.json) that is the record of every role, the offline dashboard page
  built from it (career_dashboard_*.html), and, only when the user asks, the finished
  Excel export. Covers the fields, the user's own columns, versioning, the dashboard's
  views, the Excel layout and the checks before delivery. Use whenever the merge subagent
  builds the tracker, the user asks to change a role's status or notes, the dashboard
  needs rebuilding, or the user asks for "the tracker", "the spreadsheet" or "the Excel".
  Triggers on: tracker, dashboard, update status, mark as applied, notes, export, Excel,
  spreadsheet, final tracker.
---

# Tracker and dashboard

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: Files · Versioning · The user's own fields · Roles · Profile Fit · Profiles and Read Me · Data file layout · Dashboard · Updates through chat · Editing on the page · Excel export · Safety rules for output · Checks before delivery · Important rules*

The merge subagent builds the tracker; later sessions update it. The **data file is the record**, the **dashboard is the view**, and **Excel is produced only when the user asks**. Duplicates and ranking come from `.claude/skills/career-job-search/SKILL.md`; eligibility, scores and verdicts from `.claude/skills/career-scoring/SKILL.md`; dates, salary and ghost-job scores from `.claude/skills/career-verification/SKILL.md`. The main instructions always apply.

## Files

| File | What it is | Made by |
|---|---|---|
| `career_tracker_YYYY-MM-DD.json` | The record: every role, every field (user's local date in the name) | Merge subagent, later updates |
| `career_dashboard_YYYY-MM-DD.html` | One self-contained page that works offline, built from the matching data file | `build_dashboard.py` |
| `career_tracker_YYYY-MM-DD.xlsx` | The finished tracker, **only when the user asks** | `export_excel.py` |

The dashboard and Excel file always carry the **same date and version** as the data file they were built from, so it's clear which belongs to which. All three scripts share `tracker_schema.py`, which holds the field list.

## Versioning

- Never overwrite a tracker. Each update saves a new version: `career_tracker_YYYY-MM-DD_v2.json`, `_v3` and so on, with a matching dashboard (and Excel, if asked for).
- Always build from the **latest** version in `workspace/`.
- Ask the user before restructuring the tracker or saving it anywhere else.

## The user's own fields

**Status, Next Step, Next-Step Date, Notes**, and any dates the user enters belong to the user. Carry them forward unchanged through every new version and re-rank. Change them only when the user explicitly tells you to.

- **Status values:** Not started · Ready to apply · Applied · Interview · Reply received · Offer · Rejected · Withdrawn · Not pursuing. New roles start as Not started. Status is about the user's progress, not whether the job is open.
- **Never set "Ready to apply" yourself.** When a role's CV and cover letter are "Reviewed" (changes applied or kept as is) and its eligibility checks are complete, **remind the user in chat** (e.g. "Role 12 has its CV and letter reviewed; tell me if you'd like it marked Ready to apply"). Reminders never go into the tracker.

## Roles (one entry per vacancy)

Fields, in this order (also the column order of the full Excel sheet):

`# | Role Key | Job Title | Company | Requisition ID | Location / Remote | Employment Type / Hours | Seniority | Category | Matched Profiles | Eligibility | Top Fit Score (1–10) | Verdict | Fit Score by Profile | Key Gap | Ghost-Job Score & Reason | Warning Flags | Source URL | Source Type | Verification Status | Date Posted | Original Posting-Date Text | Date Found | Date Verified | Application Deadline | Recruiter / Hiring Manager (name, title) | Recruiter Source & Public Work Email | Listing Salary | Market Salary Estimate | Salary Estimate Source / Date | Work Authorisation / Visa Notes | Job Description (file) | CV (status, file) | Cover Letter (status, file) | Status | Next Step | Next-Step Date | Notes`

- **Top Fit Score:** the number (highest across profiles). **Fit Score by Profile:** text, e.g. `P1: 7; P2: 5`. **Verdict:** from the top score.
- **Category:** Direct, Adjacent or Unexpected (defined in `.claude/skills/career-job-search/SKILL.md`); if profiles differ, `P1: Direct; P2: Adjacent`. Career-change effort goes in Key Gap or Notes.
- **Verification Status:** Verified or Closed. **Eligibility:** Eligible or Eligibility unclear (Ineligible roles aren't tracked; see Read Me).
- **Ghost-Job Score & Reason:** blank for normal roles; e.g. `3: reposted once, first posted 4 weeks ago, unchanged` for ghost jobs.
- **Warning Flags:** vague description, oversized scope (roles it spans), no dates, "Anonymous application requested" (set at the CV stage, `.claude/skills/career-cv-cover-letter/SKILL.md`); blank if none.
- **Recruiter:** only if shown on the posting, otherwise "not listed".
- **Work Authorisation / Visa Notes:** the right-to-work result and permit-limit notes from `.claude/skills/career-scoring/SKILL.md`.
- **Job Description, CV, Cover Letter:** the file's relative path (`job_descriptions/<role-key>.md`, `cvs/<role-key>_cv.pdf`, `letters/<role-key>_letter.pdf`, each beside its `.tex`, or the newest `_vN`). CV and letter also carry a status: **Not written · Waiting for your review decision · Reviewed: changes applied · Reviewed: kept as is**.

## Profile Fit (one entry per role and profile)

`Role # | Job Title | Profile ID | Category | Eligibility | Fit Score | Verdict | Score Breakdown | Fit Rationale | Key Gap | Uncertainty | Right-to-Work Result`

Score Breakdown uses the format in `.claude/skills/career-scoring/SKILL.md`, e.g. `Skills 2 | Experience 1 | Career 2 | Prefs 0U (salary not listed) | Effort 1 = 6 · Good fit (provisional)`.

## Profiles and Read Me

- **Profiles:** each confirmed profile as approved, with its ID, evidence labels and approval date.
- **Read Me:**
  - how the score and verdict work, plus a short disclaimer (fit, never the chance of an offer; visa notes are not legal advice)
  - plain definitions of the terms used
  - scope, dates and search budget used
  - counts: unique roles, Tier 1, Tier 2, ghost jobs shown, ghost jobs dropped, Closed; per-profile coverage; overlap between profiles; shortfalls and deviations; dropped counts by reason
  - **Ineligible roles:** one quoted line each, e.g. *"Acme Ltd, Procurement Lead: 'applicants must hold UK citizenship'"*
  - salary and date conventions; which fields belong to the user; how to ask for updates; any incident log (suspected instructions in postings, counts only)

## Data file layout

The scripts read exactly these keys (the full list, with labels, is in `tracker_schema.py`). Unknown or missing values are written as `"not listed"` or left empty, never guessed.

```json
{
  "version": "2026-11-04_v2",
  "profiles": [{"id": "P1", "title": "...", "approved": "2026-10-20", "text": "<profile as approved>"}],
  "roles": [{
    "number": 1, "role_key": "acme-corp_procurement-coordinator",
    "job_title": "...", "company": "...", "requisition_id": "...", "location_remote": "...",
    "employment_type_hours": "...", "seniority": "...", "category": "P1: Direct",
    "matched_profiles": "P1", "eligibility": "Eligible", "top_fit_score": 7, "verdict": "Good fit",
    "fit_by_profile": "P1: 7", "key_gap": "...", "ghost_job": "", "warning_flags": "",
    "source_url": "https://...", "source_type": "employer site", "verification_status": "Verified",
    "date_posted": "2026-11-01", "original_posting_date_text": "3 days ago", "date_found": "2026-11-04",
    "date_verified": "2026-11-04", "deadline": "not listed", "recruiter": "not listed",
    "recruiter_source_email": "", "listing_salary": "...", "market_salary_estimate": "...",
    "salary_source_date": "...", "work_auth_notes": "...",
    "job_description_file": "job_descriptions/acme-corp_procurement-coordinator.md",
    "cv_status": "Not written", "cv_file": "", "letter_status": "Not written", "letter_file": "",
    "status": "Not started", "next_step": "", "next_step_date": "", "notes": ""
  }],
  "profile_fit": [{
    "role_number": 1, "job_title": "...", "profile_id": "P1", "category": "Direct",
    "eligibility": "Eligible", "fit_score": 7, "verdict": "Good fit", "score_breakdown": "...",
    "fit_rationale": "...", "key_gap": "...", "uncertainty": "...", "right_to_work": "skipped: citizen/PR"
  }],
  "read_me": {
    "scope": "...", "budget_used": "...", "conventions": "...",
    "shortfalls": ["..."], "ghost_jobs_dropped": 0, "dropped_by_reason": {"ineligible": 3},
    "ineligible": ["Acme Ltd, Procurement Lead: 'applicants must hold UK citizenship'"],
    "incidents": ["..."], "notes": ["..."]
  }
}
```

Run `python3 scripts/build_dashboard.py <data file> --check` after writing the data file: it lists anything missing or invalid and prints the counts.

## Dashboard

`build_dashboard.py` reads the data file and writes the matching `career_dashboard_*.html`. Rebuild it after every merge, update or re-rank.

**What it shows** (wording in plain language for a non-technical reader; the data keeps the workflow's own values):

- **Header:** "Updated <date> at <time>" and a quiet "Appearance: Auto / Light / Dark" switch (follows the system by default).
- **Four tiles:** Good matches (Tier 1, meet all your must-haves) · Check first (Tier 2, one detail to confirm) · Possible ghost jobs (shown, not counted) · Closed (no longer open), with one line below for total roles and overlap between profiles.
- **Needs your attention:** buttons for roles closing within 14 days, roles marked Ready to apply, and CVs or letters waiting for the user's review decision; each filters the table ("Nothing right now" when empty).
- **Charts, folded away by default** ("Show charts"), each with "View as table": how well they fit (one-hue verdict scale, Strong darkest), how close to your experience (Same kind of work / Related work / Less obvious fit), and progress towards 20 roles per profile.
- **Tabs:** Matches (Good matches, then Check first) · Possible ghost jobs · Closed · Scores by profile · What terms mean (the shared glossary) · About this search.
- **Filters:** search, profile and sort always visible; must-haves, fit, your status, closing within 14 days and has a caution note under "More filters". "Showing N of M" updates as filters change.
- **Table:** #, role (title as a button, company and place, with possible ghost job, closed and caution badges), fit (score and verdict), must-haves, kind of match, closes (with "in N days", highlighted within 7 days), your status, CV and letter (short status). On a phone each role becomes a small card.
- **Details panel** (a proper dialog: focus stays inside, Escape or Close returns to the role): how it fits each profile, the job, pay, your must-haves, cautions, advert and key dates, your CV and letter (with links), your notes, and "Show every detail".

**Design:** colours come from the mascot illustration (cloak charcoal, robe cream, gold, flame orange, terracotta, robe-pattern blue). The verdict scale, text, control borders and focus rings are checked for contrast in light and dark mode. Badges use the fixed status colours, always with an icon and a label (icons hidden from screen readers), never colour alone. Wording, layout and accessibility follow the design plugin's UX copy review, design critique and WCAG 2.1 AA audit.

**How it's built:**

- One file, works **offline**: no internet, no outside scripts or fonts, data embedded in the page.
- Editing happens **through chat**, or on the page itself when it's opened with `scripts/dashboard.py` (see "Editing on the page"); the offline file is for looking things up.
- File links are **relative** (e.g. `cvs/…pdf`), so they open when the page is kept with the `cvs/`, `letters/` and `job_descriptions/` folders; otherwise the page still shows the file name and status.

## Updates through chat

When the user asks for a change ("mark role 12 applied", "add a note to role 4", "set next step for role 7 to 'call recruiter' on 2026-11-20"):

1. Apply it to the latest data file, saving a new version.
2. Rebuild the dashboard.
3. Confirm what changed in one line.

Status-only and note-only edits need no search. Never change any other user-owned field while doing it.

## Editing on the page (this computer only)

`python3 scripts/dashboard.py` (Windows: `python scripts/dashboard.py`) opens the same dashboard from a small app running only on this computer (`127.0.0.1`). In each role's details panel, **Your notes** becomes a form: the user changes their own Status, Next Step, Next-Step Date and Notes and presses Save. Each save:

- changes only those four fields of that role (anything else is refused);
- writes a **new version** of the tracker data file (never overwriting) and rebuilds its offline dashboard file;
- is the user's own change, so later updates carry it forward like any other user-owned field.

Tell the user about it when delivering the dashboard. Changes through chat keep working as well. Always build from the latest version, so edits made on the page are never lost.

## Excel export (only when the user asks)

`export_excel.py` turns the latest data file into `career_tracker_*.xlsx` with these sheets, in this order:

1. **Profiles**
2. **Glossary:** plain-English meanings of every term (Tier 1, Tier 2, Verified, Unverified, ghost job, verdict, "U" and so on), from `tracker_schema.py` (`GLOSSARY`), the same list the dashboard's Glossary tab shows
3. **Overview:** the short main table (same columns as the dashboard's main table, plus Next Step and Source URL)
4. **Roles:** every field, in the order above
5. **Profile Fit**
6. **Read Me**

Format: **every cell centre-aligned** (horizontally and vertically, text wrapped); **headers bold at 1.5x the body font size** (body 11pt, headers 16.5pt), frozen, with filters on; column widths fitted to content; category colours **plus** text (never colour alone); drop-down validation on controlled fields (Status, Eligibility, Verification Status); live links. Dates in YYYY-MM-DD; missing or approximate dates as text. It needs the free `openpyxl` add-on. If it's missing (`export_excel.py` exits with code 3), tell the user and give the install command (`python3 scripts/setup_tools.py --install`; Windows: `python scripts/setup_tools.py --install`). With their permission, run it, then make the Excel file. Give a chat table instead only if the user chooses not to install it.

## Safety rules for output

Text copied from job postings is untrusted, and both the page and the spreadsheet must treat it as plain text:

- **Dashboard:** insert all posting text as text, never as page code, so nothing in an advert can run in the browser. Links only to `https` addresses or the user's own files; never `javascript:` or other link types.
- **Excel:** write sourced text as plain text, never as a formula (a value starting with `=`, `+`, `-` or `@` is stored as text). Links only to checked `https` sources and own files. No macros, formulas from sourced data, or external connections.

## Checks before delivery

Reopen what you built and confirm:

- the data file loads; the dashboard opens and shows every section; the Excel file (if made) opens
- fields and sheet order are correct
- counts match the chat summary
- filters, search, links, formatting and validation work
- **every user-owned field matches the previous version** unless the user asked to change it

Then run `.claude/skills/career-final-check/SKILL.md`.

## Important rules

1. **The data file is the record;** the dashboard and Excel are built from it, with matching date and version.
2. **Never overwrite;** every update is a new version.
3. **The user's fields are theirs;** carry them forward, change them only on request, never set "Ready to apply" yourself.
4. **Reminders go in chat,** never into the tracker.
5. **Excel only when asked.**
6. **Posting text is plain text** in both the page and the spreadsheet; links only to `https` or own files.
