#!/usr/bin/env python3
"""Build a Career Pathfinder CV or cover letter to PDF, then check it.

One command does the whole job (.claude/skills/career-cv-template/SKILL.md, .claude/skills/career-cover-letter-template/SKILL.md):

  1. Safety scan. Text from postings and research is untrusted, so the .tex may load
     no file except personal.tex (and cover.cls for letters) and may not run code:
     \\input/\\include of anything else, \\write18, \\directlua, \\openout and similar
     are refused before LaTeX starts.
  2. Build in a temporary folder with the .tex, personal.tex, and for letters
     cover.cls and the fonts/ folder, so it works however the files are stored
     (templates/ and fonts come from the repository's templates/ folder).
  3. Engine: lualatex for CVs (moderncv), xelatex for letters (cover.cls), with
     shell escape turned off.
  4. Copy the PDF next to the .tex and delete the temporary folder.
  5. Checks: verify_pdf.py (pages: CV 1 or 2, letter exactly 1; readable text layer;
     for CVs, date ranges joined by a Unicode dash) and keyword coverage, then
     verify_layout.py (orphaned entries, holes, early page ends, thin final page,
     footer collisions).

A check whose tool is missing is reported as SKIPPED with the install command, never
as passed.

Usage:
  python3 scripts/build_document.py workspace/cvs/<file>.tex [--keywords "term 1" "term 2"]
  python3 scripts/build_document.py workspace/letters/<file>.tex
  (Windows: python instead of python3)

Options:
  --kind cv|letter      override detection (moderncv -> cv, cover class -> letter)
  --personal PATH       personal.tex to use (default: searched for next to the .tex,
                        then in the parent folders, e.g. workspace/personal.tex)
  --assets DIR          folder holding cover.cls and fonts/ (default: templates/)
  --layout-tool T       auto (pdfplumber, then Poppler), pdfplumber or poppler
  --no-checks           build only

Exit codes: 0 built and every check passed; 1 built but a check failed; 2 usage error,
refused by the safety scan, or the build failed; 3 the LaTeX engine is not installed.
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATES = ROOT / "templates"
WORKSPACE = ROOT / "workspace"
sys.path.insert(0, str(HERE))

ENGINES = {"cv": "lualatex", "letter": "xelatex"}
PAGES = {"cv": {1, 2}, "letter": {1}}
TIMEOUT_SECONDS = 300

# Commands a CV or letter never needs and that could read or write other files or run
# code. personal.tex is the one allowed \input; cover.cls arrives through \documentclass.
FORBIDDEN = re.compile(
    r"\\(?:include|InputIfFileExists|openin|openout|read|readline|write18|"
    r"immediate\s*\\write|directlua|luaexec|luadirect|ShellEscape|"
    r"import|subimport|includefrom|subincludefrom|catcode|usepackage\s*(?:\[[^\]]*\])?\s*\{\s*shellesc)"
)
INPUT = re.compile(r"\\input\s*\{?\s*([^}\s]+)\s*\}?")


def strip_comments(tex: str) -> str:
    """Remove LaTeX comments (an unescaped % to end of line) before scanning."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in tex.splitlines())


def safety_scan(tex: str) -> list[str]:
    body = strip_comments(tex)
    problems = [f"forbidden command: {m.group(0).strip()}" for m in FORBIDDEN.finditer(body)]
    for m in INPUT.finditer(body):
        target = Path(m.group(1)).name
        if target not in ("personal", "personal.tex"):
            problems.append(f"\\input of {m.group(1)!r} (only personal.tex may be loaded)")
    return problems


def detect_kind(tex: str) -> str | None:
    body = strip_comments(tex)
    if re.search(r"\\documentclass(\[[^\]]*\])?\{moderncv\}", body):
        return "cv"
    if re.search(r"\\documentclass(\[[^\]]*\])?\{cover\}", body):
        return "letter"
    return None


