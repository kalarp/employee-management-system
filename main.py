#!/usr/bin/env python3
"""
Employee Management System - Main Application Entry Point
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from storage.database import Database
from utils.config import Config
from utils.logger import setup_logger


class EmployeeManagementApp:
    """Main application class"""

    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("Starting Employee Management System")

        # Initialize configuration
        self.config = Config()

        # Initialize database
        self.db = Database()
        self.db.create_tables()

        # Create main window
        self.root = tk.Tk()
        self.setup_window()

        # Initialize main window
        self.main_window = MainWindow(self.root, self.db)

    def setup_window(self):
        """Configure the main window"""
        self.root.title("Employee Management System")
        self.root.geometry("1200x700")

        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        # Set minimum window size
        self.root.minsize(1000, 600)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.logger.info("Closing Employee Management System")
            self.db.close()
            self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = EmployeeManagementApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application: {str(e)}")
        raise


if __name__ == "__main__":
    main()