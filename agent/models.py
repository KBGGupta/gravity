import requests
import json
import re

class ModelClient:
    def __init__(self, config: dict):
        self.config = config

    def call_llm(self, messages: list, tools: list = None) -> dict:
        provider = self.config.get("provider", "ollama").lower()
        api_key = self.config.get("api_key", "").strip()
        model_name = self.config.get("model_name", "qwen2.5-coder")
        base_url = self.config.get("base_url", "http://localhost:11434/v1")

        if provider == "demo":
            return self._demo_response(messages)

        # Standard OpenAI-compatible format (works for Ollama, Groq, OpenRouter, DeepSeek, Gemini OpenAI endpoint)
        endpoint = base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }

        if provider == "groq":
            endpoint = "https://api.groq.com/openai/v1/chat/completions"
            headers["Authorization"] = f"Bearer {api_key}"
            if not model_name or "qwen" in model_name:
                model_name = "llama-3.3-70b-versatile"
        elif provider == "openrouter":
            endpoint = "https://openrouter.ai/api/v1/chat/completions"
            headers["Authorization"] = f"Bearer {api_key}"
            if not model_name:
                model_name = "meta-llama/llama-3.3-70b-instruct:free"
        elif provider == "gemini":
            # Using Gemini's OpenAI-compatible endpoint directly with API key - NO Google login required!
            endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            headers["Authorization"] = f"Bearer {api_key}"
            if not model_name or "qwen" in model_name:
                model_name = "gemini-1.5-flash"
        elif provider == "ollama":
            # Ollama requires no key, default endpoint is localhost
            if not base_url or base_url == "":
                endpoint = "http://localhost:11434/v1/chat/completions"
            else:
                endpoint = base_url.rstrip("/") + "/chat/completions"
        elif provider in ["copilot", "github_copilot"]:
            # GitHub Copilot & GitHub Models endpoint
            endpoint = (base_url or "https://models.inference.ai.azure.com").rstrip("/") + "/chat/completions"
            headers["Authorization"] = f"Bearer {api_key}"
            if not model_name or "qwen" in model_name:
                model_name = "gpt-4o"
        elif provider == "openai_compatible":
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.2
        }

        # Some local/free providers prefer JSON prompting or tool calling in prompt
        # We also pass tools if supported
        if tools:
            payload["tools"] = [{"type": "function", "function": t} for t in tools]

        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=90)
            if resp.status_code != 200:
                # Return informative error message
                return {
                    "error": True,
                    "message": f"API Error (Status {resp.status_code}): {resp.text}"
                }
            
            data = resp.json()
            choice = data["choices"][0]["message"]
            return {
                "error": False,
                "content": choice.get("content", ""),
                "tool_calls": choice.get("tool_calls", None)
            }
        except requests.exceptions.ConnectionError:
            if provider == "ollama":
                return {
                    "error": True,
                    "message": "Could not connect to Ollama at http://localhost:11434.\nMake sure Ollama is installed and running (`ollama serve`), or switch provider to Groq / OpenRouter / Gemini in Settings (Ctrl+S)."
                }
            return {
                "error": True,
                "message": f"Could not connect to {endpoint}. Please check your internet connection or URL in Settings."
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Request failed: {str(e)}"
            }

    def _demo_response(self, messages: list) -> dict:
        """
        Smart local heuristic fallback mode for testing without any API key or local LLM setup.
        """
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").lower()
                break

        # Check for tool trigger patterns
        if "list" in last_user_msg or "files" in last_user_msg or "folder" in last_user_msg:
            return {
                "error": False,
                "content": "I will inspect the workspace files for you.",
                "tool_calls": [{
                    "id": "call_1",
                    "function": {
                        "name": "list_directory",
                        "arguments": json.dumps({"rel_path": "."})
                    }
                }]
            }
        elif "git" in last_user_msg and ("status" in last_user_msg or "branch" in last_user_msg):
            return {
                "error": False,
                "content": "Let me check the git status.",
                "tool_calls": [{
                    "id": "call_2",
                    "function": {
                        "name": "git_status",
                        "arguments": "{}"
                    }
                }]
            }
        elif "database" in last_user_msg or "sqlite" in last_user_msg or "table" in last_user_msg:
            return {
                "error": False,
                "content": "Let me check the database tables.",
                "tool_calls": [{
                    "id": "call_3",
                    "function": {
                        "name": "sqlite_list_tables",
                        "arguments": json.dumps({"db_path": "test.db"})
                    }
                }]
            }
        else:
            return {
                "error": False,
                "content": f"I am running in Demo Mode! You asked: '{last_user_msg}'.\nTo connect real models (Ollama, Groq, OpenRouter, or Gemini), open Settings (Ctrl+S).",
                "tool_calls": None
            }
