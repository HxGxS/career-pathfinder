# Career Pathfinder

An AI career-counsellor workflow for AI coding agents, built and tested with [Claude Code](https://claude.com/claude-code). It reads your CV, drafts career profiles for you to approve, finds **verified** live job vacancies for each one, scores how well they fit, keeps everything in an offline dashboard, and, only when you ask, writes a tailored CV and cover letter for a specific role.

> [!NOTE]
> This is an independent project. It is not affiliated with, endorsed by or maintained by Anthropic; Claude Code is named only to describe the tool it runs in.

## What it does

- **Intake and profiles:** builds up to three career profiles from your CV and your answers (it asks rather than assumes), and does nothing further until you approve them.
- **Job research:** about 20 verified roles per profile, from a set of starting-point job sites and employers' own pages. Unverifiable, closed or scam-looking adverts are dropped; possible ghost jobs (reposted adverts) are shown but never counted.
- **Honest scoring:** an eligibility check against your must-haves (including right to work and languages), then a 1-10 fit score with the reasons and gaps. A score describes fit, never your chance of an offer.
- **Tracker and dashboard:** an offline web page with your matches, what needs your attention, and a plain-English glossary. Open it with `python3 scripts/dashboard.py` to edit your own status, next step and notes right on the page. An Excel copy is made when you ask for it.
- **CVs and cover letters:** LaTeX to PDF, built and checked for layout and ATS readability, followed by an independent read-only review. Only the changes you agree to are applied.
- **Never acts for you:** it never applies, contacts anyone, or submits anything. You take every application and outreach step yourself.

## How it works

1. **Intake:** you share your CV; it drafts profiles and you approve them.
2. **Research:** one researcher per approved profile finds, checks and scores roles.
3. **Merge:** duplicates are removed, roles ranked, the tracker and dashboard built, and a career summary written.
4. **Base CV:** one general CV per profile, built from the keywords that keep coming up across its adverts.
5. **Tailored CV and cover letter:** for roles you name, followed by the independent review and your decision on its notes.
6. **Final check:** a checklist runs before anything is delivered.

The rules for each stage are skills in `.claude/skills/`; the workers are subagents in `.claude/agents/`; the main instructions are in `CLAUDE.md` (and `AGENTS.md` for other AI coding tools). Keep these file and folder names as they are: Claude Code looks for them by name.

## What stays private

Everything the workflow saves (your profiles, tracker, CVs, letters and research) lives in `workspace/`, which `.gitignore` keeps off GitHub. Like any cloud AI tool, what the agent reads during the work (for example your CV and job adverts) is sent to the AI model's provider to be processed.

**Your contact details** go in `workspace/personal.tex`. At your first run the agent creates it with placeholders (by running `python3 scripts/setup_tools.py --create-personal`), and it never opens the file. You then open it in any text editor and choose one of two options:

- **Keep your details private (recommended):** replace each placeholder with a placeholder of the same length as your real detail, for example `Xxxxxx` for "Ramesh". The agent builds and checks your CVs and cover letters with these. When a document is final, put your real details into `workspace/personal.tex` and rebuild it yourself, in a terminal opened in this folder:

  | | Mac | Windows |
  |---|---|---|
  | CV | `python3 scripts/build_document.py workspace/cvs/<file>.tex` | `python scripts/build_document.py workspace/cvs/<file>.tex` |
  | Cover letter | `python3 scripts/build_document.py workspace/letters/<file>.tex` | `python scripts/build_document.py workspace/letters/<file>.tex` |

  This runs only on your computer, and the checks print their results in your terminal. If you later ask the agent for a new or changed document while your real details are in the file, its build will contain them; put the placeholders back first if you want to keep them private.
- **Use your real details from the start:** simpler, but the finished PDFs the agent builds and checks will contain your details, so they reach the AI model's provider.

## Requirements

| | |
|---|---|
| **AI coding agent** | [Claude Code](https://claude.com/claude-code) (recommended: the project's safety settings in `.claude/settings.json` only work there), or another AI coding tool that reads `AGENTS.md`; see "Using other AI tools" |
| **Python 3.10+** | For the scripts in `scripts/` |
| **LaTeX** | **Mac: MacTeX** ([tug.org/mactex](https://www.tug.org/mactex/)) (smaller alternatives such as BasicTeX exist, but are more technical and need further package installs). **Windows: MiKTeX** ([miktex.org](https://miktex.org)); in MiKTeX Console, set "Always install missing packages on-the-fly". Both provide `lualatex` (CVs) and `xelatex` (cover letters) |
| **Git for Windows** *(Windows only)* | [git-scm.com](https://git-scm.com/download/win). Claude Code on Windows runs the workflow's commands in its "Git Bash"; without it, every script asks for permission. Needed even if you download the zip instead of cloning |
| **Python add-ons** | `python3 scripts/setup_tools.py --install` installs `pdfplumber`, `pypdf` and `openpyxl` (or `pip install -r requirements.txt`). Windows: use `python` instead of `python3` |
| **Poppler** *(optional)* | `python3 scripts/setup_tools.py --poppler-help` |

Check your setup any time with `python3 scripts/setup_tools.py`.

## Quick start

1. Download or clone this repository, and open **this folder itself** (not a folder above it) in VS Code with your AI coding agent.
2. Run `python3 scripts/setup_tools.py` and install anything it says is missing.
3. In your agent's chat, say something like: *"Here's my CV: workspace/my_cv.pdf. Let's start."*
4. When asked, open `workspace/personal.tex` and fill it in, with same-length placeholders or your real details (see "What stays private").
5. After a search, run `python3 scripts/dashboard.py` to open your dashboard and edit your notes on the page.

## Using other AI tools

The workflow is written for Claude Code. Other AI coding tools can follow it through `AGENTS.md`, but `.claude/settings.json` (the allowed and blocked actions, including the block on opening `workspace/personal.tex`) only works in Claude Code. For other tools, this project includes their own files that block `workspace/personal.tex`:

| Tool | Where |
|---|---|
| Cursor | `.cursorignore` |
| Gemini CLI | `.geminiignore` |
| OpenAI Codex | `.codex/config.toml` (mark the project as trusted in Codex so it's read) |
| GitHub Copilot | No file: add `workspace/personal.tex` under your repository's Settings → Copilot → Content exclusion (Copilot Business and Enterprise plans) |

## Folder layout

```
career-pathfinder/
├── CLAUDE.md             main instructions
├── AGENTS.md             pointer for other AI coding tools
├── .claude/
│   ├── settings.json     allowed and blocked tools (Claude Code)
│   ├── skills/           the rules for each stage (one folder per skill)
│   └── agents/           researcher, merger, base CV, CV and letter writer, reviewer
├── .cursorignore         keeps workspace/personal.tex from Cursor
├── .geminiignore         keeps workspace/personal.tex from Gemini CLI
├── .codex/config.toml    keeps workspace/personal.tex from OpenAI Codex
├── scripts/              fetching, safety checks, tracker, dashboard (and dashboard.py to edit on the page), Excel, PDF build and checks
├── templates/            CV and cover letter templates, personal.tex format, fonts
├── tests/                automatic checks for the scripts
├── workspace/            your results (kept off GitHub)
├── requirements.txt      Python add-ons
└── LICENSE               MIT licence
```

## Tests

`python3 -m unittest discover -s tests -v` runs the automatic checks for the scripts. They also run on GitHub for every push (`.github/workflows/ci.yml`).

## Licence

This project is released under the MIT License; see [`LICENSE`](LICENSE).

## Credits

Parts of this repository's scripts and LaTeX templates were adapted from, and parts of its workflow were inspired by, [ai-job-search](https://github.com/ai-job-search-dev/ai-job-search) by Mads Lorentzen. The adapted files are `scripts/robots_check.py`, `scripts/fetch_page.py`, `scripts/page_decode.py`, `scripts/posting_guard.py`, `scripts/job_key.py`, `scripts/verify_pdf.py`, `scripts/verify_layout.py`, `templates/cv_template.tex`, `templates/cover.cls` and `templates/cover_template.tex`. They are used under the MIT License:

<sub>

MIT License

Copyright (c) 2026 Mads Lorentzen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

</sub>
