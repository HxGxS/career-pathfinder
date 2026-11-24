"""Field list and shared helpers for the Career Pathfinder tracker.

One home for the tracker's shape: build_dashboard.py and export_excel.py both
import this file, so a field added or renamed here changes both outputs. The
order of ROLE_FIELDS is the column order of the full Roles sheet in
.claude/skills/career-tracker-dashboard/SKILL.md.
"""

import json
import re
from datetime import date
from pathlib import Path

# (key in the data file, label shown in the dashboard and Excel)
ROLE_FIELDS = [
    ("number", "#"),
    ("role_key", "Role Key"),
    ("job_title", "Job Title"),
    ("company", "Company"),
    ("requisition_id", "Requisition ID"),
    ("location_remote", "Location / Remote"),
    ("employment_type_hours", "Employment Type / Hours"),
    ("seniority", "Seniority"),
    ("category", "Category"),
    ("matched_profiles", "Matched Profiles"),
    ("eligibility", "Eligibility"),
    ("top_fit_score", "Top Fit Score (1–10)"),
    ("verdict", "Verdict"),
    ("fit_by_profile", "Fit Score by Profile"),
    ("key_gap", "Key Gap"),
    ("ghost_job", "Ghost-Job Score & Reason"),
    ("warning_flags", "Warning Flags"),
    ("source_url", "Source URL"),
    ("source_type", "Source Type"),
    ("verification_status", "Verification Status"),
    ("date_posted", "Date Posted"),
    ("original_posting_date_text", "Original Posting-Date Text"),
    ("date_found", "Date Found"),
    ("date_verified", "Date Verified"),
    ("deadline", "Application Deadline"),
    ("recruiter", "Recruiter / Hiring Manager (name, title)"),
    ("recruiter_source_email", "Recruiter Source & Public Work Email"),
    ("listing_salary", "Listing Salary"),
    ("market_salary_estimate", "Market Salary Estimate"),
    ("salary_source_date", "Salary Estimate Source / Date"),
    ("work_auth_notes", "Work Authorisation / Visa Notes"),
    ("job_description_file", "Job Description (file)"),
    ("cv", "CV (status, file)"),                 # built from cv_status + cv_file
    ("cover_letter", "Cover Letter (status, file)"),  # built from letter_status + letter_file
    ("status", "Status"),
    ("next_step", "Next Step"),
    ("next_step_date", "Next-Step Date"),
    ("notes", "Notes"),
]
ROLE_LABELS = dict(ROLE_FIELDS)

# The short main table: dashboard main table, and the Excel Overview sheet
# (which adds next_step and source_url).
MAIN_FIELDS = ["number", "job_title", "company", "location_remote", "eligibility",
               "top_fit_score", "verdict", "category", "deadline", "status", "cv", "cover_letter"]
OVERVIEW_FIELDS = MAIN_FIELDS[:10] + ["next_step"] + MAIN_FIELDS[10:] + ["source_url"]

FIT_FIELDS = [
    ("role_number", "Role #"),
    ("job_title", "Job Title"),
    ("profile_id", "Profile ID"),
    ("category", "Category"),
    ("eligibility", "Eligibility"),
    ("fit_score", "Fit Score"),
    ("verdict", "Verdict"),
    ("score_breakdown", "Score Breakdown"),
    ("fit_rationale", "Fit Rationale"),
    ("key_gap", "Key Gap"),
    ("uncertainty", "Uncertainty"),
    ("right_to_work", "Right-to-Work Result"),
]

STATUS_VALUES = ["Not started", "Ready to apply", "Applied", "Interview", "Reply received",
                 "Offer", "Rejected", "Withdrawn", "Not pursuing"]
ELIGIBILITY_VALUES = ["Eligible", "Eligibility unclear"]
VERIFICATION_VALUES = ["Verified", "Closed"]
DOC_STATUS_VALUES = ["Not written", "Waiting for your review decision", "Reviewed: changes applied", "Reviewed: kept as is"]
VERDICT_VALUES = ["Strong fit", "Good fit", "Moderate fit", "Weak fit", "Poor fit"]
CONTROLLED = {
    "status": STATUS_VALUES,
    "eligibility": ELIGIBILITY_VALUES,
    "verification_status": VERIFICATION_VALUES,
    "cv_status": DOC_STATUS_VALUES,
    "letter_status": DOC_STATUS_VALUES,
}
LINK_KEYS = ["source_url", "job_description_file", "cv_file", "letter_file"]
REQUIRED_ROLE_KEYS = ["number", "role_key", "job_title", "company", "source_url",
                      "verification_status", "eligibility"]

