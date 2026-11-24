#!/usr/bin/env python3
"""Export a Career Pathfinder tracker data file to Excel - only when the user asks.

Reads career_tracker_YYYY-MM-DD[_vN].json and writes the matching
career_tracker_YYYY-MM-DD[_vN].xlsx next to it, with sheets in this order:
Profiles, Glossary, Overview, Roles, Profile Fit, Read Me. See .claude/skills/career-tracker-dashboard/SKILL.md.

Format: every cell centre-aligned (horizontally and vertically, text wrapped); headers
bold at 1.5x the body font size.

Safety: sourced text is written as plain text, never as a formula (values
starting with = + - @ are stored as text), links only to https addresses or the
user's own files, no macros, no formulas, no external connections. After saving,
the file is reopened and its sheets, headers and row counts are checked.

Needs the free openpyxl add-on (`pip install openpyxl`). If it is missing, the
script says so and exits 3: give the user a chat table instead.

Usage:
  python3 scripts/export_excel.py [DATA_FILE_OR_FOLDER] [--out PATH]

Exit 0 saved and checked; 1 saved but a check failed; 2 usage or read error;
3 openpyxl not available.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tracker_schema as ts  # noqa: E402

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:  # handled in main()
    Workbook = None

SHEETS = ["Profiles", "Glossary", "Overview", "Roles", "Profile Fit", "Read Me"]
BODY_SIZE = 11
HEADER_SIZE = BODY_SIZE * 1.5
CATEGORY_FILL = {"Direct": "D9EAD3", "Adjacent": "FFF2CC", "Unexpected": "E4D7F5"}
DATE_KEYS = {"date_posted", "date_found", "date_verified", "deadline", "next_step_date"}
LINK_FILE = {"source_url": "source_url", "job_description_file": "job_description_file",
             "cv": "cv_file", "cover_letter": "letter_file"}
# Columns that get a drop-down list, and where the list comes from.
VALIDATED = {"status": ts.STATUS_VALUES, "eligibility": ts.ELIGIBILITY_VALUES,
             "verification_status": ts.VERIFICATION_VALUES}
MAX_WIDTH = 60


def put(ws, row, col, value):
    """Write one cell as plain data: numbers stay numbers, real dates become
    dates, everything else is text that Excel will never run as a formula."""
    cell = ws.cell(row=row, column=col)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        cell.value = value
        return cell
    s = ts.text(value)
    d = ts.parse_date(s)
    if d is not None:
        cell.value = d
        cell.number_format = "yyyy-mm-dd"
        return cell
    cell.value = s
    cell.data_type = "s"  # stored as text: "=SUM(...)" stays visible text, never a formula
    return cell


def centre():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)


def header(ws, labels):
    for col, label in enumerate(labels, 1):
        c = ws.cell(row=1, column=col, value=label)
        c.font = Font(bold=True, size=HEADER_SIZE)
        c.alignment = centre()
    ws.freeze_panes = "A2"


def finish(ws, n_cols, n_rows):
    if n_rows:
        ws.auto_filter.ref = f"A1:{get_column_letter(n_cols)}{n_rows + 1}"
    for col in range(1, n_cols + 1):
        letter = get_column_letter(col)
        header_len = len(ts.text(ws.cell(row=1, column=col).value)) * 1.5
        longest = max([header_len] + [len(ts.text(ws.cell(row=r, column=col).value)) for r in range(2, n_rows + 2)])
        ws.column_dimensions[letter].width = max(12, min(MAX_WIDTH, longest + 2))
        for r in range(2, n_rows + 2):
            cell = ws.cell(row=r, column=col)
            cell.alignment = centre()
            if not cell.hyperlink:
                cell.font = Font(size=BODY_SIZE)


def link(cell, target):
    href = ts.safe_link(target)
    if href:
        cell.hyperlink = href
        cell.font = Font(color="1F4E79", underline="single", size=BODY_SIZE)


def category_fill(cell, category):
    for name, colour in CATEGORY_FILL.items():
        if name in ts.text(category):
            cell.fill = PatternFill("solid", start_color=colour, end_color=colour)
            return


def role_sheet(ws, roles, keys):
    header(ws, [ts.ROLE_LABELS[k] for k in keys])
    for r_i, role in enumerate(roles, 2):
        for c_i, key in enumerate(keys, 1):
            raw = role.get(key) if key not in ("cv", "cover_letter") else ts.value(role, key)
            if key in ("number", "top_fit_score") and isinstance(raw, (int, float)):
                cell = put(ws, r_i, c_i, raw)
            else:
                cell = put(ws, r_i, c_i, raw if key in DATE_KEYS else ts.value(role, key))
            if key in LINK_FILE:
                link(cell, role.get(LINK_FILE[key]))
            if key == "category":
                category_fill(cell, role.get("category"))
    for c_i, key in enumerate(keys, 1):
        allowed = VALIDATED.get(key)
        if key in ("cv", "cover_letter"):
            continue  # combined "status · file" text; the status lists are in Read Me
        if allowed and roles:
            dv = DataValidation(type="list", formula1='"' + ",".join(allowed) + '"', allow_blank=True)
            letter = get_column_letter(c_i)
            dv.add(f"{letter}2:{letter}{len(roles) + 1}")
            ws.add_data_validation(dv)
    finish(ws, len(keys), len(roles))


def build(data):
    wb = Workbook()
    roles = sorted(data.get("roles") or [],
                   key=lambda r: (["tier1", "tier2", "ghost", "closed"].index(ts.group(r)),
                                  -(r.get("top_fit_score") or 0) if isinstance(r.get("top_fit_score"), (int, float)) else 0))
    ws = wb.active
    ws.title = "Profiles"
    profiles = data.get("profiles") or []
    header(ws, ["Profile ID", "Title", "Approved", "Profile as approved"])
    for r_i, p in enumerate(profiles, 2):
        for c_i, key in enumerate(["id", "title", "approved", "text"], 1):
            put(ws, r_i, c_i, p.get(key))
    finish(ws, 4, len(profiles))

    ws = wb.create_sheet("Glossary")
    header(ws, ["Term", "What it means"])
    for r_i, (term, meaning) in enumerate(ts.GLOSSARY, 2):
        put(ws, r_i, 1, term)
        put(ws, r_i, 2, meaning)
    finish(ws, 2, len(ts.GLOSSARY))
    ws.column_dimensions["B"].width = 90

    role_sheet(wb.create_sheet("Overview"), roles, ts.OVERVIEW_FIELDS)
    role_sheet(wb.create_sheet("Roles"), roles, [k for k, _ in ts.ROLE_FIELDS])

    ws = wb.create_sheet("Profile Fit")
    fits = data.get("profile_fit") or []
    header(ws, [label for _, label in ts.FIT_FIELDS])
    for r_i, f in enumerate(fits, 2):
        for c_i, (key, _) in enumerate(ts.FIT_FIELDS, 1):
            cell = put(ws, r_i, c_i, f.get(key))
            if key == "category":
                category_fill(cell, f.get(key))
    finish(ws, len(ts.FIT_FIELDS), len(fits))

    ws = wb.create_sheet("Read Me")
    R, C = data.get("read_me") or {}, ts.counts(data)
    rows = [
        ("How to read this", "Fit scores (1–10) and verdicts describe fit with the approved profile, never the chance "
         "of an offer. Visa and work-rights notes are not legal advice. Ghost jobs are listed but never counted. "
         "Status, Next Step, Next-Step Date and Notes belong to you: change them by asking the agent in chat, "
         "or on the dashboard when it's opened with scripts/dashboard.py."),
        ("Version", data.get("version")),
        ("Scope", R.get("scope")),
        ("Search budget used", R.get("budget_used")),
        ("Unique roles", C["unique"]), ("Tier 1", C["tier1"]), ("Tier 2", C["tier2"]),
        ("Ghost jobs shown", C["ghost"]), ("Ghost jobs dropped", R.get("ghost_jobs_dropped")),
        ("Closed", C["closed"]), ("In more than one profile", C["overlap"]),
        ("Coverage by profile", "; ".join(f"{k}: {v}" for k, v in C["per_profile"].items())),
        ("Dropped, by reason", "; ".join(f"{k}: {v}" for k, v in (R.get("dropped_by_reason") or {}).items())),
        ("Shortfalls and deviations", "\n".join(map(ts.text, R.get("shortfalls") or []))),
        ("Ineligible roles", "\n".join(map(ts.text, R.get("ineligible") or []))),
        ("Salary and date conventions", R.get("conventions")),
        ("Status values", ", ".join(ts.STATUS_VALUES)),
        ("CV / cover letter status values", ", ".join(ts.DOC_STATUS_VALUES)),
        ("Incident log", "\n".join(map(ts.text, R.get("incidents") or []))),
        ("Notes", "\n".join(map(ts.text, R.get("notes") or []))),
    ]
    header(ws, ["Item", "Detail"])
    for r_i, (k, v) in enumerate(rows, 2):
        put(ws, r_i, 1, k)
        put(ws, r_i, 2, v)
    finish(ws, 2, len(rows))
    ws.column_dimensions["B"].width = 100
    return wb


def check(path, data):
    """Reopen the saved file and confirm sheets, headers and row counts."""
    problems = []
    wb = load_workbook(path)
    if wb.sheetnames != SHEETS:
        problems.append(f"sheet order {wb.sheetnames} != {SHEETS}")
    n_roles = len(data.get("roles") or [])
    for name, keys in (("Overview", ts.OVERVIEW_FIELDS), ("Roles", [k for k, _ in ts.ROLE_FIELDS])):
        ws = wb[name]
        got = [ws.cell(row=1, column=i).value for i in range(1, len(keys) + 1)]
        if got != [ts.ROLE_LABELS[k] for k in keys]:
            problems.append(f"{name}: headers out of order")
        if ws.max_row - 1 != n_roles:
            problems.append(f"{name}: {ws.max_row - 1} rows, expected {n_roles}")
    if wb["Profile Fit"].max_row - 1 != len(data.get("profile_fit") or []):
        problems.append("Profile Fit: row count does not match")
    if wb["Glossary"].max_row - 1 != len(ts.GLOSSARY):
        problems.append("Glossary: row count does not match")
    head = wb["Roles"].cell(row=1, column=1)
    if not (head.font.bold and float(head.font.size or 0) == HEADER_SIZE and head.alignment.horizontal == "center"):
        problems.append("headers are not bold, 1.5x size and centred")
    return problems


def output_path(data_path: Path) -> Path:
    return data_path.with_suffix(".xlsx")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Export the Career Pathfinder tracker to Excel (on request only).")
    ap.add_argument("source", nargs="?", default=".", help="tracker data file, or a folder holding them")
    ap.add_argument("--out", type=Path, default=None, help="where to save (default: next to the data file)")
    args = ap.parse_args(argv)

    if Workbook is None:
        print("export_excel: openpyxl is not available - give the user a chat table instead", file=sys.stderr)
        return 3
    src = Path(args.source)
    data_path = ts.latest_tracker(src) if src.is_dir() else src
    if data_path is None or not data_path.exists():
        print(f"export_excel: no career_tracker_*.json found at {src}", file=sys.stderr)
        return 2
    try:
        data = ts.load(data_path)
    except (OSError, ValueError) as exc:
        print(f"export_excel: cannot read {data_path}: {exc}", file=sys.stderr)
        return 2
    for p in ts.validate(data):
        print(f"problem: {p}")

    out = args.out or output_path(data_path)
    build(data).save(out)
    problems = check(out, data)
    for p in problems:
        print(f"check failed: {p}")
    c = ts.counts(data)
    print(f"counts: unique={c['unique']} tier1={c['tier1']} tier2={c['tier2']} ghost={c['ghost']} closed={c['closed']}")
    print(f"saved={out}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
