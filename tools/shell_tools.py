import subprocess
import os

def run_command(command: str, cwd: str = ".") -> str:
    try:
        # Run command via PowerShell on Windows
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace"
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()

        result = []
        if out:
            result.append(out)
        if err:
            result.append(f"[STDERR]\n{err}")

        final_out = "\n".join(result) if result else "(Command executed with no output)"
        # Cap length to prevent overwhelming the context window
        if len(final_out) > 8000:
            final_out = final_out[:8000] + "\n...[Output truncated]..."
        return final_out
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 60 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"
