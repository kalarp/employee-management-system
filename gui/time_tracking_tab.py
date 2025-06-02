"""
Time tracking tab for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from tkcalendar import DateEntry

from models import TimeEntry, WorkMode, Employee
from storage.database import Database


class TimeTrackingTab:
    """Time tracking management tab"""

    def __init__(self, parent, database: Database):
        self.parent = parent
        self.db = database
        self.selected_entry_id = None

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Create UI components
        self.create_entry_frame()
        self.create_filter_frame()
        self.create_time_entries_list()
        self.create_summary_frame()

        # Load initial data
        self.refresh_data()

    def create_entry_frame(self):
        """Create time entry frame"""
        entry_frame = ttk.LabelFrame(self.frame, text="Record Time Entry")
        entry_frame.pack(fill='x', padx=10, pady=5)

        # Employee selection
        ttk.Label(entry_frame, text="Employee:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(entry_frame, textvariable=self.employee_var, width=30)
        self.employee_combo.grid(row=0, column=1, padx=5, pady=5)

        # Date
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_date = DateEntry(entry_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.entry_date.grid(row=0, column=3, padx=5, pady=5)

        # Check In Time
        ttk.Label(entry_frame, text="Check In:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        check_in_frame = ttk.Frame(entry_frame)
        check_in_frame.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        self.check_in_hour = ttk.Spinbox(check_in_frame, from_=0, to=23, width=3, format="%02.0f")
        self.check_in_hour.set("08")
        self.check_in_hour.pack(side='left')
        ttk.Label(check_in_frame, text=":").pack(side='left')
        self.check_in_minute = ttk.Spinbox(check_in_frame, from_=0, to=59, width=3, format="%02.0f")
        self.check_in_minute.set("00")
        self.check_in_minute.pack(side='left')

        # Check Out Time
        ttk.Label(entry_frame, text="Check Out:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        check_out_frame = ttk.Frame(entry_frame)
        check_out_frame.grid(row=1, column=3, padx=5, pady=5, sticky='w')

        self.check_out_hour = ttk.Spinbox(check_out_frame, from_=0, to=23, width=3, format="%02.0f")
        self.check_out_hour.set("17")
        self.check_out_hour.pack(side='left')
        ttk.Label(check_out_frame, text=":").pack(side='left')
        self.check_out_minute = ttk.Spinbox(check_out_frame, from_=0, to=59, width=3, format="%02.0f")
        self.check_out_minute.set("00")
        self.check_out_minute.pack(side='left')

        # Work Mode
        ttk.Label(entry_frame, text="Work Mode:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.work_mode_var = tk.StringVar()
        work_mode_combo = ttk.Combobox(entry_frame, textvariable=self.work_mode_var, width=28)
        work_mode_combo['values'] = [wm.value for wm in WorkMode]
        work_mode_combo.set(WorkMode.OFFICE.value)
        work_mode_combo.grid(row=2, column=1, padx=5, pady=5)

        # Notes
        ttk.Label(entry_frame, text="Notes:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.notes_var = tk.StringVar()
        ttk.Entry(entry_frame, textvariable=self.notes_var, width=30).grid(row=2, column=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="Add Entry", command=self.add_time_entry).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Quick Check In", command=self.quick_check_in).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Quick Check Out", command=self.quick_check_out).pack(side='left', padx=5)

    def create_filter_frame(self):
        """Create filter frame"""
        filter_frame = ttk.LabelFrame(self.frame, text="Filter Time Entries")
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Employee filter
        ttk.Label(filter_frame, text="Employee:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.filter_employee_var = tk.StringVar()
        self.filter_employee_combo = ttk.Combobox(filter_frame, textvariable=self.filter_employee_var, width=25)
        self.filter_employee_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_employee_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Date range
        ttk.Label(filter_frame, text="From:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.filter_start_date = DateEntry(filter_frame, width=12, background='darkblue',
                                           foreground='white', borderwidth=2)
        self.filter_start_date.set_date(date.today() - timedelta(days=30))
        self.filter_start_date.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.filter_end_date = DateEntry(filter_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2)
        self.filter_end_date.grid(row=0, column=5, padx=5, pady=5)

        # Filter button
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_filter).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(filter_frame, text="Clear Filter", command=self.clear_filter).grid(row=0, column=7, padx=5, pady=5)

    def create_time_entries_list(self):
        """Create time entries list"""
        list_frame = ttk.LabelFrame(self.frame, text="Time Entries")
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
            'ID', 'Employee', 'Date', 'Check In', 'Check Out',
            'Hours', 'Work Mode', 'Notes'
        )

        # Format columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Employee', width=150)
        self.tree.column('Date', width=100, anchor='center')
        self.tree.column('Check In', width=80, anchor='center')
        self.tree.column('Check Out', width=80, anchor='center')
        self.tree.column('Hours', width=60, anchor='center')
        self.tree.column('Work Mode', width=100, anchor='center')
        self.tree.column('Notes', width=200)

        # Create headings
        for col in self.tree['columns']:
            self.tree.heading(col, text=col, anchor='center' if col != 'Employee' else 'w')

        self.tree.pack(fill='both', expand=True)

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_entry_select)

        # Create context menu
        self.create_context_menu()

    def create_summary_frame(self):
        """Create summary frame"""
        summary_frame = ttk.LabelFrame(self.frame, text="Summary")
        summary_frame.pack(fill='x', padx=10, pady=5)

        # Summary labels
        self.total_entries_label = ttk.Label(summary_frame, text="Total Entries: 0")
        self.total_entries_label.pack(side='left', padx=10, pady=5)

        self.total_hours_label = ttk.Label(summary_frame, text="Total Hours: 0.00")
        self.total_hours_label.pack(side='left', padx=10, pady=5)

        self.avg_hours_label = ttk.Label(summary_frame, text="Average Hours/Day: 0.00")
        self.avg_hours_label.pack(side='left', padx=10, pady=5)

        # Export button
        ttk.Button(summary_frame, text="Export to CSV", command=self.export_to_csv).pack(side='right', padx=10, pady=5)

    def create_context_menu(self):
        """Create context menu for time entries"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit Entry", command=self.edit_entry)
        self.context_menu.add_command(label="Delete Entry", command=self.delete_entry)

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def refresh_data(self):
        """Refresh all data"""
        # Refresh employee lists
        employees = self.db.get_all_employees()
        employee_names = ['All'] + [f"{emp.first_name} {emp.last_name}" for emp in employees]

        self.employee_combo['values'] = employee_names[1:]  # Exclude 'All' for entry
        self.filter_employee_combo['values'] = employee_names

        if employee_names:
            self.employee_combo.set(employee_names[1] if len(employee_names) > 1 else '')
            self.filter_employee_combo.set('All')

        # Store employee mapping
        self.employee_map = {f"{emp.first_name} {emp.last_name}": emp.id for emp in employees}

        # Refresh time entries
        self.refresh_time_entries()

    def refresh_time_entries(self):
        """Refresh time entries list"""
        # Clear existing entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter values
        filter_employee = self.filter_employee_var.get()
        start_date = self.filter_start_date.get_date()
        end_date = self.filter_end_date.get_date()

        # Get employee ID if specific employee selected
        employee_id = None
        if filter_employee and filter_employee != 'All':
            employee_id = self.employee_map.get(filter_employee)

        # Get time entries
        if employee_id:
            entries = self.db.get_time_entries(employee_id, start_date, end_date)
        else:
            # Get entries for all employees
            entries = []
            for emp_id in self.employee_map.values():
                entries.extend(self.db.get_time_entries(emp_id, start_date, end_date))

        # Sort by date descending
        entries.sort(key=lambda x: x.date, reverse=True)

        # Add entries to tree
        total_hours = 0
        unique_dates = set()

        for entry in entries:
            # Get employee name
            employee = self.db.get_employee(entry.employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            # Format times
            check_in = entry.check_in.strftime('%H:%M') if entry.check_in else ''
            check_out = entry.check_out.strftime('%H:%M') if entry.check_out else ''

            # Calculate hours
            hours = entry.hours_worked
            total_hours += hours
            unique_dates.add(entry.date)

            # Add to tree
            self.tree.insert('', 'end', values=(
                entry.id,
                employee_name,
                entry.date.strftime('%Y-%m-%d'),
                check_in,
                check_out,
                f"{hours:.2f}",
                entry.work_mode.value,
                entry.notes or ''
            ))

        # Update summary
        self.update_summary(len(entries), total_hours, len(unique_dates))

    def update_summary(self, total_entries: int, total_hours: float, unique_days: int):
        """Update summary information"""
        self.total_entries_label.config(text=f"Total Entries: {total_entries}")
        self.total_hours_label.config(text=f"Total Hours: {total_hours:.2f}")

        avg_hours = total_hours / unique_days if unique_days > 0 else 0
        self.avg_hours_label.config(text=f"Average Hours/Day: {avg_hours:.2f}")

    def add_time_entry(self):
        """Add new time entry"""
        # Validate employee selection
        if not self.employee_var.get():
            messagebox.showerror("Error", "Please select an employee")
            return

        # Get employee ID
        employee_id = self.employee_map.get(self.employee_var.get())
        if not employee_id:
            messagebox.showerror("Error", "Invalid employee selection")
            return

        try:
            # Create time entry
            entry = TimeEntry(
                employee_id=employee_id,
                date=self.entry_date.get_date(),
                work_mode=WorkMode(self.work_mode_var.get()),
                notes=self.notes_var.get()
            )

            # Set check in/out times
            check_in_h = int(self.check_in_hour.get())
            check_in_m = int(self.check_in_minute.get())
            check_out_h = int(self.check_out_hour.get())
            check_out_m = int(self.check_out_minute.get())

            entry.check_in = datetime.combine(entry.date,
                                              datetime.min.time().replace(hour=check_in_h, minute=check_in_m))
            entry.check_out = datetime.combine(entry.date,
                                               datetime.min.time().replace(hour=check_out_h, minute=check_out_m))

            # Validate times
            if entry.check_out <= entry.check_in:
                messagebox.showerror("Error", "Check out time must be after check in time")
                return

            # Save to database
            self.db.create_time_entry(entry)

            # Refresh list
            self.refresh_time_entries()

            # Clear form
            self.notes_var.set('')

            messagebox.showinfo("Success", "Time entry added successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add time entry: {str(e)}")

    def quick_check_in(self):
        """Quick check in for current time"""
        if not self.employee_var.get():
            messagebox.showerror("Error", "Please select an employee")
            return

        now = datetime.now()
        self.entry_date.set_date(now.date())
        self.check_in_hour.set(f"{now.hour:02d}")
        self.check_in_minute.set(f"{now.minute:02d}")

        messagebox.showinfo("Check In", f"Check in time set to {now.strftime('%H:%M')}")

    def quick_check_out(self):
        """Quick check out for current time"""
        now = datetime.now()
        self.check_out_hour.set(f"{now.hour:02d}")
        self.check_out_minute.set(f"{now.minute:02d}")

        messagebox.showinfo("Check Out", f"Check out time set to {now.strftime('%H:%M')}")

    def on_entry_select(self, event=None):
        """Handle entry selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_entry_id = item['values'][0]
        else:
            self.selected_entry_id = None

    def edit_entry(self):
        """Edit selected entry"""
        if not self.selected_entry_id:
            messagebox.showwarning("Warning", "Please select an entry to edit")
            return

        # TODO: Implement edit dialog
        messagebox.showinfo("Info", "Edit functionality to be implemented")

    def delete_entry(self):
        """Delete selected entry"""
        if not self.selected_entry_id:
            messagebox.showwarning("Warning", "Please select an entry to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
            # TODO: Implement delete functionality
            messagebox.showinfo("Info", "Delete functionality to be implemented")

    def on_filter_change(self, event=None):
        """Handle filter change"""
        self.refresh_time_entries()

    def apply_filter(self):
        """Apply date filter"""
        self.refresh_time_entries()

    def clear_filter(self):
        """Clear all filters"""
        self.filter_employee_combo.set('All')
        self.filter_start_date.set_date(date.today() - timedelta(days=30))
        self.filter_end_date.set_date(date.today())
        self.refresh_time_entries()

    def export_to_csv(self):
        """Export time entries to CSV"""
        from tkinter import filedialog
        import csv

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)

                    # Write header
                    writer.writerow(['Employee', 'Date', 'Check In', 'Check Out', 'Hours', 'Work Mode', 'Notes'])

                    # Write data
                    for child in self.tree.get_children():
                        values = self.tree.item(child)['values']
                        writer.writerow(values[1:])  # Exclude ID

                messagebox.showinfo("Success", f"Data exported to {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")