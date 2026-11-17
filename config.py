import os
import json

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".accessible_code_agent")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "provider": "ollama",  # 'ollama', 'groq', 'openrouter', 'gemini', 'openai_compatible', 'demo'
    "model_name": "qwen2.5-coder",
    "api_key": "",
    "base_url": "http://localhost:11434/v1",
    "workspace_dir": os.path.abspath("."),
    "voice_feedback": True,
    "max_steps": 10
}

def load_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

def reset_to_default_config(workspace_dir=None):
    cfg = DEFAULT_CONFIG.copy()
    if workspace_dir:
        cfg["workspace_dir"] = workspace_dir
    save_config(cfg)
    return cfg
