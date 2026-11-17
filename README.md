# Devi Gravity (Autonomous Accessible Code Agent)

Ek powerful, modern aur **NVDA Screen Reader ke saath 100% accessible** desktop software jo autonomous code planning, execution, terminal commands, database queries aur self-debugging karta hai.

---

## ⚡ UI Design: Devi Gravity

1. **Left-Hand Sidebar**:
   - **⚡ Brand Title**: Devi Gravity (Autonomous Code Agent)
   - **Active Workspace Card**: Current folder path dikhata hai aur `📂 Change Folder` (`Ctrl+O`) karne ka button hai.
   - **Navigation Tabs**:
     - 💬 **Chat & Agent Canvas** (`Alt + 1`)
     - 📁 **Workspace Files Explorer** (`Alt + 2`)
     - 🌿 **Git Repository Panel** (`Alt + 3`)
     - 🗄️ **Database (SQLite) Explorer** (`Alt + 4`)
     - ⚙️ **Settings & API Keys** (`Alt + 5`)
   - **Live Status Indicator**: Green ready pulse / Yellow working indicator aur active AI model badge.

2. **Main Chat Canvas**:
   - Modern conversation cards (You, Devi Gravity, Tool calls).
   - Multi-line accessible textarea with `Ctrl+Enter` send shortcut.
   - Quick slash action chips (`/git-status`, `/files`, `/database`, `/clear`).

---

## ♿ 100% NVDA Screen Reader Accessibility

- **Keyboard-First Navigation**: Har button, tab aur form keyboard shortcuts se navigate hota hai.
- **NVDA Speech Feedback**: Devi Gravity jab sochta hai, tool run karta hai ya complete karta hai, NVDA audio announcement se bolta hai.
- **F6 Quick Toggle**: Input box aur Chat log ke beech instant focus jump karein.

---

## ⌨️ Keyboard Shortcuts Cheat Sheet

| Shortcut | Description |
| :--- | :--- |
| **Ctrl + Enter** | Devi Gravity ko instruction / prompt send karein |
| **Escape** | Chalte hue agent ko turant rokein |
| **F6** | Prompt Input aur Chat Log ke beech focus switch karein |
| **Alt + 1** | Chat & Agent Canvas par switch karein |
| **Alt + 2** | Workspace Files explorer par switch karein |
| **Alt + 3** | Git Repository panel par switch karein |
| **Alt + 4** | Database (SQLite) panel par switch karein |
| **Alt + 5** | Settings & API Keys panel par switch karein |
| **Ctrl + O** | Workspace Folder change karein |
| **Ctrl + L** | Chat conversation clear karein |
| **F1** | Keyboard Shortcuts window kholein |

---

## 🚀 App Start Kaise Karein?

1. **One-Click Launcher (Sabse aasan):**
   - **`start.bat`** par double click karein.

2. **Terminal Se:**
   ```powershell
   python app.py
   ```

---

## ⚙️ Settings & Switchable Models (Alt + 5)

Settings mein aap kabhi bhi switch kar sakte hain:
- **Ollama**: Default, 100% Free & Offline (`qwen2.5-coder`).
- **GitHub Copilot**: GitHub token se `gpt-4o` ya `gpt-4o-mini` chalayein.
- **Google Gemini**: Direct API key (Koi Google browser login nahi).
- **Groq / OpenRouter**: Ultra-fast cloud models.
- **🔄 Reset to Default**: Ek click mein kisi bhi model se wapas default Ollama par reset karein.
