#!/usr/bin/env python3
# tamanna_code_editor.py

import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

APP_TITLE = "Tamanna Code Editor"
DEFAULT_FONT = ("Consolas", 12)
BG_COLOR = "#0b1020"
FG_COLOR = "#f5f5f5"
CURSOR_COLOR = "#ffcc66"
LINE_NUM_BG = "#111827"
LINE_NUM_FG = "#6b7280"
STATUS_BG = "#111827"
STATUS_FG = "#9ca3af"
HIGHLIGHT_BG = "#1f2937"


class TamannaEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1000x650")
        self.configure(bg=BG_COLOR)

        self.file_path = None

        self._create_menu()
        self._create_widgets()
        self._bind_events()

    # ---------- UI SETUP ----------

    def _create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        run_menu = tk.Menu(menubar, tearoff=0)
        run_menu.add_command(label="Run Python File", accelerator="F5", command=self.run_code)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Run", menu=run_menu)

        self.config(menu=menubar)

    def _create_widgets(self):
        # Main container
        main_frame = tk.Frame(self, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            main_frame,
            width=5,
            padx=5,
            takefocus=0,
            border=0,
            background=LINE_NUM_BG,
            foreground=LINE_NUM_FG,
            state="disabled",
            font=DEFAULT_FONT
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor
        self.text = ScrolledText(
            main_frame,
            undo=True,
            font=DEFAULT_FONT,
            background=BG_COLOR,
            foreground=FG_COLOR,
            insertbackground=CURSOR_COLOR,
            selectbackground=HIGHLIGHT_BG,
            border=0
        )
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Status bar
        self.status = tk.Label(
            self,
            text="Tamanna ready",
            anchor="w",
            bg=STATUS_BG,
            fg=STATUS_FG
        )
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _bind_events(self):
        self.text.bind("<<Modified>>", self._on_text_changed)
        self.text.bind("<KeyRelease>", self._update_cursor_position)
        self.text.bind("<ButtonRelease-1>", self._update_cursor_position)

        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<F5>", lambda e: self.run_code())

    # ---------- FILE OPS ----------

    def new_file(self):
        if self._confirm_discard_changes():
            self.text.delete("1.0", tk.END)
            self.file_path = None
            self._set_status("New file")
            self._update_title()

    def open_file(self):
        if not self._confirm_discard_changes():
            return

        path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", content)
            self.file_path = path
            self._set_status(f"Opened: {os.path.basename(path)}")
            self._update_title()
            self._reset_modified()
            self._update_line_numbers()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")

    def save_file(self):
        if self.file_path is None:
            return self.save_file_as()

        try:
            content = self.text.get("1.0", tk.END)
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self._set_status(f"Saved: {os.path.basename(self.file_path)}")
            self._reset_modified()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            content = self.text.get("1.0", tk.END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.file_path = path
            self._set_status(f"Saved As: {os.path.basename(path)}")
            self._update_title()
            self._reset_modified()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

    # ---------- RUN CODE ----------

    def run_code(self):
        # Ensure file is saved first
        if self.file_path is None:
            save_first = messagebox.askyesno(
                "Save file",
                "You must save the file before running.\nSave now?"
            )
            if not save_first:
                return
            self.save_file_as()
            if self.file_path is None:
                return

        self.save_file()  # Save latest changes

        cmd = [sys.executable, self.file_path]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            output = result.stdout
            error = result.stderr

            if error:
                self._show_run_output("Error", error)
            else:
                self._show_run_output("Output", output if output.strip() else "(No output)")
        except Exception as e:
            self._show_run_output("Error", str(e))

    def _show_run_output(self, title, content):
        win = tk.Toplevel(self)
        win.title(f"Run: {title}")
        win.geometry("700x400")
        win.configure(bg=BG_COLOR)

        text = ScrolledText(
            win,
            font=DEFAULT_FONT,
            background=BG_COLOR,
            foreground=FG_COLOR,
            insertbackground=CURSOR_COLOR,
            border=0
        )
        text.pack(fill=tk.BOTH, expand=True)
        text.insert("1.0", content)
        text.config(state="disabled")

    # ---------- HELPERS ----------

    def _confirm_discard_changes(self):
        if self.text.edit_modified():
            resp = messagebox.askyesnocancel(
                "Unsaved changes",
                "You have unsaved changes. Save before continuing?"
            )
            if resp is None:
                return False
            if resp:
                self.save_file()
        return True

    def _set_status(self, msg):
        self.status.config(text=msg)

    def _update_title(self):
        name = self.file_path if self.file_path else "Untitled"
        self.title(f"{APP_TITLE} - {os.path.basename(name)}")

    def _reset_modified(self):
        self.text.edit_modified(False)

    def _on_text_changed(self, event=None):
        if self.text.edit_modified():
            self._update_line_numbers()
            self.text.edit_modified(True)  # keep flag
        self.text.edit_modified(False)

    def _update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)

        content = self.text.get("1.0", "end-1c")
        lines = content.count("\n") + 1
        line_numbers_str = "\n".join(str(i) for i in range(1, lines + 1))

        self.line_numbers.insert("1.0", line_numbers_str)
        self.line_numbers.config(state="disabled")

    def _update_cursor_position(self, event=None):
        pos = self.text.index(tk.INSERT)
        line, col = pos.split(".")
        self._set_status(f"Ln {line}, Col {int(col) + 1}")

    # ---------- MAIN LOOP ----------


if __name__ == "__main__":
    app = TamannaEditor()
    app.mainloop()