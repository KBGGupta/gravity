import json
import threading
from .models import ModelClient
from .prompts import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, execute_tool
from accessibility import speaker

class AgentBrain:
    def __init__(self, config: dict, on_message=None, on_status=None):
        self.config = config
        self.on_message = on_message or (lambda role, text: None)
        self.on_status = on_status or (lambda status_text: None)
        self.client = ModelClient(config)
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.is_running = False

    def update_config(self, config: dict):
        self.config = config
        self.client = ModelClient(config)

    def clear_history(self):
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def stop(self):
        self.is_running = False
        self.on_status("Stopped by user.")
        if self.config.get("voice_feedback", True):
            speaker.speak("Agent stopped.")

    def run_async(self, user_prompt: str, on_complete=None):
        thread = threading.Thread(target=self._run_loop, args=(user_prompt, on_complete), daemon=True)
        thread.start()

    def _run_loop(self, user_prompt: str, on_complete=None):
        self.is_running = True
        workspace = self.config.get("workspace_dir", ".")
        max_steps = self.config.get("max_steps", 10)
        voice_on = self.config.get("voice_feedback", True)

        # 1. Announce and notify
        self.on_message("User", user_prompt)
        self.on_status("Thinking...")
        if voice_on:
            speaker.speak("Thinking...")

        self.messages.append({"role": "user", "content": user_prompt})

        step = 0
        while self.is_running and step < max_steps:
            step += 1
            
            # Call LLM
            response = self.client.call_llm(self.messages, tools=TOOL_DEFINITIONS)

            if not self.is_running:
                break

            if response.get("error"):
                err_msg = response["message"]
                self.on_message("System", f"[Error]: {err_msg}")
                self.on_status("Error occurred.")
                if voice_on:
                    speaker.speak("An error occurred.")
                break

            content = response.get("content") or ""
            tool_calls = response.get("tool_calls")

            # If there is textual reasoning
            if content:
                self.on_message("Agent", content)

            # If the model wants to call tools
            if tool_calls:
                # Add assistant message with tool calls to history
                self.messages.append({
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_calls
                })

                for tc in tool_calls:
                    if not self.is_running:
                        break

                    func = tc.get("function", {})
                    fn_name = func.get("name", "unknown")
                    raw_args = func.get("arguments", "{}")

                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    except Exception:
                        args = {}

                    status_msg = f"Running tool: {fn_name}"
                    self.on_status(status_msg)
                    if voice_on:
                        speaker.speak(f"Running {fn_name}")

                    self.on_message("Tool Call", f"[{fn_name}] Arguments: {json.dumps(args)}")

                    # Execute the tool
                    output = execute_tool(fn_name, args, workspace)
                    self.on_message("Tool Result", output)

                    # Add tool response to history
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", f"call_{step}"),
                        "name": fn_name,
                        "content": output
                    })
            else:
                # No more tools called, model is done
                if not content:
                    self.on_message("Agent", "Done.")
                self.on_status("Ready")
                if voice_on:
                    speaker.speak("Task complete.")
                break

        self.is_running = False
        if on_complete:
            on_complete()