# Plain-English meanings of the tracker's terms, for the Glossary sheet (Excel) and
# the Glossary tab (dashboard). One home: both read this list.
GLOSSARY = [
    ("Good match (Tier 1)", "A real, open role whose must-haves you meet, as far as the advert shows. The strongest group."),
    ("Check first (Tier 2)", "A real, open role where one detail is still unknown (for example the salary or visa wording isn't listed). Confirm it before applying."),
    ("Verified", "Someone checked the role's own advert page and it was open, with a working way to apply. Only verified roles are ever shown."),
    ("Unverified", "A role that couldn't be confirmed as real and open. These are dropped and never shown or counted."),
    ("Closed", "A role you were already tracking whose advert has since closed. Kept so your history stays complete."),
    ("Meets must-haves (Eligible)", "The advert's evidence supports every one of your must-haves."),
    ("One thing to confirm (Eligibility unclear)", "At least one must-have can't be confirmed from the advert, and none clearly fails."),
    ("Ineligible", "The role clearly fails one of your must-haves. Not shown in the tracker; listed in About this search with the advert's own words."),
    ("Possible ghost job", "An advert that seems to stay up or keep being reposted without a real plan to hire soon. Shown separately and never counted towards your 20 roles."),
    ("Ghost-job score", "Points for each repost, every full 3 weeks since the first version, and each repost with an unchanged description. 1 to 4: shown as a possible ghost job; 5 or more: dropped."),
    ("Caution note (warning flag)", "A note of caution on a real role: vague description, duties covering more than three roles, no dates at all, or an anonymous application requested."),
    ("Same kind of work (Direct)", "The same or a closely related kind of work to what you've done."),
    ("Related work (Adjacent)", "A related kind of work or industry where your skills clearly transfer."),
    ("Less obvious fit (Unexpected)", "A less obvious role with a believable link to your experience."),
    ("Fit score (1 to 10)", "How well the role matches your profile: skills, experience, career goals and interests, preferences, and effort. It describes fit, never your chance of an offer."),
    ("Fit (verdict)", "The fit score in words: Strong (8 to 10), Good (6 to 7), Moderate (4 to 5), Weak (2 to 3), Poor (1)."),
    ("U", "Unknown. Missing information scores 0 and is marked U; it is not the same as a mismatch."),
    ("Provisional", "A score for a Check first role that may change once the unknown detail is confirmed."),
    ("Listed pay", "The pay stated in the advert itself."),
    ("Market estimate", "What dated, local sources suggest the role pays. Never a promise of what the employer will offer."),
    ("Right to work", "Whether you are allowed to hold this role at all (citizenship, residency, sponsorship). A guide, not legal advice."),
    ("Permit limits", "Limits from your visa or permit: weekly hours, earliest start date, expiry date."),
    ("Profile (P1, P2, P3)", "One of your approved career directions. A role can fit more than one profile."),
    ("Role key", "A fixed ID made from the company and job title, used to avoid storing the same role twice."),
    ("Reference number (requisition ID)", "The employer's own reference number for the vacancy."),
    ("Posted / found / last checked", "When the employer posted the advert / when it was first found / when it was last checked as open."),
    ("Stale", "A role last checked more than 14 days ago. You're asked before it is checked again."),
    ("CV and letter status", "Not written; waiting for your decision (built and checked, the review is in, and you haven't decided on its notes yet); done, changes applied (you chose some or all of the review's changes); done, kept as is (you kept the documents unchanged)."),
    ("Base CV", "One general CV per profile, built from the keywords that keep coming up across that profile's adverts."),
    ("Your status", "Your own progress on a role (Not started, Ready to apply, Applied, Interview, and so on). Only you change it: by asking in chat, or on the dashboard when it's opened with scripts/dashboard.py."),
]


