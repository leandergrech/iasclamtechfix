import os
import tkinter as tk
from tkinter import filedialog, messagebox
import json

from iasclamtechfix.replace_logo import replace_ias_logo

# File to save and load settings
SETTINGS_FILE = "settings.json"


def save_settings(settings):
    """Save settings to a JSON file."""
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)


def load_settings():
    """Load settings from a JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {}


def browse_directory(entry_field):
    directory = filedialog.askdirectory()
    if directory:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, directory)


def browse_file(entry_field, file_types):
    file_path = filedialog.askopenfilename(filetypes=file_types)
    if file_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, file_path)


def start_conversion(input_dir, logo_path, output_dir):
    input_dir = input_dir.strip()
    logo_path = logo_path.strip()
    output_dir = output_dir.strip()

    if not os.path.isdir(input_dir):
        messagebox.showerror("Error", "Invalid input directory.")
        return
    if not os.path.isfile(logo_path):
        messagebox.showerror("Error", "Invalid logo file.")
        return
    os.makedirs(output_dir, exist_ok=True)

    try:
        for file in os.listdir(input_dir):
            if file.endswith(".pdf"):
                input_pdf = os.path.join(input_dir, file)
                print(input_pdf)
                replace_ias_logo(input_pdf, output_dir, new_logo_path=logo_path)
        messagebox.showinfo("Success", "Conversion completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

    # Save the settings after a successful conversion
    save_settings({
        "input_dir": input_dir,
        "logo_path": logo_path,
        "output_dir": output_dir
    })

# Create the Tkinter GUI
root = tk.Tk()
root.title("PDF Logo Replacer")

# Load previous settings
settings = load_settings()
input_dir = settings.get("input_dir", "")
logo_path = settings.get("logo_path", "")
output_dir = settings.get("output_dir", "")

tk.Label(root, text="Input Directory (PDFs):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
input_dir_entry = tk.Entry(root, width=50)
input_dir_entry.insert(0, input_dir)
input_dir_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_directory(input_dir_entry)).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="New Logo (Image File):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
logo_entry = tk.Entry(root, width=50)
logo_entry.insert(0, logo_path)
logo_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(logo_entry, [("Image Files", "*.jpg *.jpeg *.png")])).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Output Directory:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.insert(0, output_dir)
output_dir_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_directory(output_dir_entry)).grid(row=2, column=2, padx=10, pady=5)

tk.Button(root, text="Convert", command=lambda: start_conversion(input_dir_entry.get(), logo_entry.get(), output_dir_entry.get())).grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()
