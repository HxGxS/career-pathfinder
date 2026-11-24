---
name: career-cv-template
description: >
  How a Career Pathfinder CV is laid out, built and checked: the moderncv banking
  template (cv_template.tex), personal details from personal.tex, spacing, LaTeX special
  characters, in-progress qualifications, the compile-and-inspect loop, the 1-2 page
  budget, relevance-weighted cutting, section order, ATS text-layer checks and date
  rules. Use whenever building, fixing or checking a CV's LaTeX or PDF, including base
  CVs. Triggers on: build CV, compile, CV layout, page break, too long, ATS check,
  moderncv, CV PDF.
---

# CV templates and tailoring guide

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: Template · Personal details · Preamble · Spacing inside itemize lists · In-progress qualifications · LaTeX special characters · Building · Compile-and-inspect loop · ATS parseability · Date fields · Page budget · Relevance-weighted cutting · Section order · Important rules*

What each section *says* is in `.claude/skills/career-writing-style/SKILL.md`; this file covers how it is laid out, built and checked. Colours, fonts, formatting and layout follow `cv_template.tex` exactly. The main instructions always apply.

## Template

All CVs use the **moderncv** LaTeX package with the **"banking"** style and **"blue"** colour scheme, copied from `templates/cv_template.tex`.

- **Output file:** `cvs/<role-key>_cv.tex` (tailored) or `cvs/base_profile_N_cv.tex` (base)
- **Compile with:** **`lualatex`** on MiKTeX or TeX Live. `pdflatex` often fails on modern MiKTeX installs with `fontawesome5` font-expansion errors; `lualatex` handles the same sources cleanly.

## Personal details

The header reads everything from `personal.tex`, through `\input{personal}`:

```latex
\name{\myfirstname}{\mylastname}
\ifdefempty{\myaddress}{}{\address{\myaddress}{}{}}
\phone[mobile]{\myphone}
\email{\myemail}
\extrainfo{\href{\myportfolio}{\myportfoliotext}}
```

- Never write personal details into a CV file, and never change `personal.tex`.
- The address line is left out entirely when `\myaddress` is empty: `\address{}{}{}` fails with "There's no line here to end" on every moderncv version.
- The portfolio link shows its own address as text (`\myportfoliotext`), so it appears in the text layer and can be copied.

## Preamble

Keep the preamble exactly as in `cv_template.tex`; its comments explain each part. In particular:

- **Colour overrides:** the `\renewcommand*` on `\namefont` and the three `\colorlet` lines are required. Without them, the name and section headings render in black even though `\moderncvcolor{blue}` is set. Don't drop them. Both names render bold; for regular weight, change `\bfseries` to `\mdseries` in the `\namefont` line.
- `\ifpdftex\usepackage[T1]{fontenc}\fi` keeps accented letters correct in the text layer if the CV is ever built with `pdflatex`. Keep it.
- `\hypersetup` stays inside `\AtEndPreamble`, with `pdfpagemode=UseNone`. The PDF title is "<first name> <last name> - CV", taken from `personal.tex`.
- `\usepackage{needspace}` must be loaded (see the compile-and-inspect loop).

## Spacing inside itemize lists (important)

**Do not place `\vspace{...}` between `\item` entries in an `itemize` list.** It occasionally produces a noticeably oversized gap before a single item. Remove the inter-item `\vspace` and let `itemize` use its native uniform spacing.

```latex
% WRONG - intermittently produces an oversized gap before one bullet
\begin{itemize}
\item \textbf{Foo}: ...
\vspace{1pt}
\item \textbf{Bar}: ...
\end{itemize}

% RIGHT - uniform spacing using the list's native itemsep
\begin{itemize}
\item \textbf{Foo}: ...
\item \textbf{Bar}: ...
\end{itemize}
```

Two related patterns are fine and should be kept:
- `\vspace{1pt}` immediately after `\section{...}` (between the heading and the first item).
- `\vspace{3pt}` between top-level `\cventry` blocks in Professional Experience or Education.

## In-progress qualifications must say so explicitly

**A bare year range is not enough.** An entry reading `2025-2026`, seen partway through 2026, looks like a *finished* degree. A profile statement saying "currently completing…" does not fix it: the education entry is where a reader checks the credential, so it has to stand on its own. State completion inside the entry itself:

```latex
\item{\cventry{2025-2026}{[Degree], [Field]}{[Institution]}{[Location]}{}{\vspace{1pt}
In progress, expected [Month Year]. [Relevant topics]
}}
```

Any consistent form works: `In progress, expected <Month Year>.` / `Expected completion <Month Year>.` / a date field of `2025-present`. Claiming a credential not yet held is a factual misstatement, usually discovered at transcript or reference check rather than at interview. The same applies to in-progress certifications and courses.

## LaTeX special characters (important)

