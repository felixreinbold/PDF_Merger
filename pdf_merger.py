import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from pypdf import PdfReader, PdfWriter
import os
import sys
from typing import Tuple, Optional, Any

# Constants
COLOR_BG = "#F5F5F7"
COLOR_CARD = "#FFFFFF"
COLOR_BORDER = "#D2D2D7"
COLOR_HOVER = "#F9F9FB"
COLOR_DRAG_HOVER = "#E3F2FD"
COLOR_SUCCESS = "#30D158"
COLOR_SUCCESS_BG = "#E8F8ED"
COLOR_ERROR = "#FF453A"
COLOR_TEXT = "#1D1D1F"
COLOR_TEXT_SECONDARY = "#86868B"
COLOR_ACCENT = "#007AFF"
COLOR_BUTTON_HOVER = "#0051D5"

FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_SUBTITLE = ("Segoe UI", 15)
FONT_BODY = ("Segoe UI", 13)
FONT_BUTTON = ("Segoe UI", 15, "bold")


def create_rounded_rectangle(canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float, radius: int = 20, **kwargs) -> int:
    """Creates a rounded rectangle on a canvas."""
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class PDFMergerApp:
    """
    Main application class for the PDF Merger tool.
    Handles the UI and the logic for merging PDF files.
    """

    def __init__(self, root: TkinterDnD.Tk):
        self.root = root
        self.setup_window()
        
        # State variables
        self.pdf1_path = tk.StringVar()
        self.pdf2_path = tk.StringVar()
        self.status_timer: Optional[str] = None
        
        self.setup_ui()

    def setup_window(self):
        """Configures the main window properties."""
        # Taskbar Icon Fix
        try:
            import ctypes
            myappid = 'felixreinbold.pdf_merger.1.0' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Could not set AppUserModelID: {e}")

        # Icon Fix for PyInstaller
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        icon_path = os.path.join(base_path, "app.ico")

        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print("Icon could not be loaded:", e)

        self.root.title("PDF Merger")
        self.root.geometry("700x750")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

    def setup_ui(self):
        """Initializes all UI components."""
        # Header
        header_frame = tk.Frame(self.root, bg=COLOR_BG)
        header_frame.pack(pady=(40, 10))
        
        tk.Label(header_frame, text="PDF Merger", bg=COLOR_BG, fg=COLOR_TEXT, font=FONT_TITLE).pack()
        tk.Label(header_frame, text="Fügen Sie zwei PDF-Dateien zu einer zusammen", bg=COLOR_BG, fg=COLOR_TEXT_SECONDARY, font=FONT_SUBTITLE).pack(pady=(5, 0))

        # Drop Zones
        self.pdf1_widgets = self.create_drop_box(self.root, "PDF 1", "Ziehen Sie die PDF hier rein oder klicken Sie", self.pdf1_path)
        self.pdf2_widgets = self.create_drop_box(self.root, "PDF 2", "Ziehen Sie die PDF hier rein oder klicken Sie", self.pdf2_path)

        # Buttons
        button_frame = tk.Frame(self.root, bg=COLOR_BG)
        button_frame.pack(pady=(110, 30))

        btn_container = tk.Frame(button_frame, bg=COLOR_BG)
        btn_container.pack()

        # Merge Button
        self.merge_cv = tk.Canvas(btn_container, bg=COLOR_BG, width=280, height=50, highlightthickness=0)
        self.merge_cv.grid(row=0, column=0, padx=(0, 10))
        self.merge_rect = create_rounded_rectangle(self.merge_cv, 0, 0, 280, 50, radius=10, fill=COLOR_ACCENT, outline="")
        self.merge_btn = tk.Label(self.merge_cv, text="PDFs zusammenführen", bg=COLOR_ACCENT, fg="white", font=FONT_BUTTON, cursor="hand2")
        self.merge_cv.create_window(140, 25, window=self.merge_btn)

        # Reset Button
        self.reset_cv = tk.Canvas(btn_container, bg=COLOR_BG, width=50, height=50, highlightthickness=0)
        self.reset_cv.grid(row=0, column=1)
        self.reset_rect = create_rounded_rectangle(self.reset_cv, 0, 0, 50, 50, radius=10, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
        self.reset_btn = tk.Label(self.reset_cv, text="↻", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 20), cursor="hand2")
        self.reset_cv.create_window(25, 25, window=self.reset_btn)

        # Bindings
        self.merge_btn.bind("<Button-1>", lambda e: self.merge_pdfs())
        self.merge_cv.bind("<Button-1>", lambda e: self.merge_pdfs())
        self.merge_btn.bind("<Enter>", lambda e: (self.merge_cv.itemconfig(self.merge_rect, fill=COLOR_BUTTON_HOVER), self.merge_btn.config(bg=COLOR_BUTTON_HOVER)))
        self.merge_btn.bind("<Leave>", lambda e: (self.merge_cv.itemconfig(self.merge_rect, fill=COLOR_ACCENT), self.merge_btn.config(bg=COLOR_ACCENT)))

        self.reset_btn.bind("<Button-1>", lambda e: self.reset_files())
        self.reset_cv.bind("<Button-1>", lambda e: self.reset_files())
        self.reset_btn.bind("<Enter>", lambda e: (self.reset_cv.itemconfig(self.reset_rect, fill=COLOR_HOVER), self.reset_btn.config(bg=COLOR_HOVER)))
        self.reset_btn.bind("<Leave>", lambda e: (self.reset_cv.itemconfig(self.reset_rect, fill=COLOR_CARD), self.reset_btn.config(bg=COLOR_CARD)))

        # Status Bar
        self.status_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.status_canvas = tk.Canvas(self.status_frame, bg=COLOR_BG, height=55, width=625, highlightthickness=0)
        self.status_canvas.pack()
        self.status_label = tk.Label(self.status_canvas, text="", font=("Segoe UI", 12, "bold"), bg=COLOR_BG)

    def hide_status(self):
        """Hides the status message."""
        self.status_frame.place_forget() 

    def show_status(self, msg: str, error: bool = False):
        """
        Displays a status message to the user.
        
        Args:
            msg: The message to display.
            error: Whether the message is an error (changes color).
        """
        if self.status_timer is not None:
            self.root.after_cancel(self.status_timer)

        self.status_canvas.delete("all")

        if error:
            bg_color = "#FFECEC"
            border_color = COLOR_ERROR
            text_color = COLOR_ERROR
            prefix = "⚠️ "
        else:
            bg_color = COLOR_SUCCESS_BG
            border_color = COLOR_SUCCESS
            text_color = COLOR_SUCCESS
            prefix = "✓ "

        create_rounded_rectangle(
            self.status_canvas, 2, 2, 618, 48, radius=12,
            fill=bg_color, outline=border_color, width=1
        )

        self.status_label.config(
            text=prefix + msg,
            fg=text_color,
            bg=bg_color
        )

        self.status_canvas.create_window(310, 25, window=self.status_label)
        self.status_frame.place(relx=0.5, y=550, anchor="n")
        self.status_frame.lift()
        
        self.status_timer = self.root.after(4000, self.hide_status)

    def set_file(self, var: tk.StringVar, path: str):
        """Sets the file path variable and updates the UI."""
        path = path.strip("{}")
        if path.lower().endswith(".pdf") and os.path.isfile(path):
            var.set(path)
            self.update_box_state(var)
        else:
            self.show_status("Ungültige Datei (nur PDF erlaubt!)", error=True)

    def choose_file(self, var: tk.StringVar):
        """Opens a file dialog to choose a PDF."""
        path = filedialog.askopenfilename(filetypes=[("PDF Dateien", "*.pdf")])
        if path:
            var.set(path)
            self.update_box_state(var)

    def update_box_state(self, var: tk.StringVar):
        """Updates the visual state of the drop box based on whether a file is selected."""
        if var == self.pdf1_path:
            canvas, rect, box, icon, label, filename_label = self.pdf1_widgets
        else:
            canvas, rect, box, icon, label, filename_label = self.pdf2_widgets
        
        if os.path.isfile(var.get()):
            canvas.itemconfig(rect, fill=COLOR_SUCCESS_BG, outline=COLOR_SUCCESS, width=2)
            box.config(bg=COLOR_SUCCESS_BG)
            icon.config(text="✓", fg=COLOR_SUCCESS, font=("Segoe UI", 24), bg=COLOR_SUCCESS_BG)
            label.config(fg=COLOR_SUCCESS, bg=COLOR_SUCCESS_BG)
            filename = os.path.basename(var.get())
            filename_label.config(
                text=filename[:35] + "..." if len(filename) > 35 else filename,
                bg=COLOR_SUCCESS_BG
            )
            filename_label.pack(pady=(3, 0))
        else:
            canvas.itemconfig(rect, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
            box.config(bg=COLOR_CARD)
            icon.config(text="📄", fg=COLOR_TEXT_SECONDARY, font=("Segoe UI", 32), bg=COLOR_CARD)
            label.config(fg=COLOR_TEXT_SECONDARY, bg=COLOR_CARD)
            filename_label.pack_forget()

    def reset_files(self):
        """Resets both file selections."""
        self.pdf1_path.set("")
        self.pdf2_path.set("")
        self.update_box_state(self.pdf1_path)
        self.update_box_state(self.pdf2_path)
        self.hide_status()

    def merge_pdfs(self):
        """Merges the two selected PDFs."""
        file1 = self.pdf1_path.get()
        file2 = self.pdf2_path.get()

        if not os.path.isfile(file1) or not os.path.isfile(file2):
            self.show_status("Bitte beide PDFs auswählen!", error=True)
            return

        self.merge_btn.config(text="Wird zusammengeführt...")
        self.root.update()

        try:
            writer = PdfWriter()

            for p in PdfReader(file1).pages:
                writer.add_page(p)

            for p in PdfReader(file2).pages:
                writer.add_page(p)

            out_name = os.path.basename(file1).replace(".pdf", "_merged.pdf")
            
            output = filedialog.asksaveasfilename(
                initialfile=out_name,
                defaultextension=".pdf",
                filetypes=[("PDF Datei", "*.pdf")]
            )

            if not output:
                self.merge_btn.config(text="PDFs zusammenführen")
                return

            with open(output, "wb") as f:
                writer.write(f)

            self.merge_btn.config(text="PDFs zusammenführen")
            
            # Force UI Refresh
            self.root.update_idletasks()
            self.show_status("PDF erfolgreich gespeichert!")

        except Exception as e:
            self.merge_btn.config(text="PDFs zusammenführen")
            print(f"Fehler: {e}")
            self.show_status(f"Fehler: {str(e)[:40]}", error=True)

    def create_drop_box(self, parent, title_text: str, subtitle_text: str, var: tk.StringVar) -> Tuple[tk.Canvas, int, tk.Frame, tk.Label, tk.Label, tk.Label]:
        """Creates a drag-and-drop box for file selection."""
        container = tk.Frame(parent, bg=COLOR_BG)
        container.pack(pady=15, padx=40, fill="x")
        
        tk.Label(
            container, text=title_text, bg=COLOR_BG, fg=COLOR_TEXT,
            font=FONT_BODY, anchor="w"
        ).pack(fill="x", pady=(0, 8))
        
        canvas = tk.Canvas(
            container, bg=COLOR_BG, height=140,
            highlightthickness=0, cursor="hand2"
        )
        canvas.pack(fill="x")
        
        rect = create_rounded_rectangle(
            canvas, 2, 2, 618, 138, radius=12,
            fill=COLOR_CARD, outline=COLOR_BORDER, width=1
        )
        
        box = tk.Frame(canvas, bg=COLOR_CARD)
        canvas.create_window(310, 70, window=box)

        icon = tk.Label(box, text="📄", bg=COLOR_CARD, fg=COLOR_TEXT_SECONDARY, font=("Segoe UI", 32))
        icon.pack(pady=(8, 3))

        label = tk.Label(box, text=subtitle_text, bg=COLOR_CARD, fg=COLOR_TEXT_SECONDARY, font=FONT_BODY)
        label.pack()

        filename_label = tk.Label(box, text="", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold"))

        canvas.drop_target_register(DND_FILES)
        
        def on_drop(event):
            self.set_file(var, event.data)
        
        def on_drag_enter(event):
            canvas.itemconfig(rect, fill=COLOR_DRAG_HOVER, outline=COLOR_ACCENT, width=2)
            for w in [box, icon, label]: w.config(bg=COLOR_DRAG_HOVER)
            return event.action
        
        def on_drag_leave(event):
            self.update_box_state(var)
        
        canvas.dnd_bind("<<Drop>>", on_drop)
        canvas.dnd_bind("<<DragEnter>>", on_drag_enter)
        canvas.dnd_bind("<<DragLeave>>", on_drag_leave)

        # Click Logic
        def click_handler(e): self.choose_file(var)
        for w in [canvas, box, icon, label]: w.bind("<Button-1>", click_handler)

        # Hover Logic
        def on_enter(event):
            if not os.path.isfile(var.get()):
                canvas.itemconfig(rect, fill=COLOR_HOVER)
                for w in [box, icon, label]: w.config(bg=COLOR_HOVER)

        def on_leave(event):
            if not os.path.isfile(var.get()):
                canvas.itemconfig(rect, fill=COLOR_CARD)
                for w in [box, icon, label]: w.config(bg=COLOR_CARD)

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        return canvas, rect, box, icon, label, filename_label


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFMergerApp(root)
    root.mainloop()