import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from transparent_background import Remover
import sys

# ---------------- PATH FIX ----------------

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# ---------------- DEFAULT CONFIG ----------------

default_config = {
    "language": "EN",
    "theme": "dark"
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4)

try:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
except:
    config = default_config

# ---------------- UI ----------------

ctk.set_appearance_mode(config["theme"])
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.geometry("620x540")
root.title("Background Remove Tool")

input_path = ""
output_folder = ""

remover = Remover()

# ---------------- LANGUAGE ----------------

def apply_language():

    if config["language"] == "VI":

        title.configure(text="Công cụ xóa nền")
        btn_img.configure(text="Chọn ảnh")
        btn_out.configure(text="Chọn thư mục xuất")
        start_btn.configure(text="Bắt đầu")

        label_mb.configure(text="Dung lượng mong muốn (MB)")
        label_up.configure(text="Độ phân giải")

    else:

        title.configure(text="Background Remove Tool")
        btn_img.configure(text="Select Image")
        btn_out.configure(text="Select Output Folder")
        start_btn.configure(text="Start")

        label_mb.configure(text="Target size (MB)")
        label_up.configure(text="Resolution")

# ---------------- HEADER ----------------

header = ctk.CTkFrame(root, corner_radius=0)
header.pack(fill="x")

title = ctk.CTkLabel(
    header,
    text="Background Remove Tool",
    font=ctk.CTkFont(size=18, weight="bold")
)
title.pack(side="left", padx=20, pady=12)

# ---------------- SETTINGS ----------------

def open_settings():

    settings = ctk.CTkToplevel(root)
    settings.geometry("300x250")
    settings.title("Settings")

    settings.transient(root)
    settings.focus()
    settings.grab_set()

    ctk.CTkLabel(settings, text="Language").pack(pady=6)

    lang_box = ctk.CTkComboBox(settings, values=["EN", "VI"])
    lang_box.set(config["language"])
    lang_box.pack()

    ctk.CTkLabel(settings, text="Theme").pack(pady=6)

    theme_box = ctk.CTkComboBox(settings, values=["dark", "light"])
    theme_box.set(config["theme"])
    theme_box.pack()

    def save():

        config["language"] = lang_box.get()
        config["theme"] = theme_box.get()

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        ctk.set_appearance_mode(config["theme"])
        apply_language()

        settings.destroy()

    ctk.CTkButton(settings, text="Save", command=save).pack(pady=20)

settings_btn = ctk.CTkButton(header, text="⚙", width=40, command=open_settings)
settings_btn.pack(side="right", padx=10)

# ---------------- MAIN ----------------

main = ctk.CTkFrame(root)
main.pack(padx=20, pady=20, fill="both", expand=True)

preview = ctk.CTkLabel(main, text="No Image", width=200, height=200)
preview.pack(pady=10)

file_label = ctk.CTkLabel(main, text="No image selected")
file_label.pack()

def select_image():

    global input_path

    input_path = filedialog.askopenfilename(
        filetypes=[("Images", "*.png *.jpg *.jpeg")]
    )

    if input_path:

        name = os.path.basename(input_path)
        file_label.configure(text="📄 " + name)

        img = Image.open(input_path)
        img.thumbnail((200, 200))

        preview_img = ctk.CTkImage(light_image=img, size=(200, 200))
        preview.configure(image=preview_img, text="")
        preview.image = preview_img

btn_img = ctk.CTkButton(main, text="Select Image", command=select_image)
btn_img.pack(pady=10)

folder_label = ctk.CTkLabel(main, text="No folder selected")
folder_label.pack()

def select_output():

    global output_folder

    output_folder = filedialog.askdirectory()

    if output_folder:

        name = os.path.basename(output_folder)

        if name == "":
            name = output_folder

        folder_label.configure(text="📂 " + name)

btn_out = ctk.CTkButton(main, text="Select Output Folder", command=select_output)
btn_out.pack(pady=10)

# ---------------- PROGRESS ----------------

progress = ctk.CTkProgressBar(main, width=350)
progress.set(0)
progress.pack(pady=15)

status = ctk.CTkLabel(root, text="Ready")
status.pack(side="bottom", pady=5)

# ---------------- PROCESS ----------------

def process():

    try:

        status.configure(text="Removing background...")
        progress.set(0.4)

        img = Image.open(input_path)

        result = remover.process(img)

        name = os.path.basename(input_path).split(".")[0]
        out = os.path.join(output_folder, name + "_removed.png")

        result.save(out)

        progress.set(1)

        status.configure(text="Done")
        messagebox.showinfo("Done", "Image processed!")

    except Exception as e:

        messagebox.showerror("Error", str(e))
        status.configure(text="Error")

# ---------------- START ----------------

def start():

    if not input_path:
        messagebox.showwarning("Warning", "Please select an image first")
        return

    if not output_folder:
        messagebox.showwarning("Warning", "Please select output folder")
        return

    threading.Thread(target=process).start()

start_btn = ctk.CTkButton(main, text="Start", command=start)
start_btn.pack(pady=12)

apply_language()

root.mainloop()