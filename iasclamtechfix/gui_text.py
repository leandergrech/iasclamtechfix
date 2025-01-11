import os
import tkinter as tk
from tkinter import filedialog, messagebox
import json

from iasclamtechfix.replace_logo import replace_ias_logo_and_text

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


def add_text_replacement(target_text_entry, new_text_entry, font_size_entry, white_space_entry, bold_var, italic_var, replacement_listbox):
    target_text = target_text_entry.get().strip()
    new_text = new_text_entry.get().strip()
    font_size = font_size_entry.get().strip()
    white_space = white_space_entry.get().strip()
    bold = bold_var.get()
    italic = italic_var.get()

    if not target_text or not new_text or not font_size.isdigit():
        messagebox.showerror("Error", "Please provide valid target text, new text, and font size.")
        return

    replacement_entry = {
        "target": target_text,
        "new": new_text,
        "size": int(font_size),
        "wspace": float(white_space),
        "bold": bold,
        "italic": italic,
    }

    # Check if an item is selected for editing
    selected_index = replacement_listbox.curselection()
    if selected_index:
        # Update the existing entry
        replacement_listbox.replacements[selected_index[0]] = replacement_entry
        replacement_listbox.delete(selected_index)
        replacement_listbox.insert(
            selected_index,
            f"{target_text} -> {new_text} (Font: {font_size}, Wspace: {white_space}, Bold: {bold}, Italic: {italic})"
        )
    else:
        # Add as a new entry
        replacement_listbox.replacements.append(replacement_entry)
        replacement_listbox.insert(
            tk.END,
            f"{target_text} -> {new_text} (Font: {font_size}, Wspace: {white_space}, Bold: {bold}, Italic: {italic})"
        )

    # Clear the input fields
    target_text_entry.delete(0, tk.END)
    new_text_entry.delete(0, tk.END)
    font_size_entry.delete(0, tk.END)
    # white_space_entry.delete(0, tk.END)

    bold_var.set(False)
    italic_var.set(False)


def remove_text_replacement(replacement_listbox):
    """
    Removes the selected text replacement rule from the listbox and replacements list.
    """
    # Get the selected item index
    selected_index = replacement_listbox.curselection()
    if not selected_index:
        messagebox.showerror("Error", "Please select a replacement rule to remove.")
        return

    # Remove the selected item from the listbox and the replacements list
    replacement_listbox.delete(selected_index)
    del replacement_listbox.replacements[selected_index[0]]
    messagebox.showinfo("Info", "Replacement rule removed successfully!")


def edit_text_replacement(replacement_listbox, target_text_entry, new_text_entry, font_size_entry, white_space_entry, bold_var, italic_var):
    """
    Load the selected replacement rule into the input fields for editing.
    """
    # Get the selected item index
    selected_index = replacement_listbox.curselection()
    if not selected_index:
        messagebox.showerror("Error", "Please select a replacement rule to edit.")
        return

    # Get the replacement rule
    selected_rule = replacement_listbox.replacements[selected_index[0]]

    # Populate the input fields
    target_text_entry.delete(0, tk.END)
    target_text_entry.insert(0, selected_rule["target"])

    new_text_entry.delete(0, tk.END)
    new_text_entry.insert(0, selected_rule["new"])

    font_size_entry.delete(0, tk.END)
    font_size_entry.insert(0, selected_rule["size"])

    white_space_entry.delete(0, tk.END)
    white_space_entry.insert(0, selected_rule["wspace"])

    bold_var.set(selected_rule["bold"])
    italic_var.set(selected_rule["italic"])


def load_replacement_rules(replacement_listbox, replacements):
    """
    Load saved replacement rules into the listbox.
    """
    for rule in replacements:
        # Add each rule to the listbox
        replacement_listbox.insert(
            tk.END,
            f"{rule['target']} -> {rule['new']} (Font: {rule['size']}, Wspace: {rule['wspace']}, Bold: {rule['bold']}, Italic: {rule['italic']})"
        )


def start_conversion(input_dir, logo_path, output_dir, text_replacements):
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
                print(text_replacements)
                replace_ias_logo_and_text(input_pdf, output_dir, logo_path, text_replacements)
        messagebox.showinfo("Success", "Conversion completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        raise e

    # Save the settings after a successful conversion
    save_settings({
        "input_dir": input_dir,
        "logo_path": logo_path,
        "output_dir": output_dir,
        "text_replacements": text_replacements,
    })


# Create the Tkinter GUI
root = tk.Tk()
root.title("PDF Logo and Text Replacer")

# Load previous settings
settings = load_settings()
input_dir = settings.get("input_dir", "")
logo_path = settings.get("logo_path", "")
output_dir = settings.get("output_dir", "")
text_replacements = settings.get("text_replacements", [])

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

# Text Replacement Section
tk.Label(root, text="Text Replacement Rules").grid(row=3, column=0, columnspan=3, pady=10)

tk.Label(root, text="Target Text:").grid(row=4, column=0, padx=10, sticky="w")
target_text_entry = tk.Entry(root, width=20)
target_text_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="New Text:").grid(row=5, column=0, padx=10, sticky="w")
new_text_entry = tk.Entry(root, width=20)
new_text_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="Font Size:").grid(row=6, column=0, padx=10, sticky="w")
font_size_entry = tk.Entry(root, width=10)
font_size_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")

tk.Label(root, text="White Space:").grid(row=7, column=0, padx=10, sticky="w")
white_space_entry = tk.Entry(root, width=10)
white_space_entry.insert(0, "1.2")
white_space_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")

bold_var = tk.BooleanVar()
italic_var = tk.BooleanVar()
tk.Checkbutton(root, text="Bold", variable=bold_var).grid(row=8, column=0, sticky="w", padx=10)
tk.Checkbutton(root, text="Italic", variable=italic_var).grid(row=8, column=1, sticky="w", padx=10)

replacement_listbox = tk.Listbox(root, width=80)
replacement_listbox.grid(row=9, column=0, columnspan=3, padx=10, pady=5)
replacement_listbox.replacements = text_replacements

# Load saved replacement rules
load_replacement_rules(replacement_listbox, text_replacements)

replacement_listbox.bind(
    "<Double-Button-1>",
    lambda event: edit_text_replacement(
        replacement_listbox,
        target_text_entry,
        new_text_entry,
        font_size_entry,
        white_space_entry,
        bold_var,
        italic_var
    )
)

tk.Button(
    root,
    text="Add Replacement",
    command=lambda: add_text_replacement(
        target_text_entry, new_text_entry, font_size_entry, white_space_entry, bold_var, italic_var, replacement_listbox
    )
).grid(row=10, column=0, columnspan=1, pady=7)

tk.Button(
    root,
    text="Remove Replacement",
    command=lambda: remove_text_replacement(replacement_listbox)
).grid(row=10, column=1, columnspan=1, pady=7)

tk.Button(root, text="Convert", command=lambda: start_conversion(input_dir_entry.get(), logo_entry.get(), output_dir_entry.get(), text_replacements=replacement_listbox.replacements)).grid(row=10, column=2, columnspan=1, pady=7)

root.mainloop()
