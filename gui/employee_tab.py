"""
Employee management tab for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional

from models import Employee, ContractType, WorkMode
from storage.database import Database
from gui.employee_form import EmployeeForm


class EmployeeTab:
    """Employee management tab"""

    def __init__(self, parent, database: Database):
        self.parent = parent
        self.db = database
        self.selected_employee_id = None

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Create UI components
        self.create_search_frame()
        self.create_employee_list()
        self.create_button_frame()

        # Load employees
        self.refresh_employee_list()

    def create_search_frame(self):
        """Create search frame"""
        search_frame = ttk.LabelFrame(self.frame, text="Search Employees")
        search_frame.pack(fill='x', padx=10, pady=5)

        # Search entry
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)

        # Department filter
        ttk.Label(search_frame, text="Department:").pack(side='left', padx=5)
        self.dept_var = tk.StringVar()
        self.dept_combo = ttk.Combobox(search_frame, textvariable=self.dept_var, width=20)
        self.dept_combo.pack(side='left', padx=5)
        self.dept_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Clear filters button
        ttk.Button(search_frame, text="Clear Filters", command=self.clear_filters).pack(side='left', padx=5)

    def create_employee_list(self):
        """Create employee list view"""
        list_frame = ttk.LabelFrame(self.frame, text="Employee List")
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
            'ID', 'Name', 'PESEL', 'Position', 'Department',
            'Contract Type', 'Hire Date', 'Contract End'
        )

        # Format columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Name', width=150)
        self.tree.column('PESEL', width=100, anchor='center')
        self.tree.column('Position', width=120)
        self.tree.column('Department', width=100)
        self.tree.column('Contract Type', width=120)
        self.tree.column('Hire Date', width=100, anchor='center')
        self.tree.column('Contract End', width=100, anchor='center')

        # Create headings
        self.tree.heading('#0', text='', anchor='w')
        self.tree.heading('ID', text='ID', anchor='center')
        self.tree.heading('Name', text='Name', anchor='w')
        self.tree.heading('PESEL', text='PESEL', anchor='center')
        self.tree.heading('Position', text='Position', anchor='w')
        self.tree.heading('Department', text='Department', anchor='w')
        self.tree.heading('Contract Type', text='Contract Type', anchor='w')
        self.tree.heading('Hire Date', text='Hire Date', anchor='center')
        self.tree.heading('Contract End', text='Contract End', anchor='center')

        self.tree.pack(fill='both', expand=True)

        # Bind double-click event
        self.tree.bind('<Double-Button-1>', self.on_employee_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_employee_select)

        # Add row coloring for contract expiry
        self.tree.tag_configure('expired', background='#ffcccc')
        self.tree.tag_configure('expiring', background='#ffffcc')

    def create_button_frame(self):
        """Create button frame"""
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        # Buttons
        ttk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Employee", command=self.edit_employee).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Employee", command=self.delete_employee).pack(side='left', padx=5)
        ttk.Button(button_frame, text="View Details", command=self.view_employee_details).pack(side='left', padx=5)

        # Statistics
        self.stats_label = ttk.Label(button_frame, text="")
        self.stats_label.pack(side='right', padx=5)

    def refresh_employee_list(self):
        """Refresh employee list"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get all employees
        employees = self.db.get_all_employees()

        # Get unique departments
        departments = set(emp.department for emp in employees if emp.department)
        self.dept_combo['values'] = ['All'] + sorted(departments)

        # Apply filters
        search_term = self.search_var.get().lower()
        dept_filter = self.dept_var.get()

        filtered_employees = []
        for emp in employees:
            # Apply search filter
            if search_term:
                if not any(search_term in str(getattr(emp, field, '')).lower()
                           for field in ['first_name', 'last_name', 'pesel', 'position']):
                    continue

            # Apply department filter
            if dept_filter and dept_filter != 'All' and emp.department != dept_filter:
                continue

            filtered_employees.append(emp)

        # Add employees to tree
        for emp in filtered_employees:
            tags = []

            # Check contract expiry
            if emp.contract_end_date:
                days_until_expiry = (emp.contract_end_date - date.today()).days
                if days_until_expiry < 0:
                    tags.append('expired')
                elif days_until_expiry <= 30:
                    tags.append('expiring')

            self.tree.insert('', 'end', values=(
                emp.id,
                emp.full_name,
                emp.pesel,
                emp.position or '',
                emp.department or '',
                emp.contract_type.value,
                emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else '',
                emp.contract_end_date.strftime('%Y-%m-%d') if emp.contract_end_date else ''
            ), tags=tags)

        # Update statistics
        self.stats_label.config(text=f"Total Employees: {len(filtered_employees)}")

    def on_search(self, event=None):
        """Handle search"""
        self.refresh_employee_list()

    def on_filter_change(self, event=None):
        """Handle filter change"""
        self.refresh_employee_list()

    def clear_filters(self):
        """Clear all filters"""
        self.search_var.set('')
        self.dept_var.set('All')
        self.refresh_employee_list()

    def on_employee_select(self, event=None):
        """Handle employee selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_employee_id = item['values'][0]
        else:
            self.selected_employee_id = None

    def on_employee_double_click(self, event=None):
        """Handle double-click on employee"""
        self.edit_employee()

    def add_employee(self):
        """Add new employee"""
        form = EmployeeForm(self.parent, self.db)
        if form.result:
            self.refresh_employee_list()
            messagebox.showinfo("Success", "Employee added successfully!")

    def edit_employee(self):
        """Edit selected employee"""
        if not self.selected_employee_id:
            messagebox.showwarning("Warning", "Please select an employee to edit")
            return

        employee = self.db.get_employee(self.selected_employee_id)
        if employee:
            form = EmployeeForm(self.parent, self.db, employee)
            if form.result:
                self.refresh_employee_list()
                messagebox.showinfo("Success", "Employee updated successfully!")

    def delete_employee(self):
        """Delete selected employee"""
        if not self.selected_employee_id:
            messagebox.showwarning("Warning", "Please select an employee to delete")
            return

        employee = self.db.get_employee(self.selected_employee_id)
        if employee:
            if messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete {employee.full_name}?"):
                if self.db.delete_employee(self.selected_employee_id):
                    self.refresh_employee_list()
                    messagebox.showinfo("Success", "Employee deleted successfully!")
                else:
                    messagebox.showerror("Error", "Failed to delete employee")

    def view_employee_details(self):
        """View employee details"""
        if not self.selected_employee_id:
            messagebox.showwarning("Warning", "Please select an employee to view")
            return

        employee = self.db.get_employee(self.selected_employee_id)
        if employee:
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Employee Details - {employee.full_name}")
            details_window.geometry("600x500")

            # Create scrollable frame
            canvas = tk.Canvas(details_window)
            scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            # Add employee details
            details = [
                ("Personal Information", ""),
                ("Name:", employee.full_name),
                ("PESEL:", employee.pesel),
                ("Address:", employee.address or "N/A"),
                ("Phone:", employee.phone or "N/A"),
                ("Email:", employee.email or "N/A"),
                ("", ""),
                ("Employment Information", ""),
                ("Position:", employee.position or "N/A"),
                ("Department:", employee.department or "N/A"),
                ("Hire Date:", employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else "N/A"),
                ("Contract Type:", employee.contract_type.value),
                ("Contract Number:", employee.contract_number or "N/A"),
                ("Contract End Date:",
                 employee.contract_end_date.strftime('%Y-%m-%d') if employee.contract_end_date else "N/A"),
                ("Work Mode:", employee.work_mode.value),
                ("", ""),
                ("Leave Information", ""),
                ("Annual Leave Days:", str(employee.annual_leave_days)),
                ("Remaining Leave Days:", str(employee.remaining_leave_days)),
                ("", ""),
                ("Compliance Information", ""),
                ("Medical Exam Date:",
                 employee.medical_exam_date.strftime('%Y-%m-%d') if employee.medical_exam_date else "N/A"),
                ("Safety Training Date:",
                 employee.safety_training_date.strftime('%Y-%m-%d') if employee.safety_training_date else "N/A"),
            ]

            for i, (label, value) in enumerate(details):
                if value == "" and label == "":
                    continue
                elif value == "":
                    # Section header
                    ttk.Label(scrollable_frame, text=label, font=('Arial', 12, 'bold')).grid(
                        row=i, column=0, columnspan=2, pady=10, padx=10, sticky='w'
                    )
                else:
                    ttk.Label(scrollable_frame, text=label).grid(row=i, column=0, pady=2, padx=10, sticky='w')
                    ttk.Label(scrollable_frame, text=value).grid(row=i, column=1, pady=2, padx=10, sticky='w')

            # Update scroll region
            scrollable_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

            # Pack widgets
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # Close button
            ttk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)