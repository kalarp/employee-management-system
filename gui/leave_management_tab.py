"""
Leave management tab for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from tkcalendar import DateEntry

from models import LeaveRequest, LeaveType, Employee
from storage.database import Database

class LeaveManagementTab:
    """Leave management tab"""

    def __init__(self, parent, database: Database):
        self.parent = parent
        self.db = database
        self.selected_request_id = None

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Create UI components
        self.create_request_frame()
        self.create_filter_frame()
        self.create_requests_list()
        self.create_summary_frame()

        # Load initial data
        self.refresh_data()

    def create_request_frame(self):
        """Create leave request frame"""
        request_frame = ttk.LabelFrame(self.frame, text="New Leave Request")
        request_frame.pack(fill='x', padx=10, pady=5)

        # Employee selection
        ttk.Label(request_frame, text="Employee:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(request_frame, textvariable=self.employee_var, width=30)
        self.employee_combo.grid(row=0, column=1, padx=5, pady=5)
        self.employee_combo.bind('<<ComboboxSelected>>', self.on_employee_select)

        # Leave type
        ttk.Label(request_frame, text="Leave Type:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.leave_type_var = tk.StringVar()
        leave_type_combo = ttk.Combobox(request_frame, textvariable=self.leave_type_var, width=20)
        leave_type_combo['values'] = [lt.value for lt in LeaveType]
        leave_type_combo.set(LeaveType.VACATION.value)
        leave_type_combo.grid(row=0, column=3, padx=5, pady=5)

        # Date range
        ttk.Label(request_frame, text="Start Date:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.start_date = DateEntry(request_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.start_date.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.start_date.bind('<<DateEntrySelected>>', self.calculate_days)

        ttk.Label(request_frame, text="End Date:").grid(row=1, column=2, padx=5, pady=5, sticky='w')
        self.end_date = DateEntry(request_frame, width=12, background='darkblue',
                                 foreground='white', borderwidth=2)
        self.end_date.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        self.end_date.bind('<<DateEntrySelected>>', self.calculate_days)

        # Days and balance
        ttk.Label(request_frame, text="Days:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.days_label = ttk.Label(request_frame, text="0", font=('Arial', 10, 'bold'))
        self.days_label.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        ttk.Label(request_frame, text="Remaining Balance:").grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.balance_label = ttk.Label(request_frame, text="0", font=('Arial', 10, 'bold'))
        self.balance_label.grid(row=2, column=3, padx=5, pady=5, sticky='w')

        # Reason
        ttk.Label(request_frame, text="Reason:").grid(row=3, column=0, padx=5, pady=5, sticky='nw')
        self.reason_text = tk.Text(request_frame, width=70, height=3)
        self.reason_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(request_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="Submit Request", command=self.submit_request).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side='left', padx=5)

    def create_filter_frame(self):
        """Create filter frame"""
        filter_frame = ttk.LabelFrame(self.frame, text="Filter Leave Requests")
        filter_frame.pack(fill='x', padx=10, pady=5)

        # Employee filter
        ttk.Label(filter_frame, text="Employee:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.filter_employee_var = tk.StringVar()
        self.filter_employee_combo = ttk.Combobox(filter_frame, textvariable=self.filter_employee_var, width=25)
        self.filter_employee_combo.grid(row=0, column=1, padx=5, pady=5)

        # Status filter
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.filter_status_var = tk.StringVar()
        status_combo = ttk.Combobox(filter_frame, textvariable=self.filter_status_var, width=15)
        status_combo['values'] = ['All', 'Pending', 'Approved', 'Rejected']
        status_combo.set('All')
        status_combo.grid(row=0, column=3, padx=5, pady=5)

        # Date range filter
        ttk.Label(filter_frame, text="From:").grid(row=0, column=4, padx=5, pady=5, sticky='w')
        self.filter_from_date = DateEntry(filter_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2)
        self.filter_from_date.set_date(date.today() - timedelta(days=90))
        self.filter_from_date.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=6, padx=5, pady=5, sticky='w')
        self.filter_to_date = DateEntry(filter_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2)
        self.filter_to_date.grid(row=0, column=7, padx=5, pady=5)

        # Filter buttons
        ttk.Button(filter_frame, text="Apply", command=self.apply_filters).grid(row=0, column=8, padx=5, pady=5)
        ttk.Button(filter_frame, text="Clear", command=self.clear_filters).grid(row=0, column=9, padx=5, pady=5)

    def create_requests_list(self):
        """Create leave requests list"""
        list_frame = ttk.LabelFrame(self.frame, text="Leave Requests")
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
            'ID', 'Employee', 'Type', 'Start Date', 'End Date',
            'Days', 'Status', 'Reason', 'Approved By'
        )

        # Format columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Employee', width=150)
        self.tree.column('Type', width=100)
        self.tree.column('Start Date', width=100, anchor='center')
        self.tree.column('End Date', width=100, anchor='center')
        self.tree.column('Days', width=50, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        self.tree.column('Reason', width=200)
        self.tree.column('Approved By', width=100)

        # Create headings
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)

        self.tree.pack(fill='both', expand=True)

        # Add tags for coloring
        self.tree.tag_configure('pending', background='#ffffcc')
        self.tree.tag_configure('approved', background='#ccffcc')
        self.tree.tag_configure('rejected', background='#ffcccc')

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_request_select)
        self.tree.bind('<Double-Button-1>', self.on_request_double_click)

        # Create context menu
        self.create_context_menu()

    def create_context_menu(self):
        """Create context menu for requests"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self.view_request_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Approve", command=self.approve_request)
        self.context_menu.add_command(label="Reject", command=self.reject_request)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_request)

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def create_summary_frame(self):
        """Create summary frame"""
        summary_frame = ttk.LabelFrame(self.frame, text="Summary")
        summary_frame.pack(fill='x', padx=10, pady=5)

        # Summary labels
        self.pending_label = ttk.Label(summary_frame, text="Pending: 0")
        self.pending_label.pack(side='left', padx=10, pady=5)

        self.approved_label = ttk.Label(summary_frame, text="Approved: 0")
        self.approved_label.pack(side='left', padx=10, pady=5)

        self.rejected_label = ttk.Label(summary_frame, text="Rejected: 0")
        self.rejected_label.pack(side='left', padx=10, pady=5)

        # Action buttons
        ttk.Button(summary_frame, text="Approve Selected", command=self.approve_request).pack(side='right', padx=5, pady=5)
        ttk.Button(summary_frame, text="Reject Selected", command=self.reject_request).pack(side='right', padx=5, pady=5)
        ttk.Button(summary_frame, text="Export Report", command=self.export_report).pack(side='right', padx=5, pady=5)

    def refresh_data(self):
        """Refresh all data"""
        # Refresh employee lists
        employees = self.db.get_all_employees()
        employee_names = [f"{emp.first_name} {emp.last_name}" for emp in employees]

        self.employee_combo['values'] = employee_names
        self.filter_employee_combo['values'] = ['All'] + employee_names

        if employee_names:
            self.employee_combo.set(employee_names[0])
            self.filter_employee_combo.set('All')

        # Store employee mapping
        self.employee_map = {f"{emp.first_name} {emp.last_name}": emp for emp in employees}

        # Refresh leave requests
        self.refresh_requests()

        # Update employee balance
        self.on_employee_select()

    def refresh_requests(self):
        """Refresh leave requests list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filter values
        employee_filter = self.filter_employee_var.get()
        status_filter = self.filter_status_var.get()

        # Get employee ID if specific employee selected
        employee_id = None
        if employee_filter and employee_filter != 'All':
            emp = self.employee_map.get(employee_filter)
            employee_id = emp.id if emp else None

        # Get status filter
        status = None if status_filter == 'All' else status_filter

        # Get all leave requests
        requests = self.db.get_leave_requests(employee_id, status)

        # Apply date filter
        from_date = self.filter_from_date.get_date()
        to_date = self.filter_to_date.get_date()

        filtered_requests = []
        for req in requests:
            if from_date <= req.start_date <= to_date:
                filtered_requests.append(req)

        # Count by status
        pending_count = sum(1 for r in filtered_requests if r.status == 'Pending')
        approved_count = sum(1 for r in filtered_requests if r.status == 'Approved')
        rejected_count = sum(1 for r in filtered_requests if r.status == 'Rejected')

        # Add to tree
        for request in filtered_requests:
            # Get employee name
            employee = self.db.get_employee(request.employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            # Determine tag
            tag = request.status.lower()

            # Add to tree
            self.tree.insert('', 'end', values=(
                request.id,
                employee_name,
                request.leave_type.value,
                request.start_date.strftime('%Y-%m-%d'),
                request.end_date.strftime('%Y-%m-%d'),
                request.days_count,
                request.status,
                request.reason[:50] + '...' if len(request.reason) > 50 else request.reason,
                request.approved_by or ''
            ), tags=(tag,))

        # Update summary
        self.pending_label.config(text=f"Pending: {pending_count}")
        self.approved_label.config(text=f"Approved: {approved_count}")
        self.rejected_label.config(text=f"Rejected: {rejected_count}")

    def on_employee_select(self, event=None):
        """Handle employee selection"""
        employee_name = self.employee_var.get()
        if employee_name:
            employee = self.employee_map.get(employee_name)
            if employee:
                self.balance_label.config(text=str(employee.remaining_leave_days))

    def calculate_days(self, event=None):
        """Calculate number of days"""
        start = self.start_date.get_date()
        end = self.end_date.get_date()

        if start and end and end >= start:
            # Calculate business days
            days = 0
            current = start
            while current <= end:
                if current.weekday() < 5:  # Monday to Friday
                    days += 1
                current += timedelta(days=1)

            self.days_label.config(text=str(days))
        else:
            self.days_label.config(text="0")

    def submit_request(self):
        """Submit leave request"""
        # Validate employee
        employee_name = self.employee_var.get()
        if not employee_name:
            messagebox.showerror("Error", "Please select an employee")
            return

        employee = self.employee_map.get(employee_name)
        if not employee:
            messagebox.showerror("Error", "Invalid employee selection")
            return

        # Validate dates
        start = self.start_date.get_date()
        end = self.end_date.get_date()

        if end < start:
            messagebox.showerror("Error", "End date must be after start date")
            return

        # Get days count
        days = int(self.days_label.cget('text'))
        if days <= 0:
            messagebox.showerror("Error", "Invalid date range")
            return

        # Check balance for vacation
        if (self.leave_type_var.get() == LeaveType.VACATION.value and
            days > employee.remaining_leave_days):
            if not messagebox.askyesno("Warning",
                                      f"Request exceeds available balance ({employee.remaining_leave_days} days). Continue?"):
                return

        # Create request
        request = LeaveRequest(
            employee_id=employee.id,
            leave_type=LeaveType(self.leave_type_var.get()),
            start_date=start,
            end_date=end,
            days_count=days,
            reason=self.reason_text.get('1.0', 'end-1c'),
            status='Pending'
        )

        try:
            self.db.create_leave_request(request)
            messagebox.showinfo("Success", "Leave request submitted successfully")
            self.clear_form()
            self.refresh_requests()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit request: {str(e)}")

    def clear_form(self):
        """Clear request form"""
        self.start_date.set_date(date.today())
        self.end_date.set_date(date.today())
        self.reason_text.delete('1.0', 'end')
        self.days_label.config(text="0")

    def on_request_select(self, event=None):
        """Handle request selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_request_id = item['values'][0]
        else:
            self.selected_request_id = None

    def on_request_double_click(self, event=None):
        """Handle double click on request"""
        self.view_request_details()

    def view_request_details(self):
        """View request details"""
        if not self.selected_request_id:
            messagebox.showwarning("Warning", "Please select a request")
            return

        # TODO: Implement detailed view dialog
        messagebox.showinfo("Info", "Detailed view to be implemented")

    def approve_request(self):
        """Approve selected request"""
        if not self.selected_request_id:
            messagebox.showwarning("Warning", "Please select a request to approve")
            return

        if messagebox.askyesno("Confirm", "Approve this leave request?"):
            try:
                # TODO: Get actual approver name from logged-in user
                success = self.db.approve_leave_request(self.selected_request_id, "Manager")
                if success:
                    messagebox.showinfo("Success", "Leave request approved")
                    self.refresh_requests()
                    self.refresh_data()  # Update balances
                else:
                    messagebox.showerror("Error", "Failed to approve request")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to approve request: {str(e)}")

    def reject_request(self):
        """Reject selected request"""
        if not self.selected_request_id:
            messagebox.showwarning("Warning", "Please select a request to reject")
            return

        # TODO: Implement rejection with reason
        messagebox.showinfo("Info", "Rejection functionality to be implemented")

    def delete_request(self):
        """Delete selected request"""
        if not self.selected_request_id:
            messagebox.showwarning("Warning", "Please select a request to delete")
            return

        if messagebox.askyesno("Confirm", "Delete this leave request?"):
            # TODO: Implement delete functionality
            messagebox.showinfo("Info", "Delete functionality to be implemented")

    def apply_filters(self):
        """Apply filters"""
        self.refresh_requests()

    def clear_filters(self):
        """Clear all filters"""
        self.filter_employee_combo.set('All')
        self.filter_status_var.set('All')
        self.filter_from_date.set_date(date.today() - timedelta(days=90))
        self.filter_to_date.set_date(date.today())
        self.refresh_requests()

    def export_report(self):
        """Export leave report"""
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
                    writer.writerow(['Employee', 'Leave Type', 'Start Date', 'End Date',
                                   'Days', 'Status', 'Reason', 'Approved By'])

                    # Write data
                    for child in self.tree.get_children():
                        values = self.tree.item(child)['values']
                        writer.writerow(values[1:])  # Exclude ID

                messagebox.showinfo("Success", f"Report exported to {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")