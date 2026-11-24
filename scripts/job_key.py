#!/usr/bin/env python3
# Adapted for Career Pathfinder from the job-application-assistant workflow.
# Licensed under the MIT License; see README.md (Credits and licence).
"""Role key for a job posting, and a lookup against the seen-role lists.

.claude/skills/career-job-search/SKILL.md keys every row of seen_roles_profile_N.csv (and every
file in job_descriptions/) by company + title. Making the key a pure,
deterministic function of the posting fixes two failures that free-hand keys
cause:

  * Keys carrying characters that break things downstream: a "/" in a title
    splits a file path, a "," breaks a CSV row.
  * The same job stored twice under different keys, because one run shortened
    the title at a different point than the next.

Long names are length-capped *and* disambiguated by a hash of the full slug, so
a long title always produces the same key and two different long titles never
collide. A title that slugifies to nothing, or loses letters in the ASCII fold
(a posting written in a non-Latin script), falls back to the job number in the
URL, or a hash of the URL, for its identity.

Usage:
  python3 scripts/job_key.py --company "Acme Corp" --title "SOC Analyst (L2)" [--url URL]
  python3 scripts/job_key.py --company ... --title ... --url ... --seen workspace/seen_roles_profile_*.csv

With --seen, also prints `SEEN status=<status> file=<csv>` when the key or the
URL is already in one of the given seen-role lists, otherwise `NEW`, so the
lists never have to be loaded into the conversation.

Exit 0 when a key is produced; 2 on a usage error or an unreadable list.
"""

import argparse
import csv
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

COMPANY_MAX = 40
TITLE_MAX = 60
HASH_LEN = 6

# Anything outside this set becomes a separator. Deliberately strict: an
# allowlist cannot be surprised by the next punctuation mark a job board invents.
_NON_SLUG = re.compile(r"[^a-z0-9]+")
_JOB_ID = re.compile(r"(\d{6,})")

# Latin letters with no NFKD decomposition, which the ASCII fold would otherwise
# drop ("Ørsted" keyed as "rsted", "Mærsk" as "mrsk"). "å" is deliberately
# absent: it decomposes to "a" plus a ring without losing a letter.
_LATIN_FOLD = {
    "ø": "o", "Ø": "O",      # ø Ø
    "æ": "ae", "Æ": "AE",    # æ Æ
    "œ": "oe", "Œ": "OE",    # œ Œ
    "ß": "ss", "ẞ": "SS",    # ß ẞ
    "þ": "th", "Þ": "TH",    # þ Þ
    "ð": "d", "Ð": "D",      # ð Ð
    "đ": "d", "Đ": "D",      # đ Đ
    "ł": "l", "Ł": "L",      # ł Ł
    "ı": "i",                     # ı
    "ħ": "h", "Ħ": "H",      # ħ Ħ
    "ĸ": "k",                     # ĸ
    "ŋ": "ng", "Ŋ": "NG",    # ŋ Ŋ
    "ŧ": "t", "Ŧ": "T",      # ŧ Ŧ
}
_LATIN_FOLD_TABLE = str.maketrans(_LATIN_FOLD)


def slugify(text: str) -> str:
    """Lowercase ASCII slug. Non-Latin scripts legitimately reduce to ''."""
    if not text:
        return ""
    # Fold after NFKD so a letter that decomposes into a fold-table letter plus
    # a mark is folded too.
    decomposed = unicodedata.normalize("NFKD", str(text))
    folded = decomposed.translate(_LATIN_FOLD_TABLE)
    ascii_only = folded.encode("ascii", "ignore").decode("ascii")
    return _NON_SLUG.sub("-", ascii_only.lower()).strip("-")


def _lost_letters(text: str) -> bool:
    """True when the ASCII fold dropped non-Latin letters, so the slug under-identifies."""
    if not text:
        return False
    for ch in unicodedata.normalize("NFKD", str(text)):
        if ord(ch) < 128 or not ch.isalpha():
            continue
        if not unicodedata.name(ch, "LATIN").startswith("LATIN"):
            return True
    return False


def _cap(slug: str, limit: int) -> str:
    """Cap length without making truncation differ between runs."""
    if len(slug) <= limit:
        return slug
    digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:HASH_LEN]
    return f"{slug[:limit].rstrip('-')}-{digest}"


def make_key(company: str, title: str, url: str = "") -> str:
    """The canonical role key for one posting: <company-slug>_<title-slug>."""
    company_slug = _cap(slugify(company), COMPANY_MAX)
    if not company_slug or _lost_letters(company):
        name = unicodedata.normalize("NFC", str(company or "").strip().casefold())
        # An absent name stays unknown; a non-Latin name still has an identity.
        digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:HASH_LEN]
        if not name:
            company_slug = "unknown-company"
        else:
            company_slug = f"{company_slug}-{digest}" if company_slug else f"company-{digest}"
    title_slug = _cap(slugify(title), TITLE_MAX)
    if not title_slug or _lost_letters(title):
        # The job number in the URL is the stable handle; a surviving fragment
        # stays as a readable prefix only.
        fragment = title_slug
        match = _JOB_ID.search(url or "")
        if match:
            title_slug = f"{fragment}-{match.group(1)}" if fragment else match.group(1)
        else:
            basis = slugify(unicodedata.normalize("NFKD", str(title or url or "")))
            # Hash the URL alone when there is one: the URL is the posting's
            # identity; a re-listed title is not.
            digest_basis = str(url) if url else str(title)
            digest = hashlib.sha1(digest_basis.encode("utf-8")).hexdigest()[:HASH_LEN]
            title_slug = f"{fragment}-{digest}" if fragment else (basis or f"untitled-{digest}")
    return f"{company_slug}_{title_slug}"


def lookup(key: str, url: str, paths: list) -> str:
    """`SEEN status=... file=...` if key or URL is in a seen-role list, else `NEW`."""
    want_url = (url or "").strip().rstrip("/")
    for path in paths:
        if not path.exists():
            continue
        with path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                row_url = (row.get("url") or "").strip().rstrip("/")
                if row.get("key") == key or (want_url and row_url == want_url):
                    return f"SEEN status={row.get('status') or 'unknown'} file={path.name}"
    return "NEW"


def _force_utf8_output() -> None:
    """Write UTF-8 whatever the host's default encoding is."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)  # absent on a StringIO under test
        if reconfigure:
            reconfigure(encoding="utf-8")


def main() -> int:
    _force_utf8_output()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--company", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--url", default="")
    ap.add_argument("--seen", nargs="*", type=Path, default=None, metavar="CSV",
                    help="seen-role lists to check the key and URL against")
    args = ap.parse_args()

    key = make_key(args.company, args.title, args.url)
    print(key)
    if args.seen is not None:
        try:
            print(lookup(key, args.url, args.seen))
        except (OSError, csv.Error) as exc:
            print(f"job_key: cannot read seen list: {exc}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