_TRACKER_NAME = re.compile(r"^career_tracker_(\d{4}-\d{2}-\d{2})(?:_v(\d+))?\.json$")


def safe_link(value) -> str:
    """The link if it is an https address or a relative path to the user's own
    files; otherwise "". Never javascript:, data:, file:, absolute paths or '..'."""
    if not isinstance(value, str):
        return ""
    v = value.strip()
    if v.lower().startswith("https://") and " " not in v:
        return v
    if not v or ":" in v.split("/", 1)[0] or v.startswith(("/", "\\")):
        return ""
    if any(part == ".." for part in re.split(r"[\\/]", v)):
        return ""
    return v


def text(value) -> str:
    """A field as display text; None becomes ''."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def doc_cell(status, file) -> str:
    status = text(status) or "Not written"
    file = text(file)
    return f"{status} · {file}" if file else status


def value(role: dict, key: str) -> str:
    """Display value of one Roles field, combining the CV and letter parts."""
    if key == "cv":
        return doc_cell(role.get("cv_status"), role.get("cv_file"))
    if key == "cover_letter":
        return doc_cell(role.get("letter_status"), role.get("letter_file"))
    return text(role.get(key))


def group(role: dict) -> str:
    """tier1, tier2, ghost or closed - the dashboard section a role belongs to."""
    if text(role.get("verification_status")) == "Closed":
        return "closed"
    if text(role.get("ghost_job")).strip():
        return "ghost"
    return "tier1" if text(role.get("eligibility")) == "Eligible" else "tier2"


def counts(data: dict) -> dict:
    roles = data.get("roles") or []
    out = {"unique": len(roles), "tier1": 0, "tier2": 0, "ghost": 0, "closed": 0}
    for r in roles:
        out[group(r)] += 1
    per_profile = {}
    for p in data.get("profiles") or []:
        pid = text(p.get("id"))
        per_profile[pid] = sum(
            1 for r in roles
            if group(r) in ("tier1", "tier2")
            and pid in re.split(r"[,;\s]+", text(r.get("matched_profiles")))
        )
    out["per_profile"] = per_profile
    out["overlap"] = sum(
        1 for r in roles
        if group(r) in ("tier1", "tier2")
        and len([x for x in re.split(r"[,;\s]+", text(r.get("matched_profiles"))) if x]) > 1
    )
    return out


def validate(data: dict) -> list:
    """Problems that would make the dashboard or Excel wrong. Empty list = fine."""
    problems = []
    if not isinstance(data, dict):
        return ["data file is not a JSON object"]
    for key in ("version", "profiles", "roles"):
        if key not in data:
            problems.append(f"missing top-level key: {key}")
    seen_keys, seen_numbers = set(), set()
    for i, r in enumerate(data.get("roles") or [], 1):
        label = f"role {r.get('number', i)}"
        for key in REQUIRED_ROLE_KEYS:
            if text(r.get(key)).strip() == "":
                problems.append(f"{label}: missing {key}")
        for key, allowed in CONTROLLED.items():
            v = text(r.get(key))
            if v and v not in allowed:
                problems.append(f"{label}: {key} '{v}' is not one of {allowed}")
        for key in LINK_KEYS:
            v = text(r.get(key))
            if v and v != "not listed" and not safe_link(v):
                problems.append(f"{label}: {key} is not an https address or a relative file path")
        if r.get("role_key") in seen_keys:
            problems.append(f"{label}: duplicate role_key {r.get('role_key')}")
        if r.get("number") in seen_numbers:
            problems.append(f"{label}: duplicate number")
        seen_keys.add(r.get("role_key"))
        seen_numbers.add(r.get("number"))
    return problems


def load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def latest_tracker(folder: Path):
    """The newest career_tracker_YYYY-MM-DD[_vN].json in a folder, or None."""
    best, best_key = None, None
    for p in Path(folder).glob("career_tracker_*.json"):
        m = _TRACKER_NAME.match(p.name)
        if not m:
            continue
        key = (m.group(1), int(m.group(2) or 1))
        if best_key is None or key > best_key:
            best, best_key = p, key
    return best


def parse_date(value):
    """A YYYY-MM-DD string as a date, else None (approximate or 'not listed' stay text)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text(value).strip())
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
