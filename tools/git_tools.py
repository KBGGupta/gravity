import subprocess
import os
import shutil

def find_git_binary():
    git_bin = shutil.which("git")
    if git_bin:
        return git_bin
    for candidate in [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\cmd\git.exe")
    ]:
        if os.path.exists(candidate):
            return candidate
    return "git"

def run_git(args: list, cwd: str) -> str:
    try:
        git_cmd = find_git_binary()
        res = subprocess.run(
            [git_cmd] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
            errors="replace"
        )
        out = (res.stdout or "").strip()
        err = (res.stderr or "").strip()
        if res.returncode != 0:
            return f"Git Error (code {res.returncode}):\n{err or out}"
        return out if out else "(No output / clean)"
    except FileNotFoundError:
        return "Error: 'git' is not installed or not in system PATH."
    except Exception as e:
        return f"Error executing git: {str(e)}"

def git_status(base_dir: str) -> str:
    return run_git(["status", "--short", "--branch"], base_dir)

def git_diff(base_dir: str, staged: bool = False) -> str:
    args = ["diff"]
    if staged:
        args.append("--staged")
    return run_git(args, base_dir)

def git_log(base_dir: str, count: int = 5) -> str:
    return run_git(["log", f"-n{count}", "--oneline", "--decorate"], base_dir)

def git_commit(base_dir: str, message: str) -> str:
    # First stage all tracked changes
    add_res = run_git(["add", "-A"], base_dir)
    if "Git Error" in add_res:
        return add_res
    return run_git(["commit", "-m", message], base_dir)

def git_clone(repo_url: str, target_dir: str) -> str:
    try:
        parent_dir = os.path.dirname(os.path.abspath(target_dir))
        res = subprocess.run(
            ["git", "clone", repo_url, target_dir],
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0:
            return f"Successfully cloned '{repo_url}' into '{target_dir}'."
        return f"Git Clone Error:\n{res.stderr or res.stdout}"
    except Exception as e:
        return f"Error running git clone: {str(e)}"
