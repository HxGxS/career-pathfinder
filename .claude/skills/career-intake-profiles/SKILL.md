---
name: career-intake-profiles
description: Use in the Career Pathfinder project when starting intake from the user's CV or background, asking intake questions, or drafting, changing or presenting career profiles (profile_N.md) for approval.
---

# Intake and career profiles

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

The main instructions always apply. This file adds detail and never relaxes them.

## Ask, don't assume
- Never assume anything about the user. Use only what is in their CV or background, or what they tell you directly. Ask about everything else: preferences, constraints, interests, goals, and what they would or wouldn't accept.
- Confirm what you took from the CV with the user before relying on it (intake step 1).
- If an answer is unclear, or two answers conflict, ask again; never choose an interpretation yourself.
- Unknown date or time zone: ask.

## Intake steps
1. Read the CV or background (attached, pasted or in `workspace/`). Show the user a short summary of what you took from it and ask them to correct anything wrong or missing.
2. Ask about each remaining topic below: one focused question per message, waiting for each answer. If an answer is brief, follow up with an either/or question.
3. Ask the user whether each constraint is mandatory or preferred; don't decide for them.
4. Don't ask for sensitive documents or identifiers you don't need (e.g. passport or ID numbers).

Topics to cover:
- Experience and education: the three most recent examples of each to start; ask about older ones if they could matter.
- Interests and strengths, with evidence.
- CV or portfolio.
- Location, remote or hybrid, relocation.
- Salary floor: currency, pay basis (e.g. hourly or yearly), full-time or part-time.
- Employment type, seniority, hours, travel.
- Work authorisation and sponsorship needs: citizenship or permanent residency in each target country; if neither, the permit type, any limit on weekly hours, earliest start date and the visa's expiry date (used by the right-to-work and permit checks in `.claude/skills/career-scoring/SKILL.md`).
- Languages they can work in, and how well (used by the language check in `.claude/skills/career-scoring/SKILL.md`).
- Career goals: what the next role should build towards.
- Tasks that energise them and tasks that drain them.
- Career gaps, retraining, appetite for a career change.
- One direction or several.
- Transition tolerance: how much preparation time, cost and retraining is acceptable (used for the Effort score in `.claude/skills/career-scoring/SKILL.md`).

## Using interests
An interest can open up a new industry only where the user's existing, evidenced skills fit roles in that industry. Example: a user with experience as a procurement agent and a character artist, interested in anime, sports and fitness → consider procurement or administrative roles at sports or fitness companies, gaming studios, and TV or anime studios. Interest alone never qualifies someone for a role that needs skills they don't have. Before using an interest this way, ask the user whether they want it to shape their search.

## Profiles
- Save each profile in `workspace/` as `profile_N.md` (`profile_1.md`, `profile_2.md` …), status Draft, usually up to 300 words, keeping any detail needed for decisions. Never include contact details, ID numbers or full CV text.
- Fields:
  - Profile ID and target fields
  - Experience
  - Education and mandatory credentials
  - Skills, each labelled: demonstrated / self-reported / learning / inferred transferable
  - Interests
  - Languages (and level)
  - Career goals; energising and draining tasks
  - Mandatory constraints
  - Preferred conditions
  - Work authorisation (status per target country; permit type, weekly-hour limit, earliest start date, visa expiry)
  - Transition tolerance
  - Gaps, career-change appetite, open questions
- "Inferred transferable" skills are your interpretation: keep them separate from stated experience and ask the user to confirm or remove each one.
- Present the most obvious profile first. If the evidence supports several directions, name them and ask which to pursue (each adds its own research budget). Add extra profiles only once the user confirms.
- Maximum three distinct, consistent profiles, at most one mainly a career change. More need the user's approval.
- Only profiles with status Confirmed may be used for research.

## First run: personal.tex

The first time the user runs the workflow, set up the header details every CV and cover letter reads (`.claude/skills/career-cv-template/SKILL.md`). Claude never needs the real details.

1. Tell the user the templates' header fields: first name, last name, phone, email, portfolio link (and the short address shown as its text), and an optional address (CV only).
2. Create the file by running `python3 scripts/setup_tools.py --create-personal` (Windows: `python scripts/setup_tools.py --create-personal`). It copies `templates/personal.tex` (placeholders only) to `workspace/personal.tex`, and only if the file doesn't exist yet; it never overwrites it. Claude never creates, writes or opens `workspace/personal.tex` itself: the project settings block it.
3. Tell the user to open `workspace/personal.tex` in any text editor and choose one of two options:
   - **Keep details private (recommended):** replace each placeholder with a placeholder of the **same length** as the real detail (e.g. `Xxxxxx` for "Ramesh"), so the layout Claude checks is the layout they'll get. When their CVs and cover letters are final, they put in their real details and rebuild each document themselves (README, "What stays private").
   - **Real details now:** put in the real details straight away. Tell them plainly that the finished PDFs Claude builds and checks will then contain those details.
   
   Leave `\myaddress` empty for no address line. Special characters need a backslash (`\&`, `\%`, `\_`, `\#`).
4. Tell the user: Claude never opens that file (the project settings block it), and `.gitignore` keeps it off GitHub.

## Approval (repeated from the main instructions)
Present profiles for corrections. A profile is approved only when the user clearly approves it as shown ("yes", "confirmed", "go ahead" or equivalent); silence, unrelated replies or open corrections don't count. Approval is per profile; others stay Draft. On approval: set status Confirmed, record the approval date in the file, update `profile_N.md` in `workspace/`, note "Profile N approved [date], file profile_N.md" in `workspace/memory.md`, and tell the user what was saved. Ask for approval again after any material change to target roles or mandatory constraints.

## Example
Intake question: "Is your £45,000 floor a hard minimum, or would you take slightly less for fully remote?"
