#!/usr/bin/env python3
"""Check and set up the tools Career Pathfinder uses.

  python3 scripts/setup_tools.py                    report what is installed (changes nothing)
  python3 scripts/setup_tools.py --install          install the Python add-ons (pdfplumber, pypdf, openpyxl)
  python3 scripts/setup_tools.py --create-personal  create workspace/personal.tex from the template,
                                                    only if it does not exist yet (never overwrites)
  python3 scripts/setup_tools.py --poppler-help     show how to install Poppler on Mac or Windows

On Windows use `python` instead of `python3`: a python.org install ships no `python3`,
so that name reaches the Microsoft Store alias, which either exits with no output or
starts a separate Store Python without the packages pip installed.

Tools, most preferred first (.claude/skills/career-cv-cover-letter/SKILL.md, "Tools"):
  building the PDF       MacTeX (Mac) or MiKTeX (Windows): lualatex (CVs), xelatex (letters)
  reading PDF text       pdfplumber, then pypdf, then Poppler pdftotext
  measuring the layout   pdfplumber, then Poppler
  Excel export           openpyxl (only when the user asks for an Excel copy)

Poppler is optional; it is never installed automatically.

--create-personal copies templates/personal.tex (placeholders only) into workspace/. The
project settings stop the agent from creating or opening workspace/personal.tex itself;
this script is how the file is made. It never prints the file's contents.
"""

import argparse
import importlib.util
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Python add-on -> what it is for. Keep in step with requirements.txt.
PY_PACKAGES = {
    "pdfplumber": "PDF text and layout checks",
    "pypdf": "PDF text check (second choice)",
    "openpyxl": "Excel export, only when you ask for it",
}
ENGINES = {"lualatex": "CVs", "xelatex": "cover letters"}


def python_cmd() -> str:
    return "python" if platform.system() == "Windows" else "python3"


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def engine_info(name: str) -> str:
    binary = shutil.which(name)
    if not binary:
        return "not found on the command line"
    try:
        first = subprocess.run([binary, "--version"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60).stdout.splitlines()
        return f"found ({first[0] if first else binary})"
    except (OSError, subprocess.SubprocessError):
        return f"found ({binary})"


def poppler_info() -> str:
    binary = shutil.which("pdftotext")
    if not binary:
        return "not installed (optional)"
    try:
        res = subprocess.run([binary, "-h"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=30)
        has_bbox = "-bbox" in (res.stdout or "") + (res.stderr or "")
    except (OSError, subprocess.SubprocessError):
        has_bbox = False
    return f"found ({binary}){'' if has_bbox else ' - this build lacks -bbox; layout checks will use pdfplumber'}"


def report() -> int:
    py = python_cmd()
    print(f"Python {platform.python_version()} ({sys.executable})")
    if sys.version_info < (3, 10):
        print("  ! Python 3.10 or newer is needed")
    print("\nPython add-ons:")
    missing = []
    for pkg, use in PY_PACKAGES.items():
        ok = has_module(pkg)
        print(f"  {pkg:<11} {'installed' if ok else 'missing':<10} [{use}]")
        if not ok:
            missing.append(pkg)
    print("\nLaTeX (MacTeX on Mac, MiKTeX on Windows):")
    for name, use in ENGINES.items():
        print(f"  {name:<11} {engine_info(name)}  [{use}]")
    print("\nPoppler:")
    print(f"  pdftotext   {poppler_info()}")

    print("\nNext steps:")
    if missing:
        print(f"  - Missing Python add-ons: {', '.join(missing)}. Install them with:")
        print(f"      {py} scripts/setup_tools.py --install")
        print(f"    (or: {py} -m pip install -r requirements.txt), then run this check again.")
    if any(not shutil.which(e) for e in ENGINES):
        if platform.system() == "Darwin":
            print("  - Install MacTeX from https://www.tug.org/mactex/ (the standard installer).")
            print("    Then fully quit and reopen VS Code (or open a new terminal) and run this check again.")
        else:
            print("  - Install MiKTeX from https://miktex.org/download, then in MiKTeX Console:")
            print("      * set 'Always install missing packages on-the-fly'")
            print("      * make MiKTeX's programs available on the command line")
            print("    Open a new terminal afterwards and run this check again.")
    if not shutil.which("pdftotext"):
        print(f"  - Optional: Poppler (see {py} scripts/setup_tools.py --poppler-help)")
    if not missing and all(shutil.which(e) for e in ENGINES):
        print("  - Nothing required is missing.")
    return 0


def install() -> int:
    missing = [pkg for pkg in PY_PACKAGES if not has_module(pkg)]
    if not missing:
        print("All Python add-ons are already installed:", ", ".join(PY_PACKAGES))
        return 0
    cmd = [sys.executable, "-m", "pip", "install", *missing]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("pip failed. Try again, or install them yourself with the command above.")
        return 1
    print("Installed. Run the check again to confirm:", python_cmd(), "scripts/setup_tools.py")
    return 0


def create_personal() -> int:
    """Copy templates/personal.tex to workspace/personal.tex if it does not exist yet."""
    source = ROOT / "templates" / "personal.tex"
    target = ROOT / "workspace" / "personal.tex"
    if target.exists():
        print("workspace/personal.tex already exists, so it was left unchanged (it is never overwritten).")
        return 0
    if not source.is_file():
        print("error: templates/personal.tex not found; download the project again.", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("x", encoding="utf-8") as fh:  # "x": never overwrite, even in a race
            fh.write(source.read_text(encoding="utf-8"))
    except FileExistsError:
        print("workspace/personal.tex already exists, so it was left unchanged (it is never overwritten).")
        return 0
    print("Created workspace/personal.tex (placeholders only).")
    print("Open it in any text editor and replace each placeholder, either with a placeholder of the")
    print("same length as your real detail (e.g. Xxxxxx for Ramesh) or with your real details.")
    print("See README.md, 'What stays private', for the difference.")
    return 0


def poppler_help() -> int:
    print("""Poppler (optional) - only needed if you want it instead of pdfplumber.
Each route needs a package manager installed first.

Mac
  Homebrew (https://brew.sh): after installing Homebrew, run
      brew install poppler
  MacPorts (https://www.macports.org): after installing MacPorts, run
      sudo port install poppler

Windows
  Scoop (https://scoop.sh): after installing Scoop, run
      scoop install poppler
  Chocolatey (https://chocolatey.org): after installing Chocolatey, in an
  administrator terminal run
      choco install poppler

Then open a new terminal and check:  pdftotext -v
If Poppler fails on a document, the checks fall back to pdfplumber automatically.""")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check and set up the Career Pathfinder tools.")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--install", action="store_true", help="install the missing Python add-ons")
    group.add_argument("--create-personal", action="store_true",
                       help="create workspace/personal.tex from the template if it does not exist")
    group.add_argument("--poppler-help", action="store_true", help="show Poppler install commands")
    args = ap.parse_args(argv)
    if args.install:
        return install()
    if args.create_personal:
        return create_personal()
    if args.poppler_help:
        return poppler_help()
    return report()


if __name__ == "__main__":
    sys.exit(main())
