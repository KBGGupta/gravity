// State
let isRunning = false;
let messagePollInterval = null;
let lastMessageCount = 0;

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initShortcuts();
  initInputHandlers();
  loadConfig();
  startMessagePolling();
});

// NAVIGATION TABS
function initNavigation() {
  const tabs = document.querySelectorAll(".nav-item");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const viewName = tab.getAttribute("data-view");
      switchView(viewName);
    });
  });

  document.getElementById("btnHelp").addEventListener("click", openShortcutsModal);
  document.getElementById("btnClearChat").addEventListener("click", clearChat);
  document.getElementById("btnChangeWorkspace").addEventListener("click", pickWorkspace);
}

function switchView(viewName) {
  // Update tabs
  document.querySelectorAll(".nav-item").forEach(t => {
    const isTarget = t.getAttribute("data-view") === viewName;
    t.classList.toggle("active", isTarget);
    t.setAttribute("aria-selected", isTarget ? "true" : "false");
  });

  // Update panels
  const panels = {
    chat: document.getElementById("viewChat"),
    files: document.getElementById("viewFiles"),
    git: document.getElementById("viewGit"),
    db: document.getElementById("viewDb"),
    settings: document.getElementById("viewSettings")
  };

  const titles = {
    chat: "Agent Chat Canvas",
    files: "Workspace Files",
    git: "Git Repository",
    db: "Database (SQLite)",
    settings: "Settings & AI Models"
  };

  Object.keys(panels).forEach(k => {
    if (panels[k]) {
      if (k === viewName) {
        panels[k].removeAttribute("hidden");
        panels[k].classList.add("active");
      } else {
        panels[k].setAttribute("hidden", "true");
        panels[k].classList.remove("active");
      }
    }
  });

  document.getElementById("viewHeaderTitle").textContent = titles[viewName] || "Agent Canvas";

  // Trigger data load on view change
  if (viewName === "files") loadFiles();
  if (viewName === "git") fetchGitStatus();
  if (viewName === "db") fetchDbTables();
}

// KEYBOARD SHORTCUTS (Full NVDA Accessibility)
function initShortcuts() {
  window.addEventListener("keydown", (e) => {
    // F1: Help
    if (e.key === "F1") {
      e.preventDefault();
      openShortcutsModal();
    }
    // F6: Toggle between Prompt Input and Chat Scroll
    else if (e.key === "F6") {
      e.preventDefault();
      toggleFocus();
    }
    // Alt + 1..5: Views
    else if (e.altKey && e.key === "1") {
      e.preventDefault();
      switchView("chat");
    } else if (e.altKey && e.key === "2") {
      e.preventDefault();
      switchView("files");
    } else if (e.altKey && e.key === "3") {
      e.preventDefault();
      switchView("git");
    } else if (e.altKey && e.key === "4") {
      e.preventDefault();
      switchView("db");
    } else if (e.altKey && e.key === "5") {
      e.preventDefault();
      switchView("settings");
    }
    // Ctrl + O: Change Workspace
    else if (e.ctrlKey && e.key.toLowerCase() === "o") {
      e.preventDefault();
      pickWorkspace();
    }
    // Ctrl + L: Clear Chat
    else if (e.ctrlKey && e.key.toLowerCase() === "l") {
      e.preventDefault();
      clearChat();
    }
    // Escape: Stop Agent
    else if (e.key === "Escape" && isRunning) {
      e.preventDefault();
      stopAgent();
    }
  });
}

function toggleFocus() {
  const prompt = document.getElementById("promptInput");
  const chat = document.getElementById("chatScroll");
  if (document.activeElement === prompt) {
    chat.focus();
  } else {
    prompt.focus();
  }
}

// INPUT HANDLERS
function initInputHandlers() {
  const promptInput = document.getElementById("promptInput");
  const btnSend = document.getElementById("btnSend");
  const btnStop = document.getElementById("btnStop");

  btnSend.addEventListener("click", () => sendPrompt());
  btnStop.addEventListener("click", () => stopAgent());

  promptInput.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") {
      e.preventDefault();
      sendPrompt();
    }
  });
}

function setInputPrompt(text) {
  const promptInput = document.getElementById("promptInput");
  promptInput.value = text;
  promptInput.focus();
}

function triggerQuickAction(action) {
  if (action === "git_status") {
    setInputPrompt("Check git status of this repository and tell me modified files.");
  } else if (action === "list_files") {
    setInputPrompt("List all files in the current workspace directory.");
  } else if (action === "list_db") {
    setInputPrompt("Check the tables in the database test.db and describe their schema.");
  } else if (action === "clear") {
    clearChat();
  }
}

