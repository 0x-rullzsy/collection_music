"""
███╗   ███╗██╗   ██╗███████╗██╗ ██████╗    ███╗   ███╗ ██████╗ ██████╗
████╗ ████║██║   ██║██╔════╝██║██╔════╝    ████╗ ████║██╔════╝ ██╔══██╗
██╔████╔██║██║   ██║███████╗██║██║         ██╔████╔██║██║  ███╗██████╔╝
██║╚██╔╝██║██║   ██║╚════██║██║██║         ██║╚██╔╝██║██║   ██║██╔══██╗
██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗    ██║ ╚═╝ ██║╚██████╔╝██║  ██║
╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝
RullzsyHUB - Music Manager Tool
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, threading, subprocess, time, sys
from pathlib import Path
from urllib.parse import quote

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
JSON_FILE        = "list_music.json"
REPO_DIR         = os.path.dirname(os.path.abspath(__file__))
GITHUB_RAW_BASE  = "https://raw.githubusercontent.com/0x-rullzsy/collection_music/refs/heads/main/"
ITEMS_PER_PAGE   = 12

# ─────────────────────────────────────────────────────────────────────────────
# TEMA — Red Dark / Hacker
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg"       : "#0a0a0f",
    "surface"  : "#12121a",
    "card"     : "#1a1a26",
    "card2"    : "#1f1f2e",
    "border"   : "#2a1a2a",
    "accent"   : "#cc0000",
    "accent2"  : "#ff3333",
    "accent3"  : "#ff6666",
    "glow"     : "#8b0000",
    "success"  : "#22c55e",
    "warning"  : "#f59e0b",
    "danger"   : "#ef4444",
    "text"     : "#e8e8f0",
    "subtext"  : "#888899",
    "dim"      : "#555566",
    "white"    : "#ffffff",
    "input_bg" : "#0f0f1a",
    "hover"    : "#2a0a0a",
}

FONT_TITLE  = ("Consolas", 22, "bold")
FONT_HEADER = ("Consolas", 13, "bold")
FONT_BODY   = ("Consolas", 10)
FONT_SMALL  = ("Consolas", 9)
FONT_MONO   = ("Courier New", 9)
FONT_BTN    = ("Consolas", 10, "bold")
FONT_BRAND  = ("Consolas", 28, "bold")


# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
def load_data():
    p = os.path.join(REPO_DIR, JSON_FILE)
    if not os.path.exists(p):
        save_data([])
        return []
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    p = os.path.join(REPO_DIR, JSON_FILE)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def build_url(filename):
    """Build GitHub raw URL dari nama file."""
    encoded = quote(filename)
    return GITHUB_RAW_BASE + encoded

def extract_filename_from_url(url):
    from urllib.parse import unquote
    return unquote(url.split("/")[-1])


# ─────────────────────────────────────────────────────────────────────────────
# GIT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def git_cmd(args, cwd=None):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or REPO_DIR,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        return "", "Git not found. Pastikan git sudah terinstall.", 1

def git_push_with_progress(commit_msg, extra_files=None, log_cb=None):
    def log(pct, msg):
        if log_cb:
            log_cb(pct, msg)

    log(0, "⚡ Memulai proses git...")
    time.sleep(0.3)

    files_to_add = [JSON_FILE]
    if extra_files:
        files_to_add += extra_files

    log(15, f"📁 git add {len(files_to_add)} file(s)...")
    out, err, code = git_cmd(["add"] + files_to_add)
    if code != 0:
        log(-1, f"❌ Error git add: {err}")
        return False, err

    log(35, "✅ Files staged.")
    time.sleep(0.2)

    log(50, f"💾 git commit...")
    out, err, code = git_cmd(["commit", "-m", commit_msg])
    if code != 0 and "nothing to commit" not in out + err:
        log(-1, f"❌ Error git commit: {err or out}")
        return False, err or out
    if "nothing to commit" in out + err:
        log(60, "ℹ️  Nothing to commit — sudah up to date.")
    else:
        log(65, "✅ Commit berhasil.")
    time.sleep(0.3)

    log(70, "🚀 git push origin main ...")
    out, err, code = git_cmd(["push", "origin", "main"])
    if code != 0:
        log(-1, f"❌ Error git push: {err}")
        return False, err

    log(100, "🎉 Push berhasil! Perubahan sudah live di GitHub.")
    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM WIDGETS
# ─────────────────────────────────────────────────────────────────────────────
class HoverButton(tk.Button):
    def __init__(self, master, hover_bg=None, hover_fg=None, **kw):
        self._normal_bg = kw.get("bg", C["card"])
        self._normal_fg = kw.get("fg", C["text"])
        self._hover_bg  = hover_bg or C["hover"]
        self._hover_fg  = hover_fg or C["white"]
        super().__init__(master, **kw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _):
        self.config(bg=self._hover_bg, fg=self._hover_fg)

    def _on_leave(self, _):
        self.config(bg=self._normal_bg, fg=self._normal_fg)


class RedEntry(tk.Entry):
    def __init__(self, master, placeholder="", **kw):
        self._ph = placeholder
        kw.setdefault("bg", C["input_bg"])
        kw.setdefault("fg", C["text"])
        kw.setdefault("insertbackground", C["accent2"])
        kw.setdefault("relief", "flat")
        kw.setdefault("font", FONT_BODY)
        kw.setdefault("highlightthickness", 1)
        kw.setdefault("highlightcolor", C["accent"])
        kw.setdefault("highlightbackground", C["border"])
        super().__init__(master, **kw)
        if placeholder:
            self._show_placeholder()
            self.bind("<FocusIn>",  self._on_focus_in)
            self.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        self.insert(0, self._ph)
        self.config(fg=C["dim"])

    def _on_focus_in(self, _):
        if self.get() == self._ph:
            self.delete(0, tk.END)
            self.config(fg=C["text"])

    def _on_focus_out(self, _):
        if not self.get():
            self._show_placeholder()

    def get_real(self):
        v = self.get()
        return "" if v == self._ph else v

    def set_value(self, val):
        self.delete(0, tk.END)
        if val:
            self.insert(0, val)
            self.config(fg=C["text"])
        else:
            self._show_placeholder()


# ─────────────────────────────────────────────────────────────────────────────
# MP3 DROP ZONE (multiple files)
# ─────────────────────────────────────────────────────────────────────────────
class Mp3DropZone(tk.Frame):
    """Drag-and-drop zone untuk file MP3, support multiple."""
    def __init__(self, master, on_drop=None, multiple=True, **kw):
        kw.setdefault("bg", C["input_bg"])
        kw.setdefault("relief", "flat")
        kw.setdefault("highlightthickness", 2)
        kw.setdefault("highlightbackground", C["border"])
        super().__init__(master, **kw)
        self.on_drop  = on_drop
        self.multiple = multiple
        self._paths   = []
        self._build()
        self._try_enable_dnd()

    def _build(self):
        self.config(height=90)
        self._label = tk.Label(
            self,
            text="🎵  Drag & Drop file .mp3 di sini\n     atau klik untuk browse (support multiple)",
            bg=C["input_bg"], fg=C["dim"],
            font=FONT_SMALL, justify="center", cursor="hand2"
        )
        self._label.place(relx=0.5, rely=0.5, anchor="center")
        self._label.bind("<Button-1>", self._browse)
        self.bind("<Button-1>", self._browse)

    def _try_enable_dnd(self):
        try:
            self.drop_target_register("DND_Files")  # type: ignore
            self.dnd_bind("<<Drop>>", self._on_dnd_drop)
        except Exception:
            pass

    def _on_dnd_drop(self, event):
        raw = event.data.strip()
        # tkinterdnd2 returns paths space-separated, wrapped in {} if space in name
        import re
        paths = re.findall(r'\{[^}]+\}|\S+', raw)
        paths = [p.strip("{}") for p in paths]
        mp3s = [p for p in paths if p.lower().endswith(".mp3")]
        if not mp3s:
            self._label.config(text="⚠️  Hanya file .mp3 yang diterima!", fg=C["danger"])
            return
        self._handle_files(mp3s)

    def _browse(self, _=None):
        if self.multiple:
            paths = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        else:
            p = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
            paths = (p,) if p else ()
        if paths:
            self._handle_files(list(paths))

    def _handle_files(self, paths):
        bad = [p for p in paths if not p.lower().endswith(".mp3")]
        if bad:
            self._label.config(text="⚠️  Hanya file .mp3 yang diterima!", fg=C["danger"])
            return
        self._paths = paths
        n = len(paths)
        if n == 1:
            fname = os.path.basename(paths[0])
            self._label.config(text=f"✅  {fname}\n(siap diupload)", fg=C["success"])
        else:
            self._label.config(text=f"✅  {n} file MP3 dipilih\n(siap diupload)", fg=C["success"])
        if self.on_drop:
            self.on_drop(paths)

    def get_paths(self):
        return self._paths

    def reset(self):
        self._paths = []
        self._label.config(
            text="🎵  Drag & Drop file .mp3 di sini\n     atau klik untuk browse (support multiple)",
            fg=C["dim"]
        )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────
class MusicManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RullzsyHUB — Music Manager")
        self.geometry("1150x720")
        self.minsize(960, 600)
        self.configure(bg=C["bg"])

        # State
        self.data         = load_data()
        self.current_page = 1
        self.search_var   = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())

        self._build_ui()
        self._refresh()

    # ── UI BUILD ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=C["surface"], height=70)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        tk.Label(
            hdr, text="⬡ RullzsyHUB",
            bg=C["surface"], fg=C["accent2"],
            font=("Consolas", 20, "bold")
        ).pack(side="left", padx=24, pady=12)

        tk.Label(
            hdr, text="// MUSIC MANAGER v1.0",
            bg=C["surface"], fg=C["dim"],
            font=("Consolas", 9)
        ).pack(side="left", pady=20)

        self._status_lbl = tk.Label(
            hdr, text="", bg=C["surface"], fg=C["success"], font=FONT_SMALL
        )
        self._status_lbl.pack(side="right", padx=20)

        # ── Separator ──
        tk.Frame(self, bg=C["accent"], height=2).pack(fill="x")

        # ── Toolbar ──
        tb = tk.Frame(self, bg=C["surface"], pady=10)
        tb.pack(fill="x")

        tk.Label(tb, text="🔍", bg=C["surface"], fg=C["subtext"], font=FONT_BODY).pack(side="left", padx=(18,4))
        self._search_entry = RedEntry(tb, placeholder="Cari musik...", width=30)
        self._search_entry.pack(side="left", ipady=5)
        self._search_entry.bind("<KeyRelease>", lambda e: self._on_search())

        # Total badge
        self._total_badge = tk.Label(
            tb, text="", bg=C["surface"], fg=C["accent2"], font=FONT_SMALL
        )
        self._total_badge.pack(side="left", padx=16)

        # Buttons (right side)
        HoverButton(
            tb, text="⬆  Apply Changes",
            bg=C["glow"], fg=C["white"],
            hover_bg="#aa0000", hover_fg=C["white"],
            font=FONT_BTN, relief="flat", padx=14, pady=5,
            cursor="hand2", command=self._apply_changes
        ).pack(side="right", padx=4)

        HoverButton(
            tb, text="＋  Add Music",
            bg=C["accent"], fg=C["white"],
            hover_bg=C["accent2"], hover_fg=C["white"],
            font=FONT_BTN, relief="flat", padx=16, pady=5,
            cursor="hand2", command=self._open_add_modal
        ).pack(side="right", padx=(0,4))

        # ── Info bar ──
        info = tk.Frame(self, bg=C["bg"])
        info.pack(fill="x", padx=20, pady=(8,0))
        self._count_lbl = tk.Label(info, text="", bg=C["bg"], fg=C["subtext"], font=FONT_SMALL)
        self._count_lbl.pack(side="left")

        # ── List area ──
        self._list_frame = tk.Frame(self, bg=C["bg"])
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=8)

        # ── Pagination ──
        self._pag_frame = tk.Frame(self, bg=C["bg"])
        self._pag_frame.pack(fill="x", padx=20, pady=(0,12))

    # ── STATUS ────────────────────────────────────────────────────────────────
    def _set_status(self, msg, color=None):
        self._status_lbl.config(text=msg, fg=color or C["success"])
        self.after(4000, lambda: self._status_lbl.config(text=""))

    # ── SEARCH ────────────────────────────────────────────────────────────────
    def _on_search(self):
        self.current_page = 1
        self._refresh()

    def _filtered(self):
        q = self._search_entry.get_real().lower().strip()
        result = []
        for i, m in enumerate(self.data):
            if q and q not in m.get("name","").lower() and q not in m.get("filename","").lower():
                continue
            result.append((i, m))
        return result

    # ── REFRESH / RENDER ──────────────────────────────────────────────────────
    def _refresh(self):
        items  = self._filtered()
        total  = len(items)
        pages  = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        if self.current_page > pages:
            self.current_page = pages

        start     = (self.current_page - 1) * ITEMS_PER_PAGE
        page_data = items[start:start + ITEMS_PER_PAGE]

        # Total badge
        self._total_badge.config(text=f"🎵 {len(self.data)} lagu total")

        self._count_lbl.config(
            text=f"Menampilkan {len(page_data)} dari {total}  |  Halaman {self.current_page}/{pages}"
        )

        for w in self._list_frame.winfo_children():
            w.destroy()

        self._render_header()
        for disp_idx, (real_idx, m) in enumerate(page_data):
            self._render_row(disp_idx, m, real_idx)

        self._render_pagination(pages)

    def _render_header(self):
        hdr = tk.Frame(self._list_frame, bg=C["card2"], pady=6)
        hdr.pack(fill="x", pady=(0,2))
        cols = [("#", 4), ("Nama Lagu", 32), ("Filename", 34), ("Aksi", 16)]
        for label, w in cols:
            tk.Label(
                hdr, text=label, bg=C["card2"], fg=C["accent2"],
                font=("Consolas", 9, "bold"), width=w, anchor="w"
            ).pack(side="left", padx=(6,0))

    def _render_row(self, disp_idx, m, real_idx):
        row_bg = C["card"] if disp_idx % 2 == 0 else C["card2"]
        row    = tk.Frame(self._list_frame, bg=row_bg, pady=4)
        row.pack(fill="x", pady=1)

        page_start = (self.current_page - 1) * ITEMS_PER_PAGE
        display_no = page_start + disp_idx + 1

        tk.Label(row, text=str(display_no), bg=row_bg, fg=C["dim"],
                 font=FONT_SMALL, width=4, anchor="w").pack(side="left", padx=(8,0))

        tk.Label(row, text=m.get("name",""), bg=row_bg, fg=C["text"],
                 font=("Consolas", 10, "bold"), width=32, anchor="w").pack(side="left", padx=(6,0))

        fname = m.get("filename","")
        tk.Label(row, text=fname, bg=row_bg, fg=C["subtext"],
                 font=FONT_MONO, width=34, anchor="w").pack(side="left", padx=(6,0))

        # Action buttons
        act = tk.Frame(row, bg=row_bg)
        act.pack(side="left", padx=6)

        HoverButton(
            act, text="✏", bg=row_bg, fg=C["warning"],
            hover_bg=C["card"], hover_fg=C["warning"],
            font=FONT_SMALL, relief="flat", padx=6, pady=2,
            cursor="hand2", command=lambda ri=real_idx: self._open_edit_modal(ri)
        ).pack(side="left", padx=2)

        HoverButton(
            act, text="🗑", bg=row_bg, fg=C["danger"],
            hover_bg=C["card"], hover_fg=C["danger"],
            font=FONT_SMALL, relief="flat", padx=6, pady=2,
            cursor="hand2", command=lambda ri=real_idx: self._delete_music(ri)
        ).pack(side="left", padx=2)

    def _render_pagination(self, pages):
        for w in self._pag_frame.winfo_children():
            w.destroy()

        if pages <= 1:
            return

        def go(p):
            self.current_page = p
            self._refresh()

        HoverButton(
            self._pag_frame, text="◀ Prev",
            bg=C["card"], fg=C["text"],
            hover_bg=C["accent"], hover_fg=C["white"],
            font=FONT_SMALL, relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=lambda: go(max(1, self.current_page - 1))
        ).pack(side="left", padx=2)

        for p in range(1, pages + 1):
            is_cur = (p == self.current_page)
            HoverButton(
                self._pag_frame, text=str(p),
                bg=C["accent"] if is_cur else C["card"],
                fg=C["white"] if is_cur else C["text"],
                hover_bg=C["accent2"], hover_fg=C["white"],
                font=FONT_SMALL, relief="flat", padx=8, pady=4,
                cursor="hand2", command=lambda pp=p: go(pp)
            ).pack(side="left", padx=1)

        HoverButton(
            self._pag_frame, text="Next ▶",
            bg=C["card"], fg=C["text"],
            hover_bg=C["accent"], hover_fg=C["white"],
            font=FONT_SMALL, relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=lambda: go(min(pages, self.current_page + 1))
        ).pack(side="left", padx=2)

    # ── MODAL HELPER ──────────────────────────────────────────────────────────
    def _make_modal(self, title, width=580, height=520):
        modal = tk.Toplevel(self)
        modal.title(title)
        modal.geometry(f"{width}x{height}")
        modal.configure(bg=C["surface"])
        modal.resizable(False, False)
        modal.grab_set()
        modal.transient(self)

        # Title bar
        tk.Frame(modal, bg=C["accent"], height=3).pack(fill="x")
        tk.Label(
            modal, text=title,
            bg=C["surface"], fg=C["accent2"],
            font=FONT_HEADER, pady=14
        ).pack(fill="x", padx=20)
        tk.Frame(modal, bg=C["border"], height=1).pack(fill="x", padx=20)

        return modal

    # ── ADD MUSIC MODAL (multiple) ────────────────────────────────────────────
    def _open_add_modal(self):
        modal = self._make_modal("＋ Add Music", width=620, height=620)
        body  = tk.Frame(modal, bg=C["surface"])
        body.pack(fill="both", expand=True, padx=28, pady=10)

        # Info
        tk.Label(
            body,
            text="Tambahkan satu atau beberapa lagu sekaligus.\n"
                 "File MP3 akan dicopy ke folder repo lalu di-push ke GitHub.",
            bg=C["surface"], fg=C["subtext"], font=FONT_SMALL, justify="left"
        ).pack(anchor="w", pady=(0,10))

        # Drop zone
        tk.Label(body, text="File MP3:", bg=C["surface"], fg=C["subtext"],
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(0,4))

        self._add_mp3_paths = []
        self._add_name_entries = []  # list of RedEntry for custom names

        # Selected files list frame (scrollable)
        files_outer = tk.Frame(body, bg=C["surface"])
        files_outer.pack(fill="x")

        drop_zone = Mp3DropZone(files_outer, multiple=True, height=80)
        drop_zone.pack(fill="x")

        # Scrollable name override section
        names_label = tk.Label(body, text="Nama lagu (opsional — kosongkan = pakai nama file):",
                               bg=C["surface"], fg=C["subtext"], font=FONT_SMALL, anchor="w")
        names_label.pack(fill="x", pady=(10,2))

        names_canvas = tk.Canvas(body, bg=C["surface"], height=160, highlightthickness=0)
        names_scrollbar = tk.Scrollbar(body, orient="vertical", command=names_canvas.yview)
        names_canvas.configure(yscrollcommand=names_scrollbar.set)

        names_canvas.pack(side="left", fill="both", expand=True)
        names_scrollbar.pack(side="right", fill="y")

        names_inner = tk.Frame(names_canvas, bg=C["surface"])
        names_window = names_canvas.create_window((0, 0), window=names_inner, anchor="nw")

        def on_names_configure(e):
            names_canvas.configure(scrollregion=names_canvas.bbox("all"))
            names_canvas.itemconfig(names_window, width=names_canvas.winfo_width())

        names_inner.bind("<Configure>", on_names_configure)
        names_canvas.bind("<Configure>", lambda e: names_canvas.itemconfig(names_window, width=e.width))

        def on_mp3_drop(paths):
            self._add_mp3_paths = paths
            # Clear name entries
            for w in names_inner.winfo_children():
                w.destroy()
            self._add_name_entries = []
            for p in paths:
                fname   = os.path.basename(p)
                row     = tk.Frame(names_inner, bg=C["surface"])
                row.pack(fill="x", pady=2)
                tk.Label(row, text=f"📄 {fname[:38]}", bg=C["surface"], fg=C["dim"],
                         font=FONT_SMALL, width=42, anchor="w").pack(side="left", padx=(0,6))
                e = RedEntry(row, placeholder="Nama custom (opsional)", width=28)
                e.pack(side="left", ipady=4, fill="x", expand=True)
                self._add_name_entries.append((fname, e))

        drop_zone.on_drop = on_mp3_drop

        # Progress
        prog_frame = tk.Frame(modal, bg=C["surface"])
        prog_frame.pack(fill="x", padx=28, pady=(4,0))
        prog_bar = ttk.Progressbar(prog_frame, length=560, mode="determinate",
                                   style="red.Horizontal.TProgressbar")
        prog_log  = tk.Label(prog_frame, text="", bg=C["surface"], fg=C["subtext"],
                             font=FONT_SMALL, wraplength=540, justify="left")

        # Buttons
        btn_frame = tk.Frame(modal, bg=C["surface"])
        btn_frame.pack(side="bottom", fill="x", padx=28, pady=14)

        def do_add():
            paths = self._add_mp3_paths
            if not paths:
                messagebox.showerror("Error", "Pilih minimal satu file MP3!", parent=modal)
                return

            # Collect name overrides
            entries = self._add_name_entries
            songs   = []  # list of (src_path, filename, display_name)
            for src_path in paths:
                fname = os.path.basename(src_path)
                # find matching entry
                custom_name = ""
                for (efname, ewidget) in entries:
                    if efname == fname:
                        custom_name = ewidget.get_real().strip()
                        break
                stem        = os.path.splitext(fname)[0]
                display_name = custom_name if custom_name else stem
                songs.append((src_path, fname, display_name))

            # Check duplicates in existing list
            existing_fnames = {m.get("filename","") for m in self.data}
            dupes = [s[1] for s in songs if s[1] in existing_fnames]
            if dupes:
                if not messagebox.askyesno(
                    "Duplikat", f"{len(dupes)} file sudah ada:\n{chr(10).join(dupes)}\n\nTetap tambahkan?",
                    parent=modal
                ):
                    return

            add_btn.config(state="disabled", text="Menambahkan...")
            prog_bar.pack(fill="x", pady=(4,0))
            prog_log.pack(fill="x", pady=2)

            def task():
                extra_files = []
                total_songs = len(songs)
                for i, (src_path, fname, display_name) in enumerate(songs):
                    pct = int(10 + (i / total_songs) * 40)
                    def _log(p=pct, fn=fname):
                        prog_bar["value"] = p
                        prog_log.config(text=f"📋 Copying {fn}...", fg=C["subtext"])
                    self.after(0, _log)

                    dest = os.path.join(REPO_DIR, fname)
                    try:
                        import shutil
                        shutil.copy2(src_path, dest)
                        extra_files.append(fname)
                    except Exception as ex:
                        self.after(0, lambda ex=ex: messagebox.showerror(
                            "Error", f"Gagal copy file:\n{ex}", parent=modal))
                        self.after(0, lambda: add_btn.config(state="normal", text="✔  Add Music"))
                        return

                    # Add to data
                    url = build_url(fname)
                    entry = {"name": display_name, "filename": fname, "url": url}
                    self.data.append(entry)

                # Sort alphabetically by name
                self.data.sort(key=lambda x: x.get("name","").lower())
                save_data(self.data)

                def log_cb(pct, msg):
                    def _upd():
                        if pct >= 0:
                            prog_bar["value"] = 50 + int(pct * 0.5)
                        prog_log.config(
                            text=msg,
                            fg=C["success"] if pct == 100 else (C["danger"] if pct < 0 else C["subtext"])
                        )
                    self.after(0, _upd)

                ok, err = git_push_with_progress(
                    f"Add {len(songs)} song(s): {', '.join(s[2] for s in songs[:3])}{'...' if len(songs)>3 else ''}",
                    extra_files=extra_files, log_cb=log_cb
                )

                def finish():
                    add_btn.config(state="normal", text="✔  Add Music")
                    if ok:
                        self._set_status(f"✅ {len(songs)} lagu berhasil ditambahkan!", C["success"])
                        self._refresh()
                        self.after(1500, modal.destroy)
                    else:
                        messagebox.showerror("Git Error", f"Push gagal:\n{err}", parent=modal)

                self.after(0, finish)

            threading.Thread(target=task, daemon=True).start()

        add_btn = HoverButton(
            btn_frame, text="✔  Add Music",
            bg=C["accent"], fg=C["white"],
            hover_bg=C["accent2"], hover_fg=C["white"],
            font=FONT_BTN, relief="flat", padx=18, pady=7,
            cursor="hand2", command=do_add
        )
        add_btn.pack(side="right", padx=(8,0))

        HoverButton(
            btn_frame, text="Batal",
            bg=C["card"], fg=C["text"],
            hover_bg=C["card2"], hover_fg=C["text"],
            font=FONT_BTN, relief="flat", padx=14, pady=7,
            cursor="hand2", command=modal.destroy
        ).pack(side="right")

        # Setup progressbar style
        self._setup_style()

    # ── EDIT MODAL ────────────────────────────────────────────────────────────
    def _open_edit_modal(self, idx):
        m     = self.data[idx]
        modal = self._make_modal("✏ Edit Lagu", width=540, height=400)
        body  = tk.Frame(modal, bg=C["surface"])
        body.pack(fill="both", expand=True, padx=28, pady=10)

        tk.Label(body, text="Nama Lagu:", bg=C["surface"], fg=C["subtext"],
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(0,2))
        e_name = RedEntry(body, placeholder="Nama lagu", width=50)
        e_name.set_value(m.get("name",""))
        e_name.pack(fill="x", ipady=6)

        tk.Label(body, text="Filename (.mp3):", bg=C["surface"], fg=C["subtext"],
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(10,2))
        e_fname = RedEntry(body, placeholder="nama_file.mp3", width=50)
        e_fname.set_value(m.get("filename",""))
        e_fname.pack(fill="x", ipady=6)

        tk.Label(body, text="URL (auto-generate dari filename):", bg=C["surface"],
                 fg=C["dim"], font=FONT_SMALL, anchor="w").pack(fill="x", pady=(10,2))
        url_lbl = tk.Label(body, text=m.get("url",""), bg=C["input_bg"], fg=C["dim"],
                           font=FONT_MONO, anchor="w", wraplength=480, justify="left", pady=4)
        url_lbl.pack(fill="x", padx=2)

        def update_url_preview(*_):
            fn = e_fname.get_real().strip()
            if fn:
                if not fn.endswith(".mp3"):
                    fn += ".mp3"
                url_lbl.config(text=build_url(fn))

        e_fname.bind("<KeyRelease>", update_url_preview)

        # Progress
        prog_frame = tk.Frame(modal, bg=C["surface"])
        prog_frame.pack(fill="x", padx=28, pady=(8,0))
        prog_bar = ttk.Progressbar(prog_frame, length=480, mode="determinate",
                                   style="red.Horizontal.TProgressbar")
        prog_log  = tk.Label(prog_frame, text="", bg=C["surface"], fg=C["subtext"],
                             font=FONT_SMALL, wraplength=460, justify="left")

        btn_frame = tk.Frame(modal, bg=C["surface"])
        btn_frame.pack(side="bottom", fill="x", padx=28, pady=14)

        def do_save():
            new_name  = e_name.get_real().strip()
            new_fname = e_fname.get_real().strip()

            if not new_name or not new_fname:
                messagebox.showerror("Error", "Nama dan filename tidak boleh kosong!", parent=modal)
                return

            if not new_fname.endswith(".mp3"):
                new_fname += ".mp3"

            new_url = build_url(new_fname)

            save_btn.config(state="disabled", text="Menyimpan...")
            prog_bar.pack(fill="x", pady=(4,0))
            prog_log.pack(fill="x", pady=2)

            def task():
                self.data[idx]["name"]     = new_name
                self.data[idx]["filename"] = new_fname
                self.data[idx]["url"]      = new_url
                save_data(self.data)

                def log_cb(pct, msg):
                    def _upd():
                        if pct >= 0:
                            prog_bar["value"] = pct
                        prog_log.config(
                            text=msg,
                            fg=C["success"] if pct == 100 else (C["danger"] if pct < 0 else C["subtext"])
                        )
                    self.after(0, _upd)

                ok, err = git_push_with_progress(f"Edit song: {new_name}", log_cb=log_cb)

                def finish():
                    save_btn.config(state="normal", text="Apply Changes")
                    if ok:
                        self._set_status(f"✅ '{new_name}' berhasil diupdate!", C["success"])
                        self._refresh()
                        self.after(1500, modal.destroy)
                    else:
                        messagebox.showerror("Git Error", f"Push gagal:\n{err}", parent=modal)

                self.after(0, finish)

            threading.Thread(target=task, daemon=True).start()

        save_btn = HoverButton(
            btn_frame, text="✔  Apply Changes",
            bg=C["accent"], fg=C["white"],
            hover_bg=C["accent2"], hover_fg=C["white"],
            font=FONT_BTN, relief="flat", padx=18, pady=7,
            cursor="hand2", command=do_save
        )
        save_btn.pack(side="right", padx=(8,0))

        HoverButton(
            btn_frame, text="Batal",
            bg=C["card"], fg=C["text"],
            hover_bg=C["card2"], hover_fg=C["text"],
            font=FONT_BTN, relief="flat", padx=14, pady=7,
            cursor="hand2", command=modal.destroy
        ).pack(side="right")

        self._setup_style()

    # ── DELETE ────────────────────────────────────────────────────────────────
    def _delete_music(self, idx):
        m = self.data[idx]
        if not messagebox.askyesno(
            "Hapus Lagu",
            f"Hapus '{m.get('name','')}' dari list?\n\n"
            f"(File .mp3 di repo TIDAK dihapus, hanya entry di JSON)",
            parent=self
        ):
            return

        self.data.pop(idx)
        save_data(self.data)
        self._set_status(f"🗑 '{m.get('name','')}' dihapus dari list.", C["warning"])
        self._refresh()

    # ── APPLY CHANGES (global push) ────────────────────────────────────────────
    def _apply_changes(self):
        modal = self._make_modal("⬆ Apply Changes — Push ke GitHub", width=540, height=340)
        body  = tk.Frame(modal, bg=C["surface"])
        body.pack(fill="both", expand=True, padx=28)

        tk.Label(
            body,
            text=f"Push list_music.json ke GitHub.\n"
                 f"Total lagu: {len(self.data)}",
            bg=C["surface"], fg=C["subtext"], font=FONT_BODY, justify="center"
        ).pack(pady=(16,4))

        tk.Label(body, text="Commit message:", bg=C["surface"], fg=C["subtext"],
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(12,2))
        e_msg = RedEntry(body, placeholder="Update list_music.json", width=48)
        e_msg.pack(fill="x", ipady=6)

        prog_bar = ttk.Progressbar(body, length=480, mode="determinate",
                                   style="red.Horizontal.TProgressbar")
        prog_bar.pack(fill="x", pady=(14,0))
        prog_log = tk.Label(body, text="Siap untuk push...", bg=C["surface"],
                            fg=C["subtext"], font=FONT_SMALL, wraplength=480, justify="left")
        prog_log.pack(fill="x", pady=4)

        btn_frame = tk.Frame(modal, bg=C["surface"])
        btn_frame.pack(side="bottom", fill="x", padx=28, pady=14)

        def do_push():
            msg = e_msg.get_real().strip() or "Update list_music.json"
            push_btn.config(state="disabled", text="Pushing...")

            def log_cb(pct, txt):
                def _upd():
                    if pct >= 0:
                        prog_bar["value"] = pct
                    prog_log.config(
                        text=txt,
                        fg=C["success"] if pct == 100 else (C["danger"] if pct < 0 else C["subtext"])
                    )
                self.after(0, _upd)

            def task():
                save_data(self.data)
                ok, err = git_push_with_progress(msg, log_cb=log_cb)
                def finish():
                    push_btn.config(state="normal", text="⬆ Push")
                    if ok:
                        self._set_status("✅ Push berhasil!", C["success"])
                        self.after(2000, modal.destroy)
                    else:
                        messagebox.showerror("Git Error", f"Push gagal:\n{err}", parent=modal)
                self.after(0, finish)

            threading.Thread(target=task, daemon=True).start()

        push_btn = HoverButton(
            btn_frame, text="⬆  Push",
            bg=C["glow"], fg=C["white"],
            hover_bg=C["accent2"], hover_fg=C["white"],
            font=FONT_BTN, relief="flat", padx=18, pady=7,
            cursor="hand2", command=do_push
        )
        push_btn.pack(side="right", padx=(8,0))

        HoverButton(
            btn_frame, text="Tutup",
            bg=C["card"], fg=C["text"],
            hover_bg=C["card2"], hover_fg=C["text"],
            font=FONT_BTN, relief="flat", padx=14, pady=7,
            cursor="hand2", command=modal.destroy
        ).pack(side="right")

        self._setup_style()

    # ── STYLE SETUP ───────────────────────────────────────────────────────────
    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "red.Horizontal.TProgressbar",
            troughcolor=C["card"],
            background=C["accent"],
            bordercolor=C["border"],
            lightcolor=C["accent"],
            darkcolor=C["glow"],
        )


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        from tkinterdnd2 import TkinterDnD
        class App(TkinterDnD.Tk, MusicManager):
            def __init__(self):
                TkinterDnD.Tk.__init__(self)
                MusicManager.__init__(self)
        app = App()
    except ImportError:
        app = MusicManager()

    app.mainloop()