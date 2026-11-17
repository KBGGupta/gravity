import wx
import wx.html2
import os
import sys
import threading
from server import start_server, state
from accessibility import speaker

class AntigravityAgentApp(wx.Frame):
    def __init__(self, port):
        super().__init__(None, title="Devi Gravity - Autonomous Code Agent", size=(1100, 780))
        self.port = port
        self.server_url = f"http://127.0.0.1:{self.port}/"
        
        # Link workspace picker callback
        state.on_workspace_pick_callback = self.pick_workspace_dialog

        self.init_window()
        self.init_shortcuts()
        self.Centre()

        # Audio announcement for NVDA
        if state.config.get("voice_feedback", True):
            speaker.speak("Devi Gravity ready. Screen reader accessible. Press F1 for shortcuts.")

    def init_window(self):
        # Set app window title
        ws_name = os.path.basename(state.config.get('workspace_dir', '.')) or 'Workspace'
        self.SetTitle(f"Devi Gravity - [{ws_name}]")

        # Create Edge WebView2 container
        try:
            self.wv = wx.html2.WebView.New(self)
            self.wv.LoadURL(self.server_url)
        except Exception as e:
            # Fallback notification
            wx.MessageBox(
                f"Could not load WebView: {str(e)}\nOpening in default web browser instead.",
                "Notice",
                wx.OK | wx.ICON_INFORMATION
            )
            import webbrowser
            webbrowser.open(self.server_url)

    def init_shortcuts(self):
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('O'), 2001),  # Open workspace
            (wx.ACCEL_NORMAL, wx.WXK_F1, 2002), # Shortcuts help
        ])
        self.SetAcceleratorTable(accel_tbl)
        self.Bind(wx.EVT_MENU, self.on_shortcut_open_ws, id=2001)
        self.Bind(wx.EVT_MENU, self.on_shortcut_help, id=2002)

    def on_shortcut_open_ws(self, event):
        self.pick_workspace_dialog()

    def on_shortcut_help(self, event):
        help_text = (
            "Devi Gravity - Accessible Keyboard Shortcuts:\n\n"
            "• Ctrl + Enter : Send instruction to Agent\n"
            "• Escape       : Stop running Agent\n"
            "• F6           : Switch focus between Prompt Input & Chat History\n"
            "• Alt + 1      : Switch to Chat Canvas\n"
            "• Alt + 2      : Switch to Workspace Files\n"
            "• Alt + 3      : Switch to Git Repository\n"
            "• Alt + 4      : Switch to Database (SQLite)\n"
            "• Alt + 5      : Switch to Settings & Keys\n"
            "• Ctrl + O     : Change Workspace Folder\n"
            "• Ctrl + L     : Clear Chat History\n"
            "• F1           : Open this help dialog\n"
        )
        wx.MessageBox(help_text, "Devi Gravity - Shortcuts", wx.OK | wx.ICON_INFORMATION)

    def pick_workspace_dialog(self):
        dlg = wx.DirDialog(self, "Select Workspace Directory", defaultPath=state.config.get("workspace_dir", "."))
        new_path = None
        if dlg.ShowModal() == wx.ID_OK:
            new_path = dlg.GetPath()
            state.update_config({"workspace_dir": new_path})
            self.SetTitle(f"Devi Gravity - [{os.path.basename(new_path)}]")
            if state.config.get("voice_feedback", True):
                speaker.speak(f"Workspace set to {os.path.basename(new_path)}")
            # Reload page config in WebView
            if hasattr(self, 'wv'):
                self.wv.RunScript("loadConfig(); appendMessage('system', 'Workspace changed to: " + new_path.replace("\\", "\\\\") + "');")
        dlg.Destroy()
        return new_path


def main():
    # 1. Start local API & UI server
    server, port = start_server()

    # 2. Start desktop GUI
    app = wx.App(False)
    frame = AntigravityAgentApp(port)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
