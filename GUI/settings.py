from Resources import config
from tkinter import messagebox
import tkinter as tk

def group_selection_menu():
    config.group_selection = False if config.group_selection else True


def selection_size_menu():
    settings_window = tk.Toplevel()
    settings_window.title("Adjust Selection Size")
    settings_window.geometry("300x150")

    selection_var = tk.IntVar(value=config.selection_size)
    entry_box = tk.Entry(settings_window, textvariable=selection_var)
    entry_box.pack(pady=5)

    def apply_selection_size():
        try:
            new_value = int(entry_box.get())
            if 1 <= new_value <= 200:  # Ensure it's within range
                config.selection_size = new_value
                messagebox.showinfo("Success", f"Selection Size set to {config.selection_size}")
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Selection Size must be between 1 and 200.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    tk.Button(settings_window, text="Apply", command=apply_selection_size).pack(pady=10)