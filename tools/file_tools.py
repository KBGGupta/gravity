import os

def resolve_path(base_dir: str, rel_path: str) -> str:
    if os.path.isabs(rel_path):
        return rel_path
    return os.path.normpath(os.path.join(base_dir, rel_path))

def list_directory(base_dir: str, rel_path: str = ".") -> str:
    target_path = resolve_path(base_dir, rel_path)
    if not os.path.exists(target_path):
        return f"Error: Directory '{target_path}' does not exist."
    if not os.path.isdir(target_path):
        return f"Error: '{target_path}' is a file, not a directory."

    items = []
    try:
        entries = sorted(os.listdir(target_path))
        for entry in entries:
            # skip .git or node_modules or pycache for clean listing
            if entry in [".git", "__pycache__", "node_modules", ".venv", "venv"]:
                continue
            full = os.path.join(target_path, entry)
            if os.path.isdir(full):
                items.append(f"[DIR]  {entry}/")
            else:
                size_kb = round(os.path.getsize(full) / 1024, 2)
                items.append(f"[FILE] {entry} ({size_kb} KB)")
        return "\n".join(items) if items else "(Empty directory)"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def read_file(base_dir: str, file_path: str, start_line: int = 1, end_line: int = None) -> str:
    target_path = resolve_path(base_dir, file_path)
    if not os.path.exists(target_path):
        return f"Error: File '{target_path}' does not exist."
    if os.path.isdir(target_path):
        return f"Error: '{target_path}' is a directory, not a file."

    try:
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        total = len(lines)
        s = max(1, start_line)
        e = min(total, end_line) if end_line else total

        formatted = []
        for i in range(s - 1, e):
            formatted.append(f"{i + 1:4d} | {lines[i].rstrip()}")
        
        return "\n".join(formatted)
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(base_dir: str, file_path: str, content: str, overwrite: bool = True) -> str:
    target_path = resolve_path(base_dir, file_path)
    if os.path.exists(target_path) and not overwrite:
        return f"Error: File '{target_path}' already exists and overwrite=False."

    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def edit_file(base_dir: str, file_path: str, target: str, replacement: str) -> str:
    full_path = resolve_path(base_dir, file_path)
    if not os.path.exists(full_path):
        return f"Error: File '{full_path}' does not exist."

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        if target not in content:
            return f"Error: Target text not found in '{file_path}'."

        new_content = content.replace(target, replacement, 1)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Successfully updated '{file_path}'."
    except Exception as e:
        return f"Error editing file: {str(e)}"

def search_codebase(base_dir: str, query: str) -> str:
    results = []
    query_lower = query.lower()
    for root, dirs, files in os.walk(base_dir):
        # Ignore standard hidden or heavy directories
        dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"]]
        for f in files:
            path = os.path.join(root, f)
            rel = os.path.relpath(path, base_dir)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    for line_num, line in enumerate(file, 1):
                        if query_lower in line.lower():
                            results.append(f"{rel}:{line_num}: {line.strip()}")
                            if len(results) >= 50:
                                break
            except Exception:
                continue
    return "\n".join(results) if results else f"No matches found for '{query}'."
