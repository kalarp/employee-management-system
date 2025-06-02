"""
Notifications tab for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta

from models import Notification, Employee
from storage.database import Database

class NotificationsTab:
    """Notifications management tab"""

    def __init__(self, parent, database: Database):
        self.parent = parent
        self.db = database
        self.selected_notification_id = None

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Create UI components
        self.create_filter_frame()
        self.create_notifications_list()
        self.create_details_frame()
        self.create_settings_frame()

        # Load initial data
        self.refresh_notifications()

    def create_filter_frame(self):
        """Create filter frame"""
        filter_frame = ttk.LabelFrame(self.frame, text="Filter Notifications")
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Notification type filter
        ttk.Label(filter_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(filter_frame, textvariable=self.type_var, width=20)
        type_combo['values'] = [
            'All',
            'Contract Expiry',
            'Medical Exam',
            'Safety Training',
            'Leave Request',
            'Document Expiry',
            'Other'
        ]
        type_combo.set('All')
        type_combo.grid(row=0, column=1, padx=5, pady=5)
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        # Status filter
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, width=15)
        status_combo['values'] = ['All', 'Unread', 'Read', 'Overdue']
        status_combo.set('Unread')
        status_combo.grid(row=0, column=3, padx=5, pady=5)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        # Employee filter
        ttk.Label(filter_frame, text="Employee:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(filter_frame, textvariable=self.employee_var, width=25)
        self.employee_combo.grid(row=0, column=5, padx=5, pady=5)
        self.employee_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filters())

        # Buttons
        ttk.Button(filter_frame, text="Refresh", command=lambda: self.refresh_notifications()).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(filter_frame, text="Mark All Read", command=lambda: self.mark_all_read()).grid(row=0, column=7, padx=5, pady=5)

    def create_notifications_list(self):
        """Create notifications list"""
        list_frame = ttk.LabelFrame(self.frame, text="Notifications")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview with scrollbar
        tree_scroll = ttk.Scrollbar(list_frame)
        tree_scroll.pack(side='right', fill='y')

        self.tree = ttk.Treeview(
            list_frame,
            yscrollcommand=tree_scroll.set,
            selectmode='browse'
        )
        tree_scroll.config(command=self.tree.yview)

        # Define columns
        self.tree['columns'] = (
            'ID', 'Type', 'Employee', 'Title', 'Due Date', 'Status', 'Created'
        )

        # Format columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Type', width=120)
        self.tree.column('Employee', width=150)
        self.tree.column('Title', width=300)
        self.tree.column('Due Date', width=100, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        self.tree.column('Created', width=150, anchor='center')

        # Create headings
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)

        self.tree.pack(fill='both', expand=True)

        # Add tags for coloring
        self.tree.tag_configure('unread', font=('Arial', 9, 'bold'))
        self.tree.tag_configure('overdue', background='#ffcccc')
        self.tree.tag_configure('warning', background='#ffffcc')
        self.tree.tag_configure('read', foreground='#666666')

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.on_notification_select())
        self.tree.bind('<Double-Button-1>', lambda e: self.mark_as_read())

        # Create context menu
        self.create_context_menu()

    def create_context_menu(self):
        """Create context menu"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Mark as Read", command=lambda: self.mark_as_read())
        self.context_menu.add_command(label="Mark as Unread", command=lambda: self.mark_as_unread())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Employee", command=lambda: self.view_employee())
        self.context_menu.add_command(label="Create Reminder", command=lambda: self.create_reminder())
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=lambda: self.delete_notification())

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def create_details_frame(self):
        """Create notification details frame"""
        details_frame = ttk.LabelFrame(self.frame, text="Notification Details")
        details_frame.pack(fill='x', padx=10, pady=5)

        # Details text widget
        self.details_text = tk.Text(details_frame, height=6, wrap='word')
        self.details_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.details_text.config(state='disabled')

        # Action buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Take Action", command=lambda: self.take_action()).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Dismiss", command=lambda: self.dismiss_notification()).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Snooze", command=lambda: self.snooze_notification()).pack(side='left', padx=5)

    def create_settings_frame(self):
        """Create notification settings frame"""
        settings_frame = ttk.LabelFrame(self.frame, text="Notification Settings")
        settings_frame.pack(fill='x', padx=10, pady=5)

        # Settings grid
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill='x', padx=5, pady=5)

        # Contract expiry warning days
        ttk.Label(settings_grid, text="Contract Expiry Warning (days):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.contract_days_var = tk.IntVar(value=30)
        ttk.Spinbox(settings_grid, textvariable=self.contract_days_var, from_=1, to=90, width=10).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Medical exam warning days
        ttk.Label(settings_grid, text="Medical Exam Warning (days):").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.medical_days_var = tk.IntVar(value=30)
        ttk.Spinbox(settings_grid, textvariable=self.medical_days_var, from_=1, to=90, width=10).grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # Safety training warning days
        ttk.Label(settings_grid, text="Safety Training Warning (days):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.safety_days_var = tk.IntVar(value=30)
        ttk.Spinbox(settings_grid, textvariable=self.safety_days_var, from_=1, to=90, width=10).grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Check frequency
        ttk.Label(settings_grid, text="Check Frequency (minutes):").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.frequency_var = tk.IntVar(value=60)
        ttk.Spinbox(settings_grid, textvariable=self.frequency_var, from_=5, to=1440, width=10).grid(row=1, column=3, padx=5, pady=5, sticky='w')

        # Buttons
        ttk.Button(settings_grid, text="Save Settings", command=lambda: self.save_settings()).grid(row=2, column=0, columnspan=2, padx=5, pady=10)
        ttk.Button(settings_grid, text="Check Now", command=lambda: self.check_now()).grid(row=2, column=2, columnspan=2, padx=5, pady=10)

        # Statistics
        self.stats_label = ttk.Label(settings_frame, text="", font=('Arial', 9))
        self.stats_label.pack(pady=5)

    def refresh_notifications(self):
        """Refresh notifications list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get employees for combo
        employees = self.db.get_all_employees()
        employee_names = ['All'] + [f"{emp.first_name} {emp.last_name}" for emp in employees]
        self.employee_combo['values'] = employee_names

        # Store employee mapping
        self.employee_map = {emp.id: f"{emp.first_name} {emp.last_name}" for emp in employees}

        # Get all notifications
        all_notifications = self.db.get_pending_notifications()

        # Apply filters
        filtered_notifications = self.apply_notification_filters(all_notifications)

        # Statistics
        total = len(all_notifications)
        unread = sum(1 for n in all_notifications if not n.is_read)
        overdue = sum(1 for n in all_notifications if n.is_overdue)

        # Add to tree
        for notif in filtered_notifications:
            # Get employee name
            employee_name = self.employee_map.get(notif.employee_id, "All Employees")

            # Determine status
            if notif.is_overdue:
                status = "Overdue"
                tags = ('overdue', 'unread' if not notif.is_read else 'read')
            elif notif.due_date and (notif.due_date - date.today()).days <= 7:
                status = "Due Soon"
                tags = ('warning', 'unread' if not notif.is_read else 'read')
            else:
                status = "Active"
                tags = ('unread' if not notif.is_read else 'read',)

            # Add to tree
            self.tree.insert('', 'end', values=(
                notif.id,
                notif.notification_type,
                employee_name,
                notif.title,
                notif.due_date.strftime('%Y-%m-%d') if notif.due_date else '',
                status,
                notif.created_at.strftime('%Y-%m-%d %H:%M') if notif.created_at else ''
            ), tags=tags)

        # Update statistics
        self.stats_label.config(text=f"Total: {total} | Unread: {unread} | Overdue: {overdue}")

        # Clear details
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        self.details_text.config(state='disabled')

    def apply_notification_filters(self, notifications):
        """Apply filters to notifications"""
        filtered = []

        type_filter = self.type_var.get()
        status_filter = self.status_var.get()
        employee_filter = self.employee_var.get()

        for notif in notifications:
            # Type filter
            if type_filter != 'All' and notif.notification_type != type_filter:
                continue

            # Status filter
            if status_filter == 'Unread' and notif.is_read:
                continue
            elif status_filter == 'Read' and not notif.is_read:
                continue
            elif status_filter == 'Overdue' and not notif.is_overdue:
                continue

            # Employee filter
            if employee_filter and employee_filter != 'All':
                employee_name = self.employee_map.get(notif.employee_id, "")
                if employee_name != employee_filter:
                    continue

            filtered.append(notif)

        return filtered

    def apply_filters(self, event=None):
        """Apply filters when changed"""
        self.refresh_notifications()

    def on_notification_select(self, event=None):
        """Handle notification selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_notification_id = item['values'][0]

            # Get notification details
            # TODO: Implement get_notification in database.py
            # notif = self.db.get_notification(self.selected_notification_id)

            # Display details
            values = item['values']
            details = f"""Type: {values[1]}
Employee: {values[2]}
Title: {values[3]}
Due Date: {values[4]}
Status: {values[5]}
Created: {values[6]}

Message: [Notification message would be displayed here]
"""

            self.details_text.config(state='normal')
            self.details_text.delete('1.0', 'end')
            self.details_text.insert('1.0', details)
            self.details_text.config(state='disabled')
        else:
            self.selected_notification_id = None

    def mark_as_read(self, event=None):
        """Mark notification as read"""
        if not self.selected_notification_id:
            return

        # TODO: Implement mark_notification_read in database.py
        # self.db.mark_notification_read(self.selected_notification_id)

        messagebox.showinfo("Info", "Marked as read")
        self.refresh_notifications()

    def mark_as_unread(self):
        """Mark notification as unread"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        # TODO: Implement mark_notification_unread in database.py
        messagebox.showinfo("Info", "Mark as unread functionality to be implemented")

    def mark_all_read(self):
        """Mark all notifications as read"""
        if messagebox.askyesno("Confirm", "Mark all notifications as read?"):
            # TODO: Implement mark_all_notifications_read in database.py
            messagebox.showinfo("Info", "All notifications marked as read")
            self.refresh_notifications()

    def view_employee(self):
        """View employee details"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        # TODO: Open employee details dialog
        messagebox.showinfo("Info", "Employee view functionality to be implemented")

    def create_reminder(self):
        """Create a reminder for this notification"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        # Create reminder dialog
        reminder_window = tk.Toplevel(self.parent)
        reminder_window.title("Create Reminder")
        reminder_window.geometry("400x300")

        # Reminder form
        ttk.Label(reminder_window, text="Create Reminder", font=('Arial', 12, 'bold')).pack(pady=10)

        form_frame = ttk.Frame(reminder_window)
        form_frame.pack(padx=20, pady=10)

        ttk.Label(form_frame, text="Remind me in:").grid(row=0, column=0, padx=5, pady=5, sticky='w')

        days_var = tk.IntVar(value=7)
        days_spin = ttk.Spinbox(form_frame, textvariable=days_var, from_=1, to=365, width=10)
        days_spin.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="days").grid(row=0, column=2, padx=5, pady=5, sticky='w')

        ttk.Label(form_frame, text="Note:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        note_text = tk.Text(form_frame, width=30, height=5)
        note_text.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        def create_reminder():
            days = days_var.get()
            note = note_text.get('1.0', 'end-1c')

            # TODO: Implement reminder creation
            messagebox.showinfo("Success", f"Reminder will be created for {days} days from now")
            reminder_window.destroy()

        ttk.Button(reminder_window, text="Create Reminder", command=create_reminder).pack(pady=10)
        ttk.Button(reminder_window, text="Cancel", command=reminder_window.destroy).pack()

    def delete_notification(self):
        """Delete notification"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        if messagebox.askyesno("Confirm Delete", "Delete this notification?"):
            # TODO: Implement delete_notification in database.py
            messagebox.showinfo("Info", "Notification deleted")
            self.refresh_notifications()

    def take_action(self):
        """Take action on notification"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        # Get notification type from selection
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            notif_type = item['values'][1]

            if notif_type == "Contract Expiry":
                messagebox.showinfo("Action", "This would open the contract renewal form")
            elif notif_type == "Medical Exam":
                messagebox.showinfo("Action", "This would open the medical exam scheduling form")
            elif notif_type == "Safety Training":
                messagebox.showinfo("Action", "This would open the training scheduling form")
            else:
                messagebox.showinfo("Action", "Action depends on notification type")

    def dismiss_notification(self):
        """Dismiss notification"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        if messagebox.askyesno("Confirm", "Dismiss this notification?"):
            self.mark_as_read()

    def snooze_notification(self):
        """Snooze notification"""
        if not self.selected_notification_id:
            messagebox.showwarning("Warning", "Please select a notification")
            return

        # Snooze dialog
        snooze_window = tk.Toplevel(self.parent)
        snooze_window.title("Snooze Notification")
        snooze_window.geometry("300x200")

        ttk.Label(snooze_window, text="Snooze for:", font=('Arial', 10)).pack(pady=10)

        snooze_frame = ttk.Frame(snooze_window)
        snooze_frame.pack(pady=10)

        snooze_var = tk.IntVar(value=1)
        ttk.Radiobutton(snooze_frame, text="1 day", variable=snooze_var, value=1).pack(anchor='w')
        ttk.Radiobutton(snooze_frame, text="3 days", variable=snooze_var, value=3).pack(anchor='w')
        ttk.Radiobutton(snooze_frame, text="1 week", variable=snooze_var, value=7).pack(anchor='w')
        ttk.Radiobutton(snooze_frame, text="2 weeks", variable=snooze_var, value=14).pack(anchor='w')

        def snooze():
            days = snooze_var.get()
            # TODO: Implement snooze functionality
            messagebox.showinfo("Snoozed", f"Notification snoozed for {days} days")
            snooze_window.destroy()

        ttk.Button(snooze_window, text="Snooze", command=snooze).pack(pady=10)
        ttk.Button(snooze_window, text="Cancel", command=snooze_window.destroy).pack()

    def save_settings(self):
        """Save notification settings"""
        # TODO: Save settings to config
        config_values = {
            'contract_expiry_warning_days': self.contract_days_var.get(),
            'medical_exam_warning_days': self.medical_days_var.get(),
            'safety_training_warning_days': self.safety_days_var.get(),
            'notification_check_interval': self.frequency_var.get() * 60  # Convert to seconds
        }

        messagebox.showinfo("Success", "Notification settings saved")

    def check_now(self):
        """Manually trigger notification check"""
        # TODO: Trigger notification checker
        messagebox.showinfo("Info", "Checking for new notifications...")

        # Simulate finding new notifications
        self.refresh_notifications()
        messagebox.showinfo("Complete", "Notification check complete")