from .file_tools import list_directory, read_file, write_file, edit_file, search_codebase
from .git_tools import git_status, git_diff, git_log, git_commit, git_clone
from .db_tools import sqlite_list_tables, sqlite_describe_table, sqlite_query
from .shell_tools import run_command
from .web_tools import search_web

# Master Tool Definition Catalog for the Agent
TOOL_DEFINITIONS = [
    {
        "name": "list_directory",
        "description": "List files and subfolders in the current workspace or a subfolder.",
        "parameters": {
            "type": "object",
            "properties": {
                "rel_path": {"type": "string", "description": "Relative path to list (default: '.')."}
            }
        }
    },
    {
        "name": "read_file",
        "description": "Read file contents with line numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the file to read."},
                "start_line": {"type": "integer", "description": "Start line (1-indexed)."},
                "end_line": {"type": "integer", "description": "End line (optional)."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Create a new file or completely overwrite an existing file with new content.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the file to write."},
                "content": {"type": "string", "description": "Full file content."}
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "Replace exact target string with replacement string in an existing file.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the file to edit."},
                "target": {"type": "string", "description": "Exact text to replace."},
                "replacement": {"type": "string", "description": "New replacement text."}
            },
            "required": ["file_path", "target", "replacement"]
        }
    },
    {
        "name": "search_codebase",
        "description": "Search for a keyword or symbol across all files in the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to search for."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "git_status",
        "description": "Check current git status (modified, untracked, branch).",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "git_diff",
        "description": "Show git diff of unstaged or staged changes.",
        "parameters": {
            "type": "object",
            "properties": {
                "staged": {"type": "boolean", "description": "Show staged diff if true."}
            }
        }
    },
    {
        "name": "git_log",
        "description": "Show recent git commit history.",
        "parameters": {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of commits to show (default: 5)."}
            }
        }
    },
    {
        "name": "git_commit",
        "description": "Stage all changes and create a git commit with a message.",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message."}
            },
            "required": ["message"]
        }
    },
    {
        "name": "git_clone",
        "description": "Clone a Git repository URL into a target folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_url": {"type": "string", "description": "Git repository URL."},
                "target_dir": {"type": "string", "description": "Target directory to clone into."}
            },
            "required": ["repo_url", "target_dir"]
        }
    },
    {
        "name": "sqlite_list_tables",
        "description": "List all tables in an SQLite database file.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "description": "Path to .db or .sqlite file."}
            },
            "required": ["db_path"]
        }
    },
    {
        "name": "sqlite_describe_table",
        "description": "Show table columns, data types, and primary keys for an SQLite table.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "description": "Path to .db file."},
                "table_name": {"type": "string", "description": "Table name."}
            },
            "required": ["db_path", "table_name"]
        }
    },
    {
        "name": "sqlite_query",
        "description": "Run an SQL query (SELECT, INSERT, UPDATE, CREATE TABLE) on an SQLite database.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {"type": "string", "description": "Path to .db file."},
                "query": {"type": "string", "description": "SQL query to execute."}
            },
            "required": ["db_path", "query"]
        }
    },
    {
        "name": "run_command",
        "description": "Execute a terminal / PowerShell command in the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "PowerShell command to run."}
            },
            "required": ["command"]
        }
    },
    {
        "name": "search_web",
        "description": "Search StackOverflow and technical documentation for error traces, libraries, and coding solutions.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Technical query, error message, or library name."}
            },
            "required": ["query"]
        }
    }
]

def execute_tool(tool_name: str, args: dict, workspace_dir: str) -> str:
    try:
        if tool_name == "list_directory":
            return list_directory(workspace_dir, args.get("rel_path", "."))
        elif tool_name == "read_file":
            return read_file(workspace_dir, args["file_path"], args.get("start_line", 1), args.get("end_line"))
        elif tool_name == "write_file":
            return write_file(workspace_dir, args["file_path"], args["content"])
        elif tool_name == "edit_file":
            return edit_file(workspace_dir, args["file_path"], args["target"], args["replacement"])
        elif tool_name == "search_codebase":
            return search_codebase(workspace_dir, args["query"])
        elif tool_name == "git_status":
            return git_status(workspace_dir)
        elif tool_name == "git_diff":
            return git_diff(workspace_dir, args.get("staged", False))
        elif tool_name == "git_log":
            return git_log(workspace_dir, args.get("count", 5))
        elif tool_name == "git_commit":
            return git_commit(workspace_dir, args["message"])
        elif tool_name == "git_clone":
            return git_clone(args["repo_url"], args["target_dir"])
        elif tool_name == "sqlite_list_tables":
            return sqlite_list_tables(workspace_dir, args["db_path"])
        elif tool_name == "sqlite_describe_table":
            return sqlite_describe_table(workspace_dir, args["db_path"], args["table_name"])
        elif tool_name == "sqlite_query":
            return sqlite_query(workspace_dir, args["db_path"], args["query"])
        elif tool_name == "run_command":
            return run_command(args["command"], workspace_dir)
        elif tool_name == "search_web":
            return search_web(args["query"])
        else:
            return f"Error: Tool '{tool_name}' not found."
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
