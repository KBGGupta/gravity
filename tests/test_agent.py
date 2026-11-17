import os
import sys
import unittest

from config import DEFAULT_CONFIG
from tools.file_tools import list_directory, write_file, read_file, edit_file
from tools.db_tools import sqlite_query, sqlite_list_tables, sqlite_describe_table
from tools.shell_tools import run_command
from tools.web_tools import search_web
from agent.brain import AgentBrain

class TestAgentComponents(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath("./test_workspace")
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_file_tools(self):
        # 1. Write file
        msg = write_file(self.test_dir, "sample.txt", "Line 1: Hello\nLine 2: World\n")
        self.assertIn("Successfully wrote", msg)

        # 2. Read file
        content = read_file(self.test_dir, "sample.txt")
        self.assertIn("Line 1: Hello", content)

        # 3. Edit file
        edit_msg = edit_file(self.test_dir, "sample.txt", "World", "Antigravity")
        self.assertIn("Successfully updated", edit_msg)

        # 4. Verify edit
        updated_content = read_file(self.test_dir, "sample.txt")
        self.assertIn("Antigravity", updated_content)

    def test_database_tools(self):
        db_name = "test_db.sqlite"
        # Create table
        create_res = sqlite_query(self.test_dir, db_name, "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, role TEXT);")
        self.assertIn("successfully", create_res.lower())

        # Insert record
        insert_res = sqlite_query(self.test_dir, db_name, "INSERT INTO users (name, role) VALUES ('Karan', 'Developer');")
        self.assertIn("Rows affected", insert_res)

        # Query record
        query_res = sqlite_query(self.test_dir, db_name, "SELECT * FROM users;")
        self.assertIn("Karan", query_res)
        self.assertIn("Developer", query_res)

        # List tables
        tbl_res = sqlite_list_tables(self.test_dir, db_name)
        self.assertIn("users", tbl_res)

    def test_shell_tool(self):
        cmd_res = run_command("Write-Output 'Testing Shell'", self.test_dir)
        self.assertIn("Testing Shell", cmd_res)

    def test_web_search_tool(self):
        web_res = search_web("python sqlite3 tutorial", max_results=2)
        self.assertTrue(len(web_res) > 20)

    def test_agent_demo_loop(self):
        cfg = DEFAULT_CONFIG.copy()
        cfg["provider"] = "demo"
        cfg["workspace_dir"] = self.test_dir

        logs = []
        def log_msg(role, text):
            logs.append((role, text))

        brain = AgentBrain(cfg, on_message=log_msg)
        brain._run_loop("Please list files in the folder")

        # Verify that the tool was called and answered
        roles = [r[0] for r in logs]
        self.assertIn("Tool Call", roles)
        self.assertIn("Tool Result", roles)

if __name__ == "__main__":
    unittest.main()
