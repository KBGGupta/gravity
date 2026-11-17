import os
import sys
import ctypes
import threading

class AccessibilitySpeaker:
    def __init__(self):
        self.nvda_dll = None
        self.sapi_voice = None
        self._init_nvda()
        self._init_sapi()

    def _init_nvda(self):
        # Look for nvdaControllerClient.dll in common places or local dir
        dll_names = ["nvdaControllerClient64.dll", "nvdaControllerClient32.dll", "nvdaControllerClient.dll"]
        search_dirs = [
            os.path.dirname(__file__),
            r"C:\Program Files\NVDA",
            r"C:\Program Files (x86)\NVDA",
            os.getcwd()
        ]
        
        for d in search_dirs:
            for name in dll_names:
                full_path = os.path.join(d, name)
                if os.path.exists(full_path):
                    try:
                        self.nvda_dll = ctypes.windll.LoadLibrary(full_path)
                        # Test if NVDA is running
                        if self.nvda_dll.nvdaController_testIfRunning() == 0:
                            return
                        else:
                            self.nvda_dll = None
                    except Exception:
                        self.nvda_dll = None

    def _init_sapi(self):
        try:
            import win32com.client
            self.sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
        except Exception:
            self.sapi_voice = None

    def speak(self, text: str, interrupt: bool = False, use_sapi_fallback: bool = False):
        if not text:
            return

        def _do_speak():
            spoken_by_nvda = False
            # Try NVDA first
            if self.nvda_dll:
                try:
                    if self.nvda_dll.nvdaController_testIfRunning() == 0:
                        if interrupt:
                            self.nvda_dll.nvdaController_cancelSpeech()
                        self.nvda_dll.nvdaController_speakText(str(text))
                        spoken_by_nvda = True
                except Exception:
                    spoken_by_nvda = False

            # If NVDA not available or not running, use SAPI if requested
            if not spoken_by_nvda and use_sapi_fallback and self.sapi_voice:
                try:
                    # SVSFlagsAsync = 1, SVSFPurgeBeforeSpeak = 2
                    flags = 1
                    if interrupt:
                        flags |= 2
                    self.sapi_voice.Speak(str(text), flags)
                except Exception:
                    pass

        # Run speech asynchronously so UI is never blocked
        threading.Thread(target=_do_speak, daemon=True).start()

    def braille(self, text: str):
        if self.nvda_dll:
            try:
                if self.nvda_dll.nvdaController_testIfRunning() == 0:
                    self.nvda_dll.nvdaController_brailleMessage(str(text))
            except Exception:
                pass

# Global instance
speaker = AccessibilitySpeaker()