def find_personal(tex_path: Path, explicit: Path | None) -> Path | None:
    if explicit:
        return explicit if explicit.is_file() else None
    for folder in [tex_path.parent, *list(tex_path.parent.parents)[:3], WORKSPACE]:
        candidate = folder / "personal.tex"
        if candidate.is_file():
            return candidate
    return None


def engine_command(engine: str, tex_name: str) -> list[str] | None:
    binary = shutil.which(engine)
    if not binary:
        return None
    try:
        version = subprocess.run([binary, "--version"], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        version = ""
    # MiKTeX spells "no shell escape" -disable-write18; TeX Live spells it -no-shell-escape.
    no_shell = "-disable-write18" if "MiKTeX" in version else "-no-shell-escape"
    return [binary, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
            no_shell, tex_name]


def log_errors(log: str) -> str:
    lines = log.splitlines()
    picked = [l for l in lines if l.startswith("!") or ":error" in l.lower() or re.match(r".*:\d+: ", l)]
    return "\n".join(picked[:15]) if picked else "\n".join(lines[-20:])


def build(tex_path: Path, kind: str, personal: Path, assets: Path) -> tuple[Path | None, str]:
    """Return (pdf path or None, message)."""
    engine = ENGINES[kind]
    with tempfile.TemporaryDirectory(prefix="career-build-") as tmp:
        work = Path(tmp)
        shutil.copy2(tex_path, work / tex_path.name)
        shutil.copy2(personal, work / "personal.tex")
        if kind == "letter":
            cls = assets / "cover.cls"
            if not cls.is_file():
                return None, f"cover.cls not found in {assets}"
            shutil.copy2(cls, work / "cover.cls")
            fonts = assets / "fonts"
            if fonts.is_dir():
                shutil.copytree(fonts, work / "fonts")
        cmd = engine_command(engine, tex_path.name)
        if cmd is None:
            return None, f"ENGINE MISSING: {engine} not found on the command line"
        log = ""
        for _ in range(2):  # a second run only if LaTeX asks for one
            try:
                subprocess.run(cmd, cwd=work, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                return None, f"{engine} timed out after {TIMEOUT_SECONDS}s"
            log_file = work / (tex_path.stem + ".log")
            log = log_file.read_text(encoding="utf-8", errors="replace") if log_file.exists() else ""
            if "Rerun to get" not in log:
                break
        pdf = work / (tex_path.stem + ".pdf")
        if not pdf.exists():
            return None, f"{engine} produced no PDF:\n{log_errors(log)}"
        out = tex_path.with_suffix(".pdf")
        shutil.copy2(pdf, out)
    return out, f"built with {engine}"


def run_checks(pdf: Path, kind: str, keywords: list[str], layout_tool: str) -> list[tuple[str, str, str]]:
    """Return (check, status, detail) rows; status is PASS, FAIL or SKIPPED."""
    rows = []
    try:
        import verify_pdf as vp
    except ImportError as exc:
        return [("text layer", "SKIPPED", f"verify_pdf.py not found next to this script ({exc})")]

    try:
        text, pages, extractor = vp.extract_text_layer(pdf)
    except vp.VerificationError as exc:
        rows.append(("text layer", "SKIPPED", f"{exc}. Install: python3 scripts/setup_tools.py --install"))
        text, pages, extractor = None, None, None

    if text is not None:
        allowed = PAGES[kind]
        wanted = " or ".join(str(n) for n in sorted(allowed))
        rows.append(("pages", "PASS" if pages in allowed else "FAIL",
                     f"{pages} page(s); allowed {wanted}"))
        chars = len(vp.normalize_text(text))
        rows.append(("text layer", "PASS" if chars >= 200 else "FAIL",
                     f"{chars} readable characters via {extractor}"))
        garbled = text.count("\ufffd") + len(re.findall(r"\(cid:\d+\)", text))
        rows.append(("garbled text", "PASS" if garbled == 0 else "FAIL",
                     f"{garbled} replacement or (cid:) markers"))
        if kind == "cv":
            hits = vp.find_non_ascii_date_ranges(text)
            rows.append(("date ranges", "PASS" if not hits else "FAIL",
                         "; ".join(f"U+{ord(d):04X} in {l[:60]!r}" for l, d in hits) or "plain hyphens"))
        if keywords:
            normalized = vp.normalize_text(text).lower()
            missing = [k for k in keywords if vp.normalize_text(k).lower() not in normalized]
            rows.append(("keywords", "PASS" if not missing else "FAIL",
                         f"{len(keywords) - len(missing)}/{len(keywords)} found"
                         + (f"; missing: {', '.join(missing)}" if missing else "")))

    try:
        import verify_layout as vl
        try:
            layout_pages, used = vl.parse_pdf(pdf, layout_tool)
            problems = vl.report(pdf, layout_pages, used)
            rows.append(("layout", "PASS" if not problems else "FAIL",
                         "clean" if not problems else " | ".join(problems)))
        except RuntimeError as exc:
            rows.append(("layout", "SKIPPED",
                         f"{exc}. Install: python3 scripts/setup_tools.py --install "
                         "(or --poppler-help for Poppler)"))
    except ImportError as exc:
        rows.append(("layout", "SKIPPED", f"verify_layout.py not found next to this script ({exc})"))
    return rows


def _force_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


def main(argv=None) -> int:
    _force_utf8_output()
    ap = argparse.ArgumentParser(description="Build a CV or cover letter to PDF, then check it.")
    ap.add_argument("tex", type=Path)
    ap.add_argument("--kind", choices=["cv", "letter"])
    ap.add_argument("--keywords", nargs="*", default=[])
    ap.add_argument("--personal", type=Path)
    ap.add_argument("--assets", type=Path, default=TEMPLATES)
    ap.add_argument("--layout-tool", choices=["auto", "pdfplumber", "poppler"], default="auto")
    ap.add_argument("--no-checks", action="store_true")
    args = ap.parse_args(argv)

    tex_path = args.tex.resolve()
    if not tex_path.is_file() or tex_path.suffix != ".tex":
        print(f"error: {args.tex} is not a .tex file", file=sys.stderr)
        return 2
    source = tex_path.read_text(encoding="utf-8", errors="replace")

    problems = safety_scan(source)
    if problems:
        print("REFUSED by the safety scan:")
        for p in problems:
            print(f"  - {p}")
        return 2

    kind = args.kind or detect_kind(source)
    if kind is None:
        print("error: cannot tell CV from letter; use --kind cv or --kind letter", file=sys.stderr)
        return 2

    personal = find_personal(tex_path, args.personal)
    if personal is None:
        print("error: personal.tex not found (it is created at intake; see .claude/skills/career-intake-profiles/SKILL.md)",
              file=sys.stderr)
        return 2

    pdf, message = build(tex_path, kind, personal, args.assets.resolve())
    if pdf is None:
        print(f"BUILD FAILED: {message}")
        if message.startswith("ENGINE MISSING"):
            print("  Install MacTeX on Mac (tug.org/mactex) or MiKTeX on Windows (miktex.org), make its "
                  "programs available on the command line, then check with: python3 scripts/setup_tools.py")
            return 3
        return 2
    print(f"BUILD OK: {pdf} ({message}, personal details from {personal})")

    if args.no_checks:
        return 0
    rows = run_checks(pdf, kind, args.keywords, args.layout_tool)
    width = max(len(r[0]) for r in rows)
    for check, status, detail in rows:
        print(f"  {check:<{width}}  {status:<7}  {detail}")
    if any(status == "SKIPPED" for _, status, _ in rows):
        print("Some checks were SKIPPED (not passed). Install the tools above and run again.")
    return 1 if any(status == "FAIL" for _, status, _ in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
