# -*- coding: utf-8 -*-
"""
URL to EXE Builder
Tehran by https://github.com/mahanneman MA.AD.GH

Works both as a Python script AND as a compiled EXE.
Auto-converts PNG/JPG/BMP icons to .ico using Pillow.
"""

import os
import sys
import subprocess
import threading
import tempfile
import shutil
import traceback
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ============================================================
# Author info
# ============================================================
AUTHOR_GITHUB = "https://github.com/mahanneman"
AUTHOR_TEXT = "Tehran by https://github.com/mahanneman MA.AD.GH"
APP_TITLE = "URL to EXE Builder - by MA.AD.GH"

if sys.platform == "win32":
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


# ============================================================
# 45 Advanced options
# ============================================================
ADVANCED_OPTIONS = [
    # --- Core (1-6) ---
    ("onefile",            "One file (--onefile)",                        "bool", True),
    ("windowed",           "No console (--windowed)",                     "bool", True),
    ("name",               "Output name",                                 "str",  "MyURLApp"),
    ("icon",               "Custom icon (.ico/.png/.jpg)",                "file", ""),
    ("clean",              "Clean cache (--clean)",                       "bool", True),
    ("noconfirm",          "No confirm (--noconfirm)",                    "bool", True),

    # --- Compression / UPX (7-9) ---
    ("upx_dir",            "UPX directory (--upx-dir)",                   "dir",  ""),
    ("noupx",              "Disable UPX (--noupx)",                       "bool", False),
    ("strip",              "Strip symbols (--strip)",                     "bool", False),

    # --- Imports (10-14) ---
    ("hidden_import",      "Hidden imports (--hidden-import)",            "str",  ""),
    ("exclude_module",     "Exclude module (--exclude-module)",           "str",  ""),
    ("additional_hooks",   "Additional hooks dir (--additional-hooks-dir)","dir", ""),
    ("runtime_hook",       "Runtime hook (--runtime-hook)",               "file", ""),
    ("include_package_data","Include package data (--include-package-data)","str",""),

    # --- Data bundling (15-22) ---
    ("add_data",           "Add data (--add-data)",                       "str",  ""),
    ("add_binary",         "Add binary (--add-binary)",                   "str",  ""),
    ("collect_all",        "Collect all (--collect-all)",                 "str",  ""),
    ("collect_submodules", "Collect submodules (--collect-submodules)",   "str",  ""),
    ("collect_data",       "Collect data (--collect-data)",               "str",  ""),
    ("collect_binaries",   "Collect binaries (--collect-binaries)",       "str",  ""),
    ("exclude_binary",     "Exclude binary (--exclude-binary)",           "str",  ""),
    ("recursive_copy_metadata","Recursive copy metadata (--recursive-copy-metadata)","str",""),

    # --- Metadata (23-27) ---
    ("copy_metadata",      "Copy metadata (--copy-metadata)",             "str",  ""),
    ("version_file",       "Version file (--version-file)",               "file", ""),
    ("manifest",           "Manifest (--manifest)",                       "file", ""),
    ("contents_directory", "Contents dir (--contents-directory)",         "str",  ""),
    ("no_embed_manifest",  "No embed manifest (--no-embed-manifest)",     "bool", False),

    # --- Paths (28-31) ---
    ("paths",              "Extra paths (--paths)",                       "str",  ""),
    ("distpath",           "Dist path (--distpath)",                      "dir",  ""),
    ("workpath",           "Work path (--workpath)",                      "dir",  ""),
    ("specpath",           "Spec path (--specpath)",                      "dir",  ""),

    # --- Runtime (32-38) ---
    ("log_level",          "Log level (--log-level)",                     "str",  "INFO"),
    ("debug",              "Debug (--debug)",                             "bool", False),
    ("runtime_tmpdir",     "Runtime tmpdir (--runtime-tmpdir)",           "str",  ""),
    ("uac_admin",          "UAC admin (--uac-admin)",                     "bool", False),
    ("splash",             "Splash screen (--splash)",                    "file", ""),
    ("bootloader_ignore_signals","Bootloader ignore signals (--bootloader-ignore-signals)","bool",False),
    ("keyring",            "Keyring (--keyring)",                         "str",  ""),

    # --- Advanced / NEW (39-45) ---
    ("optimize",           "Optimize bytecode (--optimize)",              "str",  "0"),
    ("target_arch",        "Target architecture (--target-architecture)", "str",  ""),
    ("python_option",      "Python option (--python-option)",             "str",  ""),
    ("debug_imports",      "Debug imports (--debug-imports)",             "bool", False),
    ("debug_bootloader",   "Debug bootloader (--debug-bootloader)",       "bool", False),
    ("debug_noarchive",    "Debug noarchive (--debug-noarchive)",         "bool", False),
    ("codesign_identity",  "Codesign identity (--codesign-identity)",     "str",  ""),
]