// CONFIG & API
async function loadConfig() {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    document.getElementById("wsPathDisplay").textContent = data.workspace_dir || "Not set";
    document.getElementById("modelBadge").textContent = `${data.provider}: ${data.model_name}`;
    
    // Fill settings inputs
    document.getElementById("selProvider").value = data.provider || "ollama";
    document.getElementById("txtModelName").value = data.model_name || "qwen2.5-coder";
    document.getElementById("txtApiKey").value = data.api_key || "";
    document.getElementById("txtBaseUrl").value = data.base_url || "http://localhost:11434/v1";
    document.getElementById("chkVoiceFeedback").checked = data.voice_feedback !== false;
  } catch (err) {
    console.error("Failed to load config:", err);
  }
}

async function saveSettings() {
  const payload = {
    provider: document.getElementById("selProvider").value,
    model_name: document.getElementById("txtModelName").value.trim(),
    api_key: document.getElementById("txtApiKey").value.trim(),
    base_url: document.getElementById("txtBaseUrl").value.trim(),
    voice_feedback: document.getElementById("chkVoiceFeedback").checked
  };

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      alert("Settings saved successfully!");
      loadConfig();
      switchView("chat");
    }
  } catch (err) {
    alert("Error saving settings: " + err.message);
  }
}

async function resetSettingsToDefault() {
  if (!confirm("Are you sure you want to reset all settings back to default (Ollama)?")) {
    return;
  }
  try {
    const res = await fetch("/api/config/reset", { method: "POST" });
    if (res.ok) {
      alert("Settings reset to default (Ollama) successfully!");
      await loadConfig();
      switchView("chat");
    }
  } catch (err) {
    alert("Error resetting settings: " + err.message);
  }
}

function onProviderSelectChange() {
  const prov = document.getElementById("selProvider").value;
  const mName = document.getElementById("txtModelName");
  const bUrl = document.getElementById("txtBaseUrl");

  if (prov === "ollama") {
    mName.value = "qwen2.5-coder";
    bUrl.value = "http://localhost:11434/v1";
  } else if (prov === "copilot") {
    mName.value = "gpt-4o";
    bUrl.value = "https://models.inference.ai.azure.com";
  } else if (prov === "gemini") {
    mName.value = "gemini-1.5-flash";
    bUrl.value = "https://generativelanguage.googleapis.com/v1beta/openai";
  } else if (prov === "groq") {
    mName.value = "llama-3.3-70b-versatile";
    bUrl.value = "https://api.groq.com/openai/v1";
  } else if (prov === "openrouter") {
    mName.value = "meta-llama/llama-3.3-70b-instruct:free";
    bUrl.value = "https://openrouter.ai/api/v1";
  }
}

async function pickWorkspace() {
  try {
    const res = await fetch("/api/workspace/pick", { method: "POST" });
    const data = await res.json();
    if (data.path) {
      document.getElementById("wsPathDisplay").textContent = data.path;
      appendMessage("system", `Workspace folder changed to: ${data.path}`);
    }
  } catch (err) {
    console.error("Workspace picker error:", err);
  }
}

// PROMPT & CHAT EXECUTION
async function sendPrompt() {
  const input = document.getElementById("promptInput");
  const text = input.value.trim();
  if (!text || isRunning) return;

  input.value = "";
  setRunningState(true);

  try {
    await fetch("/api/prompt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text })
    });
  } catch (err) {
    appendMessage("system", "Error sending prompt: " + err.message);
    setRunningState(false);
  }
}

async function stopAgent() {
  try {
    await fetch("/api/stop", { method: "POST" });
    setRunningState(false);
  } catch (err) {
    console.error("Error stopping agent:", err);
  }
}

async function clearChat() {
  try {
    await fetch("/api/clear", { method: "POST" });
    const chatScroll = document.getElementById("chatScroll");
    chatScroll.innerHTML = "";
    lastMessageCount = 0;
    appendMessage("system", "Chat history cleared.");
  } catch (err) {
    console.error("Error clearing chat:", err);
  }
}

function setRunningState(running) {
  isRunning = running;
  document.getElementById("btnSend").disabled = running;
  document.getElementById("btnStop").disabled = !running;

  const dot = document.getElementById("statusDot");
  const text = document.getElementById("statusText");

  if (running) {
    dot.className = "status-dot working";
    text.textContent = "Working...";
  } else {
    dot.className = "status-dot ready";
    text.textContent = "Ready";
  }
}

