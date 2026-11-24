---
name: career-cover-letter-template
description: >
  How a Career Pathfinder cover letter is laid out, built and checked: the custom
  cover.cls class (XeLaTeX) with Lato and Raleway fonts, cover_template.tex, the optional
  company address block, headline and subheadings, the itemize pitfall, the one-page
  length rules, special characters and the compile-and-inspect loop. Use whenever
  building, fixing or checking a cover letter's LaTeX or PDF. Triggers on: build cover
  letter, compile letter, letter layout, letter too long, cover.cls.
---

# Cover letter templates and tailoring guide

> **Where things are:** files the workflow saves live in `workspace/` (so `cvs/…` means `workspace/cvs/…`, `profile_N.md` means `workspace/profile_N.md`); scripts are in `scripts/` and are run from the repository root; templates and fonts are in `templates/`. Other skills are in `.claude/skills/<name>/SKILL.md`.

*Contents: Template · Fonts · Document structure · Key commands reference · Known template pitfall · Length · Line spacing · Bullet lists · LaTeX special characters · Building · Compile-and-inspect loop · Important rules*

What the letter *says* is in `.claude/skills/career-writing-style/SKILL.md`; this file covers how it is laid out, built and checked. Colours, fonts, formatting and layout follow `cover.cls` and `cover_template.tex` exactly. The main instructions always apply.

## Template

Cover letters use a custom LaTeX document class (`cover.cls`) with Lato and Raleway fonts, copied from `templates/cover_template.tex` (the class itself is `templates/cover.cls`).

- **Output file:** `letters/<role-key>_letter.tex`
- **Compile with:** **`xelatex`** (`cover.cls` requires `fontspec`)
- The PDF has no title set, as in the original template.

## Fonts

The font folder is set once at the top of `cover.cls` (`\latopath` = `fonts/lato/`, `\ralewaypath` = `fonts/raleway/`), and `build_document.py` places `templates/fonts/` next to the letter when building.

## Document structure

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Cover Letter - [Company], [Role]
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\documentclass[]{cover}
\usepackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{}