# ============================================================
# Right-click context menu (Copy/Paste/Cut/Select All)
# ============================================================
def _attach_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)

    def _cut():
        try: widget.event_generate("<<Cut>>")
        except Exception: pass

    def _copy():
        try: widget.event_generate("<<Copy>>")
        except Exception: pass

    def _paste():
        try: widget.event_generate("<<Paste>>")
        except Exception: pass

    def _select_all():
        try:
            if isinstance(widget, tk.Text):
                widget.tag_add("sel", "1.0", "end-1c")
                widget.mark_set("insert", "1.0")
            else:
                widget.selection_range(0, "end")
                widget.icursor("end")
        except Exception: pass

    def _clear():
        try:
            if isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, "end")
        except Exception: pass

    menu.add_command(label="Cut",        command=_cut,        accelerator="Ctrl+X")
    menu.add_command(label="Copy",       command=_copy,       accelerator="Ctrl+C")
    menu.add_command(label="Paste",      command=_paste,      accelerator="Ctrl+V")
    menu.add_separator()
    menu.add_command(label="Select All", command=_select_all, accelerator="Ctrl+A")
    menu.add_command(label="Clear",      command=_clear)

    def _show(event):
        try:
            widget.focus_set()
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    widget.bind("<Button-3>", _show)
    widget.bind("<Button-2>", _show)
    widget.bind("<Control-c>", lambda e: (_copy(), "break")[1])
    widget.bind("<Control-v>", lambda e: (_paste(), "break")[1])
    widget.bind("<Control-x>", lambda e: (_cut(), "break")[1])
    widget.bind("<Control-a>", lambda e: (_select_all(), "break")[1])


def _walk_and_attach(widget):
    for child in widget.winfo_children():
        if isinstance(child, (tk.Entry, tk.Text)):
            _attach_context_menu(child)
        _walk_and_attach(child)