Postings, profile data and research arrive as plain text; the CV is LaTeX. Escape these wherever they land in body text: company names, achievement bullets, skill lists.

| Character | Write | Typical trigger |
|---|---|---|
| `&` | `\&` | company names: H\&M, Bang \& Olufsen |
| `%` | `\%` | quantified achievements: "cut latency by 40\%" |
| `$` | `\$` | salary and cost figures |
| `#` | `\#` | "ranked \#1", C\# |
| `_` | `\_` | file names, code identifiers |
| `~` | `\textasciitilde{}` | URLs, "approx. 5 years" tildes |
| `^` | `\textasciicircum{}` | version strings, maths |
| `\` | `\textbackslash{}` | rare |

- **`%` fails silently.** An unescaped `%` starts a LaTeX comment: the build succeeds with zero errors, and everything after the `%` on that line vanishes from the PDF. "Cut inference latency by 40% and saved DKK 2M annually" renders as "Cut inference latency by 40". Check every `%` in every bullet before building.
- **`&` fails loudly** inside `\cventry` (alignment-tab errors, `Missing } inserted`). Escape employer names up front.
- A bullet whose text begins with a literal `[` must be braced, `\item {[text]}`, or LaTeX reads the bracketed text as `\item`'s optional label and renders it clipped off the left page edge with a clean build.
- **Safety:** copied text is always escaped, never pasted in as LaTeX commands. The only file a CV may load is `personal.tex`; `build_document.py` refuses anything else.

## Building

```bash
python3 scripts/build_document.py workspace/cvs/<file>.tex --keywords "term 1" "term 2"
```

(Windows: `python`.) It builds with `lualatex` (shell escape off), then runs `verify_pdf.py` (page count, text layer, date dashes, keywords) and `verify_layout.py` (orphaned entries, holes, early page ends, thin final page, footer collisions), and reports each result.

## Compile-and-inspect loop (mandatory)

After writing the CV and before presenting it to the user, always build and visually inspect the PDF. Iterate until the layout is clean:

1. Build with `build_document.py`.
2. Check the page count: **1 or 2 pages, never more.**
3. Read the PDF and visually inspect every page.
4. Check for **orphaned entries**: a `\cventry` title line must never sit alone at the bottom of page 1 with its bullets on page 2.

**Problem: entry title on page 1, bullets orphaned to page 2.** Add `\needspace{5\baselineskip}` immediately before the problematic `\cventry`:

```latex
\needspace{5\baselineskip}
\item{\cventry{YEAR-YEAR}{Role Title}{Organization}{Location}{}{...}}
```

**Caveat: use `\needspace` before entries, never before `\section` headings.** A section-level `\needspace` pushes the entire section to the next page whenever the request does not fit, stranding empty space and typically *adding* a page. Apply it only to the individual `\cventry` that orphans, and only after a build shows the orphan.

**Problem: one trailing section spills to page 3.** Add `\enlargethispage{2\baselineskip}` (up to 3) before a late section to stretch page 2 by a few lines.

**Problem: 3 pages with significant content on page 3.** Cut content; do not compress geometry or `\vspace`. See "Relevance-weighted cutting".

**Problem: a 2-page CV whose content finishes early on page 2 (feels thin).** Restore the highest-relevance item that was previously cut; a CV that ends mid-page 2 looks incomplete. If the honest content fits comfortably on 1 page, a 1-page CV is fine; never pad.

## ATS parseability

Applicant tracking systems (for example **Workday, Greenhouse, Lever, Ashby, SmartRecruiters**) read the PDF's embedded **text layer**, not the rendered page. A CV can pass visual inspection and still extract as garbage. After the layout passes, verify the text layer with `verify_pdf.py` (run by `build_document.py`). Extraction uses `pdfplumber`, then `pypdf`, then Poppler `pdftotext` (always with `-enc UTF-8`). If none is installed, give the user the install command (`.claude/skills/career-cv-cover-letter/SKILL.md`, "Tools") and offer to rerun; report the check as skipped, never passed, only if they decline.

Check in the extraction:

- **Contact details as literal text.** The template's contact icons extract as glyph names (`MOBILE-ALT`, `Envelope`): harmless noise, because the actual details are printed beside them. The failure is a detail carried *only* by an icon or a hyperlink, which is invisible to an ATS. The email and portfolio address must appear as printed text.
- **No garbled output.** `(cid:NNN)` markers or `�` characters mean a font is embedded without a Unicode mapping; an ATS sees the same garbage.
- **Reading order.** The banking style is single-column, so extraction order matches visual order. Sidebars or multi-column layouts can interleave lines.
- **Keyword coverage.** Match the posting's required and preferred terms against the extracted text. Prefer the posting's exact term over a synonym when it is truthfully applicable; ATS matching is often literal. Never add a keyword the profile does not support. `--contains` ignores LaTeX's typographic substitutions (curly apostrophes, dashes) when comparing; the dumped text is the raw layer the ATS sees.
- **Accents intact.** Keep the T1 line in the preamble, in case of a `pdflatex` build.

## Date fields must be ASCII ranges (confirmed ATS import failure)

This fails **silently**: a CV that passes every other check can still have its dates dropped when imported into an applicant system (a real Workday import lost a role's end date and every education entry). Two independent causes:

1. **`--` in a `\cventry` date renders as an en dash, not a hyphen.** Many parsers split date ranges only on an ASCII hyphen. Write the date argument with a **single hyphen**:

   ```latex
   \item{\cventry{2016-2024}{Role Title}{Organization}{Location}{}{...}}   % parses
   \item{\cventry{2016--2024}{Role Title}{Organization}{Location}{}{...}}  % en dash, may not
   ```

   `verify_pdf.py --ascii-dates` scans the raw text layer for a year joined to a Unicode dash and fails, naming each one.
2. **A bare single year gives the parser no end date.** Use an explicit range, with months where the role ran under a year:

   ```latex
   \item{\cventry{Mar 2016 - Jul 2016}{Contract Role}{Client}{Location}{}{...}}
   ```

   Where a genuine range exists, use it. Do not invent a start date you do not have. After extracting the text layer, confirm every experience entry shows a start *and* an end.

**Exception (the user's decision): education completed more than 6 years ago shows no dates.** Leave its date field empty (`\cventry{}{[Degree]}…`). An applicant system will ask for those dates to be typed in by hand; that is accepted. Don't "fix" it by adding dates back.

## Page budget (1 or 2 pages)

Standard amounts:

| Section | Standard |
|---|---|
| Profile statement | 3–4 lines |
| Core competencies | 5–6 items, each 1–2 lines |
| Most recent role | 4–5 bullets |
| Previous role | 3–4 bullets |
| Older roles | 2–3 bullets |
| Education | 2–3 entries |
| Publications | 2–3 entries |
| Honours and awards | 3 entries, single line each |

If the standard amounts run past 2 pages, trim with relevance-weighted cutting. **If in doubt, cut rather than squeeze:** reducing `\vspace` or geometry scale to force-fit content makes the CV look cramped.

## Relevance-weighted cutting (the right way to shrink a CV)

**Cut by signal, not by section.** An older-role bullet that speaks directly to the posting is worth more than a recent-role bullet that does not. For every candidate line, score three things:

1. **Relevance to this posting:** does it hit a named tool, keyword or stated responsibility in the advert? (For a base CV, the profile's keyword list.)
2. **Uniqueness:** is it the only place this claim appears, or is it duplicated elsewhere?
3. **Narrative load:** does the cover letter depend on it? If cutting it would force a cover-letter rewrite, it is load-bearing.

Cut the lowest-scoring line first, regardless of section.

**Practical order of cuts (easiest to last resort):**

1. **Redundancy.** An achievement in both Core Competencies and a role bullet: the Core Competencies version is usually the cleaner cut (the experience bullet is more concrete evidence).
2. **Profile-statement fluff.** A sentence that just restates what another section shows ("Peer-reviewed publications on X..." is already a Publications entry; the profile can claim it once and stop).
3. **Low-relevance experience bullets**, wherever they sit.
4. **Low-relevance supporting content:** an older-role bullet that doesn't speak to the target role; a certification that doesn't touch the posting's stack.
5. **Low-relevance publications.** Keep 1–2 that best match the posting.
6. **Last-resort structural cuts:** oldest education entry; tightening an older role to 2 bullets; collapsing certifications into one line.

**Pitfalls to avoid:**
- Don't mechanically cut from the bottom of a fixed section list without checking relevance.
- Don't cut the one concrete example the cover letter leans on. Interviewers will have read both.
- Don't cut to fit a borderline overflow (2.02 pages). Prefer `\enlargethispage{2\baselineskip}` on a late section; reserve content cuts for genuine overflow.

## Recommended section order

**Technical roles:** 1. Profile statement · 2. Core competencies · 3. Professional experience (reverse chronological) · 4. Education (reverse chronological) · 5. Publications and awards.

**Domain-specific or specialist roles:** 1. Profile statement · 2. Core competencies · 3. Education (reverse chronological; credentials are a key qualifier) · 4. Professional experience (reverse chronological) · 5. Publications and awards.

## Important rules

1. **`lualatex`; 1 or 2 pages, never 3;** never pad.
2. **Personal details only from `personal.tex`;** omit the address line when empty.
3. **Escape every special character;** load no file except `personal.tex`.
4. **Single-hyphen date ranges with a start and an end;** education over 6 years old has no dates.
5. **Never add a keyword the profile doesn't support.**
6. **Inspect every build** until clean; a skipped check is reported as skipped.
