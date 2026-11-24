# workspace/

Everything Career Pathfinder saves for your job search lives here: your approved profiles (`profile_N.md`), `memory.md`, the tracker (`career_tracker_*.json`), the dashboard (`career_dashboard_*.html`), the Excel file (only when you ask), saved job descriptions (`job_descriptions/`), research files (`research/`, `company_research/`, `seen_roles_profile_*.csv`), summaries (`career_summary_*.md`), your CVs (`cvs/`) and cover letters (`letters/`), and `personal.tex`.

**Private by design:** this folder is excluded from GitHub by `.gitignore`. Only this README and `.gitkeep` are committed.

**`personal.tex`** holds the details printed at the top of your CVs and letters. It's created at your first run with placeholders (by `python3 scripts/setup_tools.py --create-personal`). Open it in any text editor and replace them with either same-length placeholders or your real details; see the main README, "What stays private". The agent never opens it.