// MESSAGE POLLING
function startMessagePolling() {
  if (messagePollInterval) clearInterval(messagePollInterval);
  messagePollInterval = setInterval(async () => {
    try {
      const res = await fetch("/api/messages?since=" + lastMessageCount);
      const data = await res.json();

      if (data.status) {
        setRunningState(data.is_running);
        if (data.status_text) {
          document.getElementById("statusText").textContent = data.status_text;
        }
      }

      if (data.messages && data.messages.length > 0) {
        data.messages.forEach(msg => {
          appendMessage(msg.role, msg.content, msg.extra);
        });
        lastMessageCount += data.messages.length;
      }
    } catch (err) {
      // ignore transient poll errors
    }
  }, 600);
}

function appendMessage(role, content, extra = null) {
  const chatScroll = document.getElementById("chatScroll");
  const card = document.createElement("div");

  let cardClass = "agent-card";
  let avatar = "⚡";
  let author = "Devi Gravity";

  const lowerRole = (role || "").toLowerCase();
  if (lowerRole.includes("user")) {
    cardClass = "user-card";
    avatar = "👤";
    author = "You";
  } else if (lowerRole.includes("tool call")) {
    cardClass = "tool-card";
    avatar = "🛠️";
    author = "Tool Invocation";
  } else if (lowerRole.includes("tool result")) {
    cardClass = "tool-card";
    avatar = "📋";
    author = "Tool Output";
  } else if (lowerRole.includes("system")) {
    cardClass = "agent-card";
    avatar = "⚙️";
    author = "System";
  }

  card.className = `msg-card ${cardClass}`;
  card.innerHTML = `
    <div class="msg-header">
      <span class="msg-avatar">${avatar}</span>
      <span class="msg-author">${author}</span>
      <span class="msg-time">${new Date().toLocaleTimeString()}</span>
    </div>
    <div class="msg-body">${escapeHtml(content)}</div>
  `;

  chatScroll.appendChild(card);
  chatScroll.scrollTop = chatScroll.scrollHeight;
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// AUXILIARY PANELS DATA
async function loadFiles() {
  const container = document.getElementById("fileListContainer");
  container.textContent = "Loading workspace files...";
  try {
    const res = await fetch("/api/tools/files");
    const data = await res.json();
    container.textContent = data.output || "(Empty)";
  } catch (err) {
    container.textContent = "Error loading files: " + err.message;
  }
}

async function fetchGitStatus() {
  runGitAction("status");
}

async function fetchGitDiff() {
  runGitAction("diff");
}

async function fetchGitLog() {
  runGitAction("log");
}

async function commitGitChanges() {
  const msg = document.getElementById("gitCommitMsg").value.trim();
  if (!msg) {
    alert("Please enter a commit message.");
    return;
  }
  runGitAction("commit", { message: msg });
}

async function runGitAction(action, extra = {}) {
  const box = document.getElementById("gitOutputBox");
  box.textContent = `Running git ${action}...`;
  try {
    const res = await fetch("/api/tools/git", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ...extra })
    });
    const data = await res.json();
    box.textContent = data.output || "(No output)";
  } catch (err) {
    box.textContent = "Git Error: " + err.message;
  }
}

async function fetchDbTables() {
  const dbPath = document.getElementById("dbFilePathInput").value.trim() || "test.db";
  const box = document.getElementById("dbOutputBox");
  box.textContent = `Inspecting tables in '${dbPath}'...`;
  try {
    const res = await fetch("/api/tools/db", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "tables", db_path: dbPath })
    });
    const data = await res.json();
    box.textContent = data.output || "No tables found.";
  } catch (err) {
    box.textContent = "Database Error: " + err.message;
  }
}

async function runSqlQuery() {
  const dbPath = document.getElementById("dbFilePathInput").value.trim() || "test.db";
  const query = document.getElementById("sqlQueryInput").value.trim();
  if (!query) {
    alert("Please enter an SQL query.");
    return;
  }
  const box = document.getElementById("dbOutputBox");
  box.textContent = `Executing SQL on '${dbPath}'...`;
  try {
    const res = await fetch("/api/tools/db", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "query", db_path: dbPath, query: query })
    });
    const data = await res.json();
    box.textContent = data.output || "Done.";
  } catch (err) {
    box.textContent = "SQL Error: " + err.message;
  }
}

// MODAL
function openShortcutsModal() {
  const modal = document.getElementById("shortcutsModal");
  if (modal.showModal) {
    modal.showModal();
  } else {
    modal.setAttribute("open", "true");
  }
}

function closeShortcutsModal() {
  const modal = document.getElementById("shortcutsModal");
  if (modal.close) {
    modal.close();
  } else {
    modal.removeAttribute("open");
  }
}
