# test.py
import tkinter as tk
from tkcalendar import DateEntry
import sqlite3

root = tk.Tk()
root.title("Test")
DateEntry(root).pack()
root.mainloop()