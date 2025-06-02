"""
Main window GUI for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

from gui.employee_tab import EmployeeTab
from gui.time_tracking_tab import TimeTrackingTab
from gui.leave_management_tab import LeaveManagementTab
from gui.documents_tab import DocumentsTab
from gui.notifications_tab import NotificationsTab
from storage.database import Database
from utils.notification_checker import NotificationChecker

class MainWindow:
    """Main application window"""

    def __init__(self, root: tk.Tk, database: Database):
        self.root = root
        self.db = database

        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)

        # Create header
        self.create_header()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs
        self.create_tabs()

        # Create status bar
        self.create_status_bar()

        # Start notification checker
        self.notification_checker = NotificationChecker(self.db, self.update_notifications)
        self.notification_checker.start()

    def create_header(self):
        """Create application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', padx=10, pady=5)

        # Title
        title_label = ttk.Label(
            header_frame,
            text="Employee Management System",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side='left')

        # Date and time
        self.datetime_label = ttk.Label(
            header_frame,
            text=datetime.now().strftime('%Y-%m-%d %H:%M'),
            font=('Arial', 10)
        )
        self.datetime_label.pack(side='right')

        # Update datetime every minute
        self.update_datetime()

    def create_tabs(self):
        """Create all application tabs"""
        # Employee management tab
        self.employee_tab = EmployeeTab(self.notebook, self.db)
        self.notebook.add(self.employee_tab.frame, text="Employees")

        # Time tracking tab
        self.time_tracking_tab = TimeTrackingTab(self.notebook, self.db)
        self.notebook.add(self.time_tracking_tab.frame, text="Time Tracking")

        # Leave management tab
        self.leave_management_tab = LeaveManagementTab(self.notebook, self.db)
        self.notebook.add(self.leave_management_tab.frame, text="Leave Management")

        # Documents tab
        self.documents_tab = DocumentsTab(self.notebook, self.db)
        self.notebook.add(self.documents_tab.frame, text="Documents")

        # Notifications tab
        self.notifications_tab = NotificationsTab(self.notebook, self.db)
        self.notebook.add(self.notifications_tab.frame, text="Notifications")

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill='x', side='bottom')

        # Status message
        self.status_message = ttk.Label(
            self.status_bar,
            text="Ready",
            relief='sunken',
            anchor='w'
        )
        self.status_message.pack(side='left', fill='x', expand=True, padx=2)

        # Notifications indicator
        self.notification_indicator = ttk.Label(
            self.status_bar,
            text="No new notifications",
            relief='sunken',
            anchor='e'
        )
        self.notification_indicator.pack(side='right', padx=2)

    def update_datetime(self):
        """Update datetime display"""
        self.datetime_label.config(text=datetime.now().strftime('%Y-%m-%d %H:%M'))
        self.root.after(60000, self.update_datetime)  # Update every minute

    def update_notifications(self, count: int):
        """Update notifications indicator"""
        if count > 0:
            self.notification_indicator.config(
                text="No new notifications",
                foreground='black'
            )

    def on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.tab('current')['text']
        self.status_message.config(text=f"Viewing {selected_tab}")

        # Refresh data in the selected tab
        if selected_tab == "Employees":
            self.employee_tab.refresh_employee_list()
        elif selected_tab == "Time Tracking":
            self.time_tracking_tab.refresh_data()
        elif selected_tab == "Leave Management":
            self.leave_management_tab.refresh_data()
        elif selected_tab == "Notifications":
            self.notifications_tab.refresh_notifications()