# ============================================================
# Find working Python + PyInstaller
# ============================================================
def _find_python_interpreters():
    candidates = []
    if not getattr(sys, "frozen", False):
        candidates.append(sys.executable)

    if sys.platform == "win32":
        user_home = os.path.expanduser("~")
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

        common = [
            os.path.join(local_appdata, "Programs", "Python"),
            os.path.join(user_home, "AppData", "Local", "Programs", "Python"),
            os.path.join(user_home, "AppData", "Local", "Python"),
            os.path.join(user_home, "AppData", "Local", "Microsoft", "WindowsApps"),
            os.path.join(program_files, "Python"),
            os.path.join(program_files_x86, "Python"),
            r"C:\Python311", r"C:\Python312", r"C:\Python310",
            r"C:\Python39", r"C:\Python38",
        ]
        for base in common:
            if base and os.path.isdir(base):
                for entry in os.listdir(base):
                    full = os.path.join(base, entry)
                    if os.path.isdir(full):
                        exe = os.path.join(full, "python.exe")
                        if os.path.isfile(exe):
                            candidates.append(exe)

    for cmd in (["where", "python"], ["where", "py"],
                ["which", "python"], ["which", "python3"]):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8,
                                 creationflags=CREATE_NO_WINDOW)
            if res.returncode == 0:
                for line in res.stdout.strip().splitlines():
                    line = line.strip()
                    if line and os.path.isfile(line):
                        candidates.append(line)
        except Exception:
            pass

    seen = set()
    unique = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def _test_pyinstaller(python_exe):
    try:
        res = subprocess.run(
            [python_exe, "-m", "PyInstaller", "--version"],
            capture_output=True, text=True, timeout=20,
            creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0 and res.stdout.strip():
            return True, res.stdout.strip()
        return False, (res.stderr or res.stdout or "unknown").strip()
    except Exception as e:
        return False, str(e)


def find_pyinstaller_python():
    errors = []
    for py in _find_python_interpreters():
        ok, info = _test_pyinstaller(py)
        if ok:
            return py, info
        errors.append(f"{py} -> {info}")
    return None, "\n".join(errors) if errors else "No Python interpreter found."


# ============================================================
# Icon auto-conversion (PNG/JPG/BMP -> ICO)
# ============================================================
def _has_pillow(python_exe):
    try:
        res = subprocess.run(
            [python_exe, "-c", "import PIL; print(PIL.__version__)"],
            capture_output=True, text=True, timeout=20,
            creationflags=CREATE_NO_WINDOW)
        return res.returncode == 0, res.stdout.strip() or res.stderr.strip()
    except Exception as e:
        return False, str(e)


def _install_pillow(python_exe, log_func):
    log_func("[*] Pillow not found; installing it...")
    try:
        res = subprocess.run(
            [python_exe, "-m", "pip", "install", "Pillow"],
            capture_output=True, text=True, timeout=180,
            creationflags=CREATE_NO_WINDOW)
        for line in (res.stdout or "").splitlines():
            log_func("    " + line)
        if res.returncode == 0:
            log_func("[OK] Pillow installed successfully.")
            return True
        log_func(f"[!] pip install failed: {res.stderr.strip()}")
        return False
    except Exception as e:
        log_func(f"[!] Pillow install error: {e}")
        return False


def _convert_icon(python_exe, icon_path, log_func):
    """
    Convert any image to .ico using Pillow.
    Returns path to .ico file, or None on failure.
    """
    if not icon_path or not os.path.isfile(icon_path):
        return None

    ext = os.path.splitext(icon_path)[1].lower()
    if ext == ".ico":
        return icon_path

    # Need Pillow
    has, info = _has_pillow(python_exe)
    if not has:
        if not _install_pillow(python_exe, log_func):
            log_func("[!] Cannot convert icon without Pillow. Skipping icon.")
            return None

    out_dir = tempfile.mkdtemp(prefix="icon_")
    out_ico = os.path.join(out_dir, "converted.ico")

    # Run Pillow conversion in a subprocess (so it works even from a frozen EXE)
    convert_code = (
        "from PIL import Image\n"
        "import sys\n"
        f"img = Image.open(r'{icon_path}')\n"
        "img = img.convert('RGBA')\n"
        "w, h = img.size\n"
        "side = max(w, h)\n"
        "canvas = Image.new('RGBA', (side, side), (0,0,0,0))\n"
        "canvas.paste(img, ((side-w)//2, (side-h)//2))\n"
        "sizes = [(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)]\n"
        f"canvas.save(r'{out_ico}', format='ICO', sizes=sizes)\n"
        "print('OK')\n"
    )
    try:
        res = subprocess.run(
            [python_exe, "-c", convert_code],
            capture_output=True, text=True, timeout=60,
            creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0 and os.path.isfile(out_ico):
            log_func(f"[OK] Icon converted: {out_ico}")
            return out_ico
        log_func(f"[!] Icon conversion failed: {res.stderr.strip()}")
        return None
    except Exception as e:
        log_func(f"[!] Icon conversion error: {e}")
        return None


# ============================================================
# Main application
# ============================================================
class URLtoEXEBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("960x840")
        self.root.minsize(760, 620)
        self.root.configure(bg="#f0f2f5")
        self.option_vars = {}
        self.python_exe = None
        self.pyinstaller_version = None
        self._build_ui()
        self.root.after(200, lambda: _walk_and_attach(self.root))

    # --------------------------------------------------------
    def _build_ui(self):
        # URL row
        top_frame = tk.Frame(self.root, bg="#f0f2f5", pady=10)
        top_frame.pack(fill="x", padx=20)

        tk.Label(top_frame, text="Website URL:",
                 font=("Segoe UI", 12, "bold"), bg="#f0f2f5").pack(anchor="w")

        url_row = tk.Frame(top_frame, bg="#f0f2f5")
        url_row.pack(fill="x", pady=(4, 0))

        self.url_entry = tk.Entry(url_row, font=("Segoe UI", 11),
                                  relief="solid", bd=1)
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.url_entry.insert(0, "https://github.com/mahanneman")

        tk.Button(url_row, text="Paste", command=self._paste_url,
                  font=("Segoe UI", 9), padx=10).pack(side="left", padx=(6, 0))
        tk.Button(url_row, text="Test URL", command=self._test_url,
                  font=("Segoe UI", 9), padx=10).pack(side="left", padx=(6, 0))

        # Status bar
        status_frame = tk.Frame(self.root, bg="#f0f2f5")
        status_frame.pack(fill="x", padx=20, pady=(4, 0))

        self.status_lbl = tk.Label(
            status_frame, text="Checking Python + PyInstaller...",
            font=("Segoe UI", 9), bg="#f0f2f5", fg="#555")
        self.status_lbl.pack(side="left")

        tk.Button(status_frame, text="Re-check", command=self._refresh_status,
                  font=("Segoe UI", 8), padx=6).pack(side="right")

        # Advanced options
        mid_frame = tk.LabelFrame(
            self.root, text=" Advanced PyInstaller Options (45) ",
            font=("Segoe UI", 10, "bold"), bg="#f0f2f5", padx=10, pady=8)
        mid_frame.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        canvas = tk.Canvas(mid_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(mid_frame, orient="vertical",
                                  command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#ffffff")
        scrollable.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for opt_id, label, otype, default in ADVANCED_OPTIONS:
            row = tk.Frame(scrollable, bg="#ffffff")
            row.pack(fill="x", pady=2, padx=5)

            if otype == "bool":
                var = tk.BooleanVar(value=default)
                tk.Checkbutton(row, text=label, variable=var,
                               bg="#ffffff", font=("Segoe UI", 9),
                               anchor="w").pack(side="left", fill="x", expand=True)
                self.option_vars[opt_id] = var
            else:
                tk.Label(row, text=label + ":", width=44, anchor="w",
                         bg="#ffffff", font=("Segoe UI", 9)).pack(side="left")
                var = tk.StringVar(value=default if isinstance(default, str) else "")
                self.option_vars[opt_id] = var
                tk.Entry(row, textvariable=var, font=("Segoe UI", 9)).pack(
                    side="left", fill="x", expand=True, padx=(4, 4))
                if otype in ("file", "dir"):
                    tk.Button(row, text="...", width=3,
                              command=lambda v=var, t=otype: self._browse(v, t)
                              ).pack(side="left")

        # Log
        log_frame = tk.LabelFrame(self.root, text=" Build Log ",
                                  font=("Segoe UI", 10, "bold"), bg="#f0f2f5")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 5))

        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=10, font=("Consolas", 9),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Bottom
        bottom = tk.Frame(self.root, bg="#f0f2f5", pady=8)
        bottom.pack(fill="x", padx=20)

        self.build_btn = tk.Button(
            bottom, text="  Build EXE  ", command=self._start_build,
            font=("Segoe UI", 12, "bold"), bg="#2b7a4b", fg="white",
            padx=20, pady=6, activebackground="#1e5e38",
            activeforeground="white", relief="flat", cursor="hand2")
        self.build_btn.pack(side="left")

        tk.Button(bottom, text="Open Output Folder", command=self._open_output,
                  font=("Segoe UI", 9), padx=10).pack(side="left", padx=(10, 0))
        tk.Button(bottom, text="Clear Log",
                  command=lambda: self.log_text.delete("1.0", "end"),
                  font=("Segoe UI", 9), padx=10).pack(side="left", padx=(6, 0))

        author_lbl = tk.Label(
            bottom, text=AUTHOR_TEXT, font=("Segoe UI", 9, "underline"),
            fg="#0645ad", bg="#f0f2f5", cursor="hand2")
        author_lbl.pack(side="right")
        author_lbl.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_GITHUB))

    # --------------------------------------------------------
    def _paste_url(self):
        try:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, self.root.clipboard_get())
        except Exception:
            pass

    def _test_url(self):
        url = self.url_entry.get().strip()
        if url:
            webbrowser.open(url)

    def _open_output(self):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        target = desktop if os.path.isdir(desktop) else os.getcwd()
        try:
            if sys.platform == "win32":
                os.startfile(target)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def _browse(self, var, btype):
        if btype == "file":
            path = filedialog.askopenfilename(
                filetypes=[
                    ("All supported", "*.ico *.png *.jpg *.jpeg *.bmp *.gif"),
                    ("Icon files", "*.ico"),
                    ("Images", "*.png *.jpg *.jpeg *.bmp *.gif"),
                    ("All files", "*.*"),
                ])
        else:
            path = filedialog.askdirectory()
        if path:
            var.set(path)

    def _log(self, msg):
        self.log_text.insert("end", str(msg) + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def _refresh_status(self):
        self.status_lbl.config(text="Checking Python + PyInstaller...", fg="#555")
        self.root.update_idletasks()
        py, info = find_pyinstaller_python()
        if py:
            self.python_exe = py
            self.pyinstaller_version = info
            self.status_lbl.config(
                text=f"OK  |  Python: {py}  |  PyInstaller: {info}",
                fg="#1e7a3a")
        else:
            self.python_exe = None
            self.pyinstaller_version = None
            self.status_lbl.config(
                text="PyInstaller NOT found. Run: pip install pyinstaller",
                fg="#b00020")

    # --------------------------------------------------------
    # Build
    # --------------------------------------------------------
    def _start_build(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a website URL.")
            return

        self.build_btn.config(state="disabled", text="  Building...  ")
        self.log_text.delete("1.0", "end")

        self._log(f"[*] Tool mode: {'EXE (frozen)' if getattr(sys, 'frozen', False) else 'Python script'}")
        self._log(f"[*] sys.executable: {sys.executable}")
        self._log(f"[*] Platform: {sys.platform}")
        self._log(f"[*] Target URL: {url}")
        self._log(f"[*] Author: {AUTHOR_TEXT}")
        self._log("-" * 60)

        self._refresh_status()
        if not self.python_exe:
            self._log("[!] PyInstaller not found.")
            self._log("[!] Install with: pip install pyinstaller")
            self.build_btn.config(state="normal", text="  Build EXE  ")
            messagebox.showerror(
                "PyInstaller Missing",
                "PyInstaller not found.\n\nRun:\n  pip install pyinstaller")
            return

        self._log(f"[*] Using Python: {self.python_exe}")
        self._log(f"[*] PyInstaller: {self.pyinstaller_version}")
        self._log("-" * 60)

        threading.Thread(target=self._build, args=(url,), daemon=True).start()

    def _build(self, url):
        try:
            tmpdir = tempfile.mkdtemp(prefix="url2exe_")
            self._log(f"[*] Temp directory: {tmpdir}")

            script_path = os.path.join(tmpdir, "launcher.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write("import webbrowser\n")
                f.write("import sys\n")
                f.write(f"webbrowser.open({repr(url)})\n")
                f.write("sys.exit(0)\n")

            dist_dir = os.path.join(tmpdir, "dist")
            work_dir = os.path.join(tmpdir, "build")
            spec_dir = tmpdir

            if self.option_vars["distpath"].get().strip():
                dist_dir = self.option_vars["distpath"].get().strip()
            if self.option_vars["workpath"].get().strip():
                work_dir = self.option_vars["workpath"].get().strip()
            if self.option_vars["specpath"].get().strip():
                spec_dir = self.option_vars["specpath"].get().strip()

            exe_name = self.option_vars["name"].get().strip() or "launcher"

            # ---- Icon handling (auto-convert PNG/JPG to ICO) ----
            icon_val = self.option_vars["icon"].get().strip()
            if icon_val:
                if not os.path.isfile(icon_val):
                    self._log(f"[!] Icon file not found: {icon_val}")
                    self._log("[!] Skipping icon.")
                else:
                    ext = os.path.splitext(icon_val)[1].lower()
                    if ext != ".ico":
                        self._log(f"[*] Detected non-ICO icon ({ext}); converting...")
                        converted = _convert_icon(self.python_exe, icon_val, self._log)
                        if converted:
                            self.option_vars["icon"].set(converted)
                        else:
                            self._log("[!] Icon conversion failed; building without icon.")
                            self.option_vars["icon"].set("")

            cmd = [self.python_exe, "-m", "PyInstaller"]
            cmd += ["--noconfirm",
                    "--distpath", dist_dir,
                    "--workpath", work_dir,
                    "--specpath", spec_dir]

            bool_map = {
                "onefile":                    "--onefile",
                "windowed":                   "--windowed",
                "clean":                      "--clean",
                "noupx":                      "--noupx",
                "debug":                      "--debug",
                "strip":                      "--strip",
                "uac_admin":                  "--uac-admin",
                "no_embed_manifest":          "--no-embed-manifest",
                "bootloader_ignore_signals":  "--bootloader-ignore-signals",
                "debug_imports":              "--debug-imports",
                "debug_bootloader":           "--debug-bootloader",
                "debug_noarchive":            "--debug-noarchive",
            }
            for key, flag in bool_map.items():
                if self.option_vars[key].get():
                    cmd.append(flag)

            str_map = {
                "name":                    "--name",
                "hidden_import":           "--hidden-import",
                "exclude_module":          "--exclude-module",
                "include_package_data":    "--include-package-data",
                "add_data":                "--add-data",
                "add_binary":              "--add-binary",
                "collect_all":             "--collect-all",
                "collect_submodules":      "--collect-submodules",
                "collect_data":            "--collect-data",
                "collect_binaries":        "--collect-binaries",
                "exclude_binary":          "--exclude-binary",
                "recursive_copy_metadata": "--recursive-copy-metadata",
                "copy_metadata":           "--copy-metadata",
                "contents_directory":      "--contents-directory",
                "paths":                   "--paths",
                "log_level":               "--log-level",
                "runtime_tmpdir":          "--runtime-tmpdir",
                "keyring":                 "--keyring",
                "optimize":                "--optimize",
                "target_arch":             "--target-architecture",
                "python_option":           "--python-option",
                "codesign_identity":       "--codesign-identity",
            }
            for key, flag in str_map.items():
                val = self.option_vars[key].get().strip()
                if val:
                    cmd.extend([flag, val])

            file_map = {
                "icon":             "--icon",
                "upx_dir":          "--upx-dir",
                "additional_hooks": "--additional-hooks-dir",
                "runtime_hook":     "--runtime-hook",
                "version_file":     "--version-file",
                "manifest":         "--manifest",
                "splash":           "--splash",
            }
            for key, flag in file_map.items():
                val = self.option_vars[key].get().strip()
                if val:
                    cmd.extend([flag, val])

            cmd.append(script_path)

            self._log("[*] Command:")
            pretty = " ".join(f'"{c}"' if " " in c else c for c in cmd)
            self._log("    " + pretty)
            self._log("-" * 60)

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                cwd=tmpdir, creationflags=CREATE_NO_WINDOW)

            for line in process.stdout:
                self._log(line.rstrip())
            process.wait()

            if process.returncode != 0:
                self._log(f"\n[!] Build failed. Return code: {process.returncode}")
                return

            exe_path = os.path.join(dist_dir, exe_name + ".exe")
            self._log(f"[*] Looking for: {exe_path}")

            if not os.path.exists(exe_path) and os.path.isdir(dist_dir):
                sub = os.path.join(dist_dir, exe_name, exe_name + ".exe")
                if os.path.exists(sub):
                    exe_path = sub
                else:
                    for name in os.listdir(dist_dir):
                        full = os.path.join(dist_dir, name)
                        if name.lower().endswith(".exe"):
                            exe_path = full
                            break

            if not os.path.exists(exe_path):
                self._log("[!] EXE not found after build.")
                return

            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.isdir(desktop):
                desktop = os.getcwd()
            final_path = os.path.join(desktop, os.path.basename(exe_path))

            try:
                shutil.copy2(exe_path, final_path)
            except PermissionError:
                final_path = os.path.join(os.getcwd(), os.path.basename(exe_path))
                shutil.copy2(exe_path, final_path)
                self._log("[!] Desktop write denied; saved to current folder.")

            self._log("-" * 60)
            self._log(f"[OK] SUCCESS! EXE created at:")
            self._log(f"     {final_path}")
            self._log(f"[OK] Double-click it to open: {url}")

            messagebox.showinfo("Build Complete",
                                f"EXE created successfully:\n\n{final_path}")

        except Exception:
            self._log("\n[!] EXCEPTION:")
            self._log(traceback.format_exc())
            messagebox.showerror("Build Error", "See log for details.")
        finally:
            self.build_btn.config(state="normal", text="  Build EXE  ")


# ============================================================
def main():
    root = tk.Tk()
    app = URLtoEXEBuilder(root)
    root.after(300, app._refresh_status)
    root.mainloop()


if __name__ == "__main__":
    main()