\rfoot{Page \thepage \hspace{0pt}}
\thispagestyle{empty}
\renewcommand{\headrulewidth}{0pt}
\input{personal}
\begin{document}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     TITLE NAME
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\namesection{}{\Huge{\myfirstname\ \mylastname}}{  \href{mailto:\myemail}{\myemail} | \myphone |  \urlstyle{same}\href{\myportfolio}{\myportfoliotext}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%     MAIN COVER LETTER CONTENT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Only when the applying office's address was found (posting or company research):
\companyname{[Company]}
\companyaddress{[Applying office address]}

\currentdate{\today}
\section{[Headline: title or education + posting keyword]}

\lettercontent{Dear [First Last / Hiring Manager],}

\lettercontent{[Block 1: opening and why this company]}

\subsection{[Optional subheading]}
\lettercontent{[Block 2: task-solving body, introducing the bullet list]}

{\raggedright\fontspec[Path = \ralewaypath]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont
\begin{itemize}
    \item {[Concrete achievement/skill 1]}
    \item {[Concrete achievement/skill 2]}
    \item {[Concrete achievement/skill 3]}
\end{itemize}\par}
\vspace{6pt}

\lettercontent{[Block 3: company connection and forward-looking close]}

\lettercontent{I look forward to hearing from you.}

\begin{flushright}
% No trailing \\ inside \closing{} - cover.cls appends its own \\, and a
% doubled break triggers "! LaTeX Error: There's no line here to end."
\closing{Kind regards,}

\signature{\myfirstname\ \mylastname}
\end{flushright}
\end{document}
```

- Leave out the company block entirely when no applying-office address was found.
- Use at most two `\subsection` subheadings; each costs lines from the one-page budget.

## Key commands reference

| Command | Purpose |
|---|---|
| `\namesection{}{Name}{contact info}` | Header with name and contact |
| `\companyname{text}`, `\companyaddress{text}` | Company and applying-office address (only when the address is known) |
| `\currentdate{date}` | Date field (use `\today` or an explicit date) |
| `\section{text}` | Headline |
| `\subsection{text}` | Subheading |
| `\lettercontent{text}` | Body paragraph (adds spacing after) |
| `\closing{text}` | Closing line |
| `\signature{name}` | Printed name below the signature |

## Known template pitfall: itemize inside `\lettercontent{}`

The `\lettercontent{}` macro appends `\\` to its argument. This breaks when the argument ends in `\end{itemize}`, because `\\` has no line to break after the environment closes, producing `! LaTeX Error: There's no line here to end.` and no PDF output.

**Wrong (breaks the build):**
```latex
\lettercontent{Here is how my experience maps:
\begin{itemize}
    \item ...
\end{itemize}}
```

**Correct: close `\lettercontent{}` before the list, and wrap the list in the matching Raleway-Medium font so typography stays consistent:**
```latex
\lettercontent{Here is how my experience maps:}

{\raggedright\fontspec[Path = \ralewaypath]{Raleway-Medium}\fontsize{11pt}{13pt}\selectfont
\begin{itemize}
    \item ...
\end{itemize}\par}
\vspace{6pt}

\lettercontent{[next paragraph]}
```

The font wrapper is mandatory. If you just move `\begin{itemize}` outside `\lettercontent{}` without the `\fontspec` block, bullets render in the default body font (Lato) and visually mismatch the rest of the letter.

## Length: hard 1-page limit

- Target: 1 page including the signature block. Maximum: **never exceed 1 page**.
- **Word budget: 250–300 words** of body text (not counting LaTeX markup). This is the safe maximum. **350 words will overflow.**
- **Always count:** the three blocks (`.claude/skills/career-writing-style/SKILL.md`). Add the personal-fit paragraph only if the others are short.
- When adding company-specific content, **trim other content to compensate** rather than adding net length.

## Line spacing

- Add `\usepackage{setspace}` and `\setstretch{1.0}` if the letter is long and needs to fit on one page.
- Use `\vspace{.5cm}` between major sections for readability, only if space permits.

## Bullet lists

- Place `\begin{itemize}...\end{itemize}` **outside** a `\lettercontent{}` block (see the pitfall above), wrapped in the matching Raleway-Medium `\fontspec`.
- 3–5 bullets is ideal.
- Start each bullet with a bold label or an action verb; use `\textbf{Label:}` for category-style bullets.
- A bullet whose text begins with a literal `[` must be braced, `\item {[text]}`. Unbraced, LaTeX parses `[text]` as `\item`'s optional label and renders it off the left page edge, missing from the PDF text layer entirely.

## LaTeX special characters

Escape these wherever they appear in body text:
- Ampersand: `\&` (company names: H\&M). Unescaped, the build fails loudly.
- Percent: `\%` ("grew revenue 30\%"). Unescaped, it does **not** fail: everything after the `%` on that line is silently eaten as a LaTeX comment.
- Dollar `\$`, hash `\#`, underscore `\_`.
- Tilde `\textasciitilde{}`, caret `\textasciicircum{}`, backslash `\textbackslash{}`.

Copied text is always escaped, never pasted in as LaTeX commands. The only files a letter may load are `cover.cls` and `personal.tex`.

## Building

```bash
python3 scripts/build_document.py workspace/letters/<file>.tex
```

(Windows: `python`.) It builds with `xelatex` (shell escape off), then runs `verify_pdf.py` (exactly 1 page, readable text) and `verify_layout.py`, and reports each result.

## Compile-and-inspect loop (mandatory)

After writing the cover letter and before presenting it to the user, always build and visually inspect the PDF. Iterate until the layout is clean:

1. Build with `build_document.py`.
2. Confirm the page count is **exactly 1** and the build succeeded.
3. Read the PDF and visually check: the signature fits at the bottom, no text is cut off, the bullet font matches the body.
4. If it overflows, trim text first (within the word budget), then line spacing.

## Important rules

1. **`xelatex`; exactly 1 page,** signature included; 350 words will overflow.
2. **Never put a list inside `\lettercontent{}`;** always wrap lists in the Raleway-Medium font block.
3. **Company block only** with the applying office's address.
4. **Headline with `\section`; at most two `\subsection` subheadings.**
5. **Escape every special character;** load nothing except `cover.cls` and `personal.tex`.
