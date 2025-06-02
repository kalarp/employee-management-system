"""
Employee form dialog for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry

from models import Employee, ContractType, WorkMode
from storage.database import Database


class EmployeeForm:
    """Employee form dialog"""

    def __init__(self, parent, database: Database, employee: Employee = None):
        self.db = database
        self.employee = employee
        self.result = False

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Employee" if not employee else "Edit Employee")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Create form
        self.create_form()

        # Load employee data if editing
        if self.employee:
            self.load_employee_data()

        # Wait for dialog to close
        self.dialog.wait_window()

    def create_form(self):
        """Create form fields"""
        # Create scrollable frame
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_frame = canvas.create_window((0, 0), window=self.form_frame, anchor="nw")

        # Personal Information Section
        personal_frame = ttk.LabelFrame(self.form_frame, text="Personal Information", padding=10)
        personal_frame.pack(fill='x', padx=10, pady=5)

        # First Name
        ttk.Label(personal_frame, text="First Name:*").grid(row=0, column=0, sticky='w', pady=5)
        self.first_name_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.first_name_var, width=30).grid(row=0, column=1, pady=5, padx=5)

        # Last Name
        ttk.Label(personal_frame, text="Last Name:*").grid(row=1, column=0, sticky='w', pady=5)
        self.last_name_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.last_name_var, width=30).grid(row=1, column=1, pady=5, padx=5)

        # PESEL
        ttk.Label(personal_frame, text="PESEL:*").grid(row=2, column=0, sticky='w', pady=5)
        self.pesel_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.pesel_var, width=30).grid(row=2, column=1, pady=5, padx=5)

        # Address
        ttk.Label(personal_frame, text="Address:").grid(row=3, column=0, sticky='w', pady=5)
        self.address_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.address_var, width=30).grid(row=3, column=1, pady=5, padx=5)

        # Phone
        ttk.Label(personal_frame, text="Phone:").grid(row=4, column=0, sticky='w', pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.phone_var, width=30).grid(row=4, column=1, pady=5, padx=5)

        # Email
        ttk.Label(personal_frame, text="Email:").grid(row=5, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(personal_frame, textvariable=self.email_var, width=30).grid(row=5, column=1, pady=5, padx=5)

        # Employment Information Section
        employment_frame = ttk.LabelFrame(self.form_frame, text="Employment Information", padding=10)
        employment_frame.pack(fill='x', padx=10, pady=5)

        # Position
        ttk.Label(employment_frame, text="Position:").grid(row=0, column=0, sticky='w', pady=5)
        self.position_var = tk.StringVar()
        ttk.Entry(employment_frame, textvariable=self.position_var, width=30).grid(row=0, column=1, pady=5, padx=5)

        # Department
        ttk.Label(employment_frame, text="Department:").grid(row=1, column=0, sticky='w', pady=5)
        self.department_var = tk.StringVar()
        ttk.Entry(employment_frame, textvariable=self.department_var, width=30).grid(row=1, column=1, pady=5, padx=5)

        # Hire Date
        ttk.Label(employment_frame, text="Hire Date:").grid(row=2, column=0, sticky='w', pady=5)
        self.hire_date = DateEntry(employment_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.hire_date.grid(row=2, column=1, pady=5, padx=5, sticky='w')

        # Contract Type
        ttk.Label(employment_frame, text="Contract Type:").grid(row=3, column=0, sticky='w', pady=5)
        self.contract_type_var = tk.StringVar()
        contract_combo = ttk.Combobox(employment_frame, textvariable=self.contract_type_var, width=27)
        contract_combo['values'] = [ct.value for ct in ContractType]
        contract_combo.grid(row=3, column=1, pady=5, padx=5)
        contract_combo.set(ContractType.EMPLOYMENT.value)

        # Contract Number
        ttk.Label(employment_frame, text="Contract Number:").grid(row=4, column=0, sticky='w', pady=5)
        self.contract_number_var = tk.StringVar()
        ttk.Entry(employment_frame, textvariable=self.contract_number_var, width=30).grid(row=4, column=1, pady=5,
                                                                                          padx=5)

        # Contract End Date
        ttk.Label(employment_frame, text="Contract End Date:").grid(row=5, column=0, sticky='w', pady=5)
        self.contract_end_date = DateEntry(employment_frame, width=12, background='darkblue',
                                           foreground='white', borderwidth=2)
        self.contract_end_date.grid(row=5, column=1, pady=5, padx=5, sticky='w')
        self.contract_end_date.set_date(None)

        # Work Mode
        ttk.Label(employment_frame, text="Work Mode:").grid(row=6, column=0, sticky='w', pady=5)
        self.work_mode_var = tk.StringVar()
        work_mode_combo = ttk.Combobox(employment_frame, textvariable=self.work_mode_var, width=27)
        work_mode_combo['values'] = [wm.value for wm in WorkMode]
        work_mode_combo.grid(row=6, column=1, pady=5, padx=5)
        work_mode_combo.set(WorkMode.OFFICE.value)

        # Leave Information Section
        leave_frame = ttk.LabelFrame(self.form_frame, text="Leave Information", padding=10)
        leave_frame.pack(fill='x', padx=10, pady=5)

        # Annual Leave Days
        ttk.Label(leave_frame, text="Annual Leave Days:").grid(row=0, column=0, sticky='w', pady=5)
        self.annual_leave_var = tk.IntVar(value=26)
        ttk.Spinbox(leave_frame, textvariable=self.annual_leave_var, from_=0, to=365, width=10).grid(row=0, column=1,
                                                                                                     pady=5, padx=5,
                                                                                                     sticky='w')

        # Remaining Leave Days
        ttk.Label(leave_frame, text="Remaining Leave Days:").grid(row=1, column=0, sticky='w', pady=5)
        self.remaining_leave_var = tk.IntVar(value=26)
        ttk.Spinbox(leave_frame, textvariable=self.remaining_leave_var, from_=0, to=365, width=10).grid(row=1, column=1,
                                                                                                        pady=5, padx=5,
                                                                                                        sticky='w')

        # Compliance Information Section
        compliance_frame = ttk.LabelFrame(self.form_frame, text="Compliance Information", padding=10)
        compliance_frame.pack(fill='x', padx=10, pady=5)

        # Medical Exam Date
        ttk.Label(compliance_frame, text="Medical Exam Date:").grid(row=0, column=0, sticky='w', pady=5)
        self.medical_exam_date = DateEntry(compliance_frame, width=12, background='darkblue',
                                           foreground='white', borderwidth=2)
        self.medical_exam_date.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        self.medical_exam_date.set_date(None)

        # Safety Training Date
        ttk.Label(compliance_frame, text="Safety Training Date:").grid(row=1, column=0, sticky='w', pady=5)
        self.safety_training_date = DateEntry(compliance_frame, width=12, background='darkblue',
                                              foreground='white', borderwidth=2)
        self.safety_training_date.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        self.safety_training_date.set_date(None)

        # Update scroll region
        self.form_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(button_frame, text="Save", command=self.save_employee).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side='right', padx=5)

    def load_employee_data(self):
        """Load employee data into form"""
        self.first_name_var.set(self.employee.first_name)
        self.last_name_var.set(self.employee.last_name)
        self.pesel_var.set(self.employee.pesel)
        self.address_var.set(self.employee.address or '')
        self.phone_var.set(self.employee.phone or '')
        self.email_var.set(self.employee.email or '')
        self.position_var.set(self.employee.position or '')
        self.department_var.set(self.employee.department or '')

        if self.employee.hire_date:
            self.hire_date.set_date(self.employee.hire_date)

        self.contract_type_var.set(self.employee.contract_type.value)
        self.contract_number_var.set(self.employee.contract_number or '')

        if self.employee.contract_end_date:
            self.contract_end_date.set_date(self.employee.contract_end_date)

        self.work_mode_var.set(self.employee.work_mode.value)
        self.annual_leave_var.set(self.employee.annual_leave_days)
        self.remaining_leave_var.set(self.employee.remaining_leave_days)

        if self.employee.medical_exam_date:
            self.medical_exam_date.set_date(self.employee.medical_exam_date)

        if self.employee.safety_training_date:
            self.safety_training_date.set_date(self.employee.safety_training_date)

    def save_employee(self):
        """Save employee data"""
        # Validate required fields
        if not all([self.first_name_var.get(), self.last_name_var.get(), self.pesel_var.get()]):
            messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
            return

        # Validate PESEL
        if len(self.pesel_var.get()) != 11 or not self.pesel_var.get().isdigit():
            messagebox.showerror("Error", "PESEL must be 11 digits")
            return

        try:
            # Create or update employee object
            if self.employee:
                employee = self.employee
            else:
                employee = Employee()

            # Set employee data
            employee.first_name = self.first_name_var.get()
            employee.last_name = self.last_name_var.get()
            employee.pesel = self.pesel_var.get()
            employee.address = self.address_var.get() or None
            employee.phone = self.phone_var.get() or None
            employee.email = self.email_var.get() or None
            employee.position = self.position_var.get() or None
            employee.department = self.department_var.get() or None
            employee.hire_date = self.hire_date.get_date()
            employee.contract_number = self.contract_number_var.get() or None
            employee.contract_type = ContractType(self.contract_type_var.get())

            # Handle optional dates
            contract_end = self.contract_end_date.get_date()
            employee.contract_end_date = contract_end if contract_end != date.today() else None

            medical_exam = self.medical_exam_date.get_date()
            employee.medical_exam_date = medical_exam if medical_exam != date.today() else None

            safety_training = self.safety_training_date.get_date()
            employee.safety_training_date = safety_training if safety_training != date.today() else None

            employee.work_mode = WorkMode(self.work_mode_var.get())
            employee.annual_leave_days = self.annual_leave_var.get()
            employee.remaining_leave_days = self.remaining_leave_var.get()

            # Save to database
            if self.employee:
                success = self.db.update_employee(employee)
            else:
                employee_id = self.db.create_employee(employee)
                success = employee_id is not None

            if success:
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to save employee")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save employee: {str(e)}")