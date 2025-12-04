import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from pypdf import PdfReader, PdfWriter
import os
import sys


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

status_timer = None


def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
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

FONT_TITLE = ("Segoe UI", 28, "bold")
FONT_SUBTITLE = ("Segoe UI", 15)
FONT_BODY = ("Segoe UI", 13)
FONT_BUTTON = ("Segoe UI", 15, "bold")


def hide_status():
    status_frame.place_forget() 

def show_status(msg, error=False):
    global status_timer
    
  
    if status_timer is not None:
        root.after_cancel(status_timer)

    
    status_canvas.delete("all")

    
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
        status_canvas, 2, 2, 618, 48, radius=12,
        fill=bg_color, outline=border_color, width=1
    )

 
    status_label.config(
        text=prefix + msg,
        fg=text_color,
        bg=bg_color
    )

  
    status_canvas.create_window(310, 25, window=status_label)

    status_frame.place(relx=0.5, y=550, anchor="n")
    status_frame.lift()

  
    status_timer = root.after(4000, hide_status)



def set_file(var, path):
    path = path.strip("{}")
    if path.lower().endswith(".pdf") and os.path.isfile(path):
        var.set(path)
        update_box_state(var)
    else:
        show_status("Ungültige Datei (nur PDF erlaubt!)", error=True)

def choose_file(var):
    path = filedialog.askopenfilename(filetypes=[("PDF Dateien", "*.pdf")])
    if path:
        var.set(path)
        update_box_state(var)

def update_box_state(var):
    
    canvas, rect, box, icon, label, filename_label = (
        rechnung_widgets if var == rechnung_var else ln_widgets
    )
    
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

def reset_files():
    rechnung_var.set("")
    ln_var.set("")
    update_box_state(rechnung_var)
    update_box_state(ln_var)
    hide_status()


def merge_pdfs():
    file1 = rechnung_var.get()
    file2 = ln_var.get()

    if not os.path.isfile(file1) or not os.path.isfile(file2):
        show_status("Bitte beide PDFs auswählen!", error=True)
        return

    merge_btn.config(text="Wird zusammengeführt...")
    root.update()

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
            merge_btn.config(text="PDFs zusammenführen")
            return

        with open(output, "wb") as f:
            writer.write(f)

        merge_btn.config(text="PDFs zusammenführen")
        
        # UI Refresh erzwingen
        root.update_idletasks()
        show_status("PDF erfolgreich gespeichert!")

    except Exception as e:
        merge_btn.config(text="PDFs zusammenführen")
        print(f"Fehler: {e}")
        show_status("Fehler: " + str(e)[:40], error=True)



def create_drop_box(parent, title_text, subtitle_text, var):
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
        set_file(var, event.data)
    
    def on_drag_enter(event):
        canvas.itemconfig(rect, fill=COLOR_DRAG_HOVER, outline=COLOR_ACCENT, width=2)
        for w in [box, icon, label]: w.config(bg=COLOR_DRAG_HOVER)
        return event.action
    
    def on_drag_leave(event):
        update_box_state(var)
    
    canvas.dnd_bind("<<Drop>>", on_drop)
    canvas.dnd_bind("<<DragEnter>>", on_drag_enter)
    canvas.dnd_bind("<<DragLeave>>", on_drag_leave)

    # Click Logic
    def click_handler(e): choose_file(var)
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


root = TkinterDnD.Tk()
# ---- Icon-Fix für PyInstaller ----
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

icon_path = os.path.join(base_path, "app.ico")

try:
    root.iconbitmap(icon_path)
except Exception as e:
    print("Icon konnte nicht geladen werden:", e)
# -----------------------------------


root.title("PDF Merger")

root.geometry("700x750")
root.configure(bg=COLOR_BG)
root.resizable(False, False)



header_frame = tk.Frame(root, bg=COLOR_BG)
header_frame.pack(pady=(40, 10))

tk.Label(header_frame, text="PDF Merger", bg=COLOR_BG, fg=COLOR_TEXT, font=FONT_TITLE).pack()
tk.Label(header_frame, text="Fügen Sie zwei PDF-Dateien zu einer zusammen", bg=COLOR_BG, fg=COLOR_TEXT_SECONDARY, font=FONT_SUBTITLE).pack(pady=(5, 0))


rechnung_var = tk.StringVar()
ln_var = tk.StringVar()


rechnung_widgets = create_drop_box(root, "PDF 1", "Ziehen Sie die PDF hier rein oder klicken Sie", rechnung_var)
ln_widgets = create_drop_box(root, "PDF 2", "Ziehen Sie die PDF hier rein oder klicken Sie", ln_var)


button_frame = tk.Frame(root, bg=COLOR_BG)

button_frame.pack(pady=(110, 30))

btn_container = tk.Frame(button_frame, bg=COLOR_BG)
btn_container.pack()

merge_cv = tk.Canvas(btn_container, bg=COLOR_BG, width=280, height=50, highlightthickness=0)
merge_cv.grid(row=0, column=0, padx=(0, 10))
merge_rect = create_rounded_rectangle(merge_cv, 0, 0, 280, 50, radius=10, fill=COLOR_ACCENT, outline="")
merge_btn = tk.Label(merge_cv, text="PDFs zusammenführen", bg=COLOR_ACCENT, fg="white", font=FONT_BUTTON, cursor="hand2")
merge_cv.create_window(140, 25, window=merge_btn)


reset_cv = tk.Canvas(btn_container, bg=COLOR_BG, width=50, height=50, highlightthickness=0)
reset_cv.grid(row=0, column=1)
reset_rect = create_rounded_rectangle(reset_cv, 0, 0, 50, 50, radius=10, fill=COLOR_CARD, outline=COLOR_BORDER, width=1)
reset_btn = tk.Label(reset_cv, text="↻", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 20), cursor="hand2")
reset_cv.create_window(25, 25, window=reset_btn)

def on_merge_click(e): merge_pdfs()
def on_reset_click(e): reset_files()


merge_btn.bind("<Button-1>", on_merge_click)
merge_cv.bind("<Button-1>", on_merge_click)
merge_btn.bind("<Enter>", lambda e: (merge_cv.itemconfig(merge_rect, fill=COLOR_BUTTON_HOVER), merge_btn.config(bg=COLOR_BUTTON_HOVER)))
merge_btn.bind("<Leave>", lambda e: (merge_cv.itemconfig(merge_rect, fill=COLOR_ACCENT), merge_btn.config(bg=COLOR_ACCENT)))

reset_btn.bind("<Button-1>", on_reset_click)
reset_cv.bind("<Button-1>", on_reset_click)
reset_btn.bind("<Enter>", lambda e: (reset_cv.itemconfig(reset_rect, fill=COLOR_HOVER), reset_btn.config(bg=COLOR_HOVER)))
reset_btn.bind("<Leave>", lambda e: (reset_cv.itemconfig(reset_rect, fill=COLOR_CARD), reset_btn.config(bg=COLOR_CARD)))



status_frame = tk.Frame(root, bg=COLOR_BG)
status_canvas = tk.Canvas(status_frame, bg=COLOR_BG, height=55, width=625, highlightthickness=0)
status_canvas.pack()


status_label = tk.Label(status_canvas, text="", font=("Segoe UI", 12, "bold"), bg=COLOR_BG)

root.mainloop()