"""
Initialize a Git repository and create one commit for each project file.

Run from the project root:
    python scripts/git_commit_each_file.py

The script intentionally does not configure your Git identity or remote.
"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".venv", ".venv312", "__pycache__", "dist", ".pytest_cache"}
SKIP_FILES = {"finance.db", ".DS_Store", ".env", "model.joblib"}

def run(*args):
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)

def git_available():
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def project_files():
    paths = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        paths.append(rel)
    return sorted(paths)

def main():
    if not git_available():
        print("Git is not installed or not available on PATH.")
        sys.exit(1)

    if not (ROOT / ".git").exists():
        run("git", "init")

    run("git", "status", "--short")

    for rel in project_files():
        run("git", "add", "--", str(rel))
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT
        )
        if result.returncode == 0:
            continue
        message = f"Add {rel.as_posix()}"
        run("git", "commit", "-m", message)

    print("\nDone. Git history:")
    subprocess.run(["git", "log", "--oneline", "--decorate", "--max-count=20"], cwd=ROOT)

if __name__ == "__main__":
    main()
