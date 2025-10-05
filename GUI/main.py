import tkinter as tk
from gui import setup_gui


def main():
    root = tk.Tk()
    root.title("Song Finder")
    root.geometry("850x800")

    setup_gui(root)

    root.mainloop()


if __name__ == "__main__":
    main()