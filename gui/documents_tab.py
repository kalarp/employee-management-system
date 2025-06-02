"""
Documents tab for Employee Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import shutil
from pathlib import Path

from models import Document, Employee
from storage.database import Database

class DocumentsTab:
    """Documents management tab"""

    def __init__(self, parent, database: Database):
        self.parent = parent
        self.db = database
        self.selected_document_id = None

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Create UI components
        self.create_generation_frame()
        self.create_documents_list()
        self.create_template_frame()

        # Load initial data
        self.refresh_data()

    def create_generation_frame(self):
        """Create document generation frame"""
        gen_frame = ttk.LabelFrame(self.frame, text="Generate Document")
        gen_frame.pack(fill='x', padx=10, pady=5)

        # Employee selection
        ttk.Label(gen_frame, text="Employee:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(gen_frame, textvariable=self.employee_var, width=30)
        self.employee_combo.grid(row=0, column=1, padx=5, pady=5)

        # Document type
        ttk.Label(gen_frame, text="Document Type:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.doc_type_var = tk.StringVar()
        doc_type_combo = ttk.Combobox(gen_frame, textvariable=self.doc_type_var, width=25)
        doc_type_combo['values'] = [
            'Employment Contract',
            'Service Contract',
            'Work Contract',
            'Employment Certificate',
            'Salary Certificate',
            'Leave Confirmation',
            'Termination Letter',
            'Reference Letter'
        ]
        doc_type_combo.set('Employment Certificate')
        doc_type_combo.grid(row=0, column=3, padx=5, pady=5)

        # Additional options frame
        options_frame = ttk.Frame(gen_frame)
        options_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Date range for certificates
        ttk.Label(options_frame, text="Period From:").pack(side='left', padx=5)
        self.period_from = ttk.Entry(options_frame, width=12)
        self.period_from.pack(side='left', padx=5)

        ttk.Label(options_frame, text="To:").pack(side='left', padx=5)
        self.period_to = ttk.Entry(options_frame, width=12)
        self.period_to.pack(side='left', padx=5)

        # Purpose
        ttk.Label(options_frame, text="Purpose:").pack(side='left', padx=5)
        self.purpose_var = tk.StringVar()
        self.purpose_entry = ttk.Entry(options_frame, textvariable=self.purpose_var, width=30)
        self.purpose_entry.pack(side='left', padx=5)

        # Notes/Comments
        ttk.Label(gen_frame, text="Additional Notes:").grid(row=2, column=0, padx=5, pady=5, sticky='nw')
        self.notes_text = tk.Text(gen_frame, width=70, height=4)
        self.notes_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(gen_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="Generate Document", command=self.generate_document).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Preview", command=self.preview_document).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Email Document", command=self.email_document).pack(side='left', padx=5)

    def create_documents_list(self):
        """Create documents list"""
        list_frame = ttk.LabelFrame(self.frame, text="Generated Documents")
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Search bar
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', self.on_search)

        # Filter by employee
        ttk.Label(search_frame, text="Filter by Employee:").pack(side='left', padx=5)
        self.filter_employee_var = tk.StringVar()
        self.filter_employee_combo = ttk.Combobox(search_frame, textvariable=self.filter_employee_var, width=25)
        self.filter_employee_combo.pack(side='left', padx=5)
        self.filter_employee_combo.bind('<<ComboboxSelected>>', self.on_filter_change)

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
            'ID', 'Employee', 'Document Type', 'Document Name',
            'Generated Date', 'File Path'
        )

        # Format columns
        self.tree.column('#0', width=0, stretch=False)
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Employee', width=150)
        self.tree.column('Document Type', width=150)
        self.tree.column('Document Name', width=200)
        self.tree.column('Generated Date', width=150, anchor='center')
        self.tree.column('File Path', width=300)

        # Create headings
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)

        self.tree.pack(fill='both', expand=True)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_document_select)
        self.tree.bind('<Double-Button-1>', self.open_document)

        # Create context menu
        self.create_context_menu()

    def create_context_menu(self):
        """Create context menu for documents"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Open Document", command=self.open_document)
        self.context_menu.add_command(label="Open Folder", command=self.open_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Email Document", command=self.email_selected_document)
        self.context_menu.add_command(label="Print Document", command=self.print_document)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename", command=self.rename_document)
        self.context_menu.add_command(label="Delete", command=self.delete_document)

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu"""
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def create_template_frame(self):
        """Create template management frame"""
        template_frame = ttk.LabelFrame(self.frame, text="Document Templates")
        template_frame.pack(fill='x', padx=10, pady=5)

        # Template buttons
        button_frame = ttk.Frame(template_frame)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Manage Templates", command=self.manage_templates).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Import Template", command=self.import_template).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export Template", command=self.export_template).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Template", command=self.edit_template).pack(side='left', padx=5)

        # Statistics
        self.stats_label = ttk.Label(button_frame, text="")
        self.stats_label.pack(side='right', padx=5)

    def refresh_data(self):
        """Refresh all data"""
        # Refresh employee list
        employees = self.db.get_all_employees()
        employee_names = [f"{emp.first_name} {emp.last_name}" for emp in employees]

        self.employee_combo['values'] = employee_names
        self.filter_employee_combo['values'] = ['All'] + employee_names

        if employee_names:
            self.employee_combo.set(employee_names[0])
            self.filter_employee_combo.set('All')

        # Store employee mapping
        self.employee_map = {f"{emp.first_name} {emp.last_name}": emp.id for emp in employees}

        # Refresh documents list
        self.refresh_documents()

    def refresh_documents(self):
        """Refresh documents list"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get all documents from database
        # TODO: Implement get_all_documents in database.py
        documents = []  # self.db.get_all_documents()

        # Apply filters
        search_term = self.search_var.get().lower()
        employee_filter = self.filter_employee_var.get()

        filtered_documents = []
        for doc in documents:
            # Apply search filter
            if search_term:
                if not any(search_term in str(getattr(doc, field, '')).lower()
                          for field in ['document_type', 'document_name']):
                    continue

            # Apply employee filter
            if employee_filter and employee_filter != 'All':
                employee_id = self.employee_map.get(employee_filter)
                if doc.employee_id != employee_id:
                    continue

            filtered_documents.append(doc)

        # Add to tree
        for doc in filtered_documents:
            # Get employee name
            employee = self.db.get_employee(doc.employee_id)
            employee_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"

            self.tree.insert('', 'end', values=(
                doc.id,
                employee_name,
                doc.document_type,
                doc.document_name,
                doc.generated_date.strftime('%Y-%m-%d %H:%M') if doc.generated_date else '',
                doc.file_path or ''
            ))

        # Update statistics
        self.stats_label.config(text=f"Total Documents: {len(filtered_documents)}")

    def generate_document(self):
        """Generate document"""
        # Validate employee selection
        employee_name = self.employee_var.get()
        if not employee_name:
            messagebox.showerror("Error", "Please select an employee")
            return

        employee_id = self.employee_map.get(employee_name)
        if not employee_id:
            messagebox.showerror("Error", "Invalid employee selection")
            return

        employee = self.db.get_employee(employee_id)
        doc_type = self.doc_type_var.get()

        try:
            # Generate document content
            content = self.create_document_content(employee, doc_type)

            # Create filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = employee_name.replace(' ', '_')
            filename = f"{doc_type.replace(' ', '_')}_{safe_name}_{timestamp}.txt"

            # Save document
            doc_path = os.path.join('documents', filename)
            os.makedirs('documents', exist_ok=True)

            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Save to database
            document = Document(
                employee_id=employee_id,
                document_type=doc_type,
                document_name=filename,
                file_path=doc_path,
                generated_date=datetime.now()
            )

            # TODO: Implement create_document in database.py
            # self.db.create_document(document)

            messagebox.showinfo("Success", f"Document generated successfully!\n\nSaved to: {doc_path}")

            # Refresh list
            self.refresh_documents()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate document: {str(e)}")

    def create_document_content(self, employee: Employee, doc_type: str) -> str:
        """Create document content based on type"""
        company_name = "Your Company Ltd."
        company_address = "123 Business Street, City, Country"
        current_date = date.today().strftime('%B %d, %Y')

        if doc_type == "Employment Certificate":
            content = f"""
{company_name}
{company_address}

EMPLOYMENT CERTIFICATE

Date: {current_date}

TO WHOM IT MAY CONCERN

This is to certify that {employee.full_name} (PESEL: {employee.pesel}) has been employed 
with {company_name} since {employee.hire_date.strftime('%B %d, %Y') if employee.hire_date else 'N/A'}.

Current Position: {employee.position or 'N/A'}
Department: {employee.department or 'N/A'}
Employment Type: {employee.contract_type.value}

{employee.first_name} {employee.last_name} is a valued member of our organization and 
continues to be employed with us as of the date of this certificate.

This certificate is issued upon request for {self.purpose_var.get() or 'official purposes'}.

Additional Notes:
{self.notes_text.get('1.0', 'end-1c')}

Sincerely,

_______________________
HR Department
{company_name}
"""

        elif doc_type == "Leave Confirmation":
            content = f"""
{company_name}
{company_address}

LEAVE CONFIRMATION

Date: {current_date}

Employee Name: {employee.full_name}
Employee ID: {employee.id}
Department: {employee.department or 'N/A'}

This letter confirms the approved leave for the above-mentioned employee.

Leave Period: {self.period_from.get()} to {self.period_to.get()}
Remaining Leave Balance: {employee.remaining_leave_days} days

Additional Notes:
{self.notes_text.get('1.0', 'end-1c')}

Approved by:

_______________________
HR Department
{company_name}
"""

        elif doc_type == "Employment Contract":
            content = f"""
EMPLOYMENT CONTRACT

This Employment Contract is entered into on {current_date} between:

EMPLOYER:
{company_name}
{company_address}

EMPLOYEE:
Name: {employee.full_name}
PESEL: {employee.pesel}
Address: {employee.address or 'N/A'}

TERMS OF EMPLOYMENT:

1. Position: {employee.position or 'To be determined'}
2. Department: {employee.department or 'To be determined'}
3. Start Date: {employee.hire_date.strftime('%B %d, %Y') if employee.hire_date else 'To be determined'}
4. Contract Type: {employee.contract_type.value}
5. Work Mode: {employee.work_mode.value}

6. LEAVE ENTITLEMENT:
   Annual Leave: {employee.annual_leave_days} days per year

7. ADDITIONAL TERMS:
{self.notes_text.get('1.0', 'end-1c')}

This contract is subject to the labor laws and regulations of the jurisdiction.

SIGNATURES:

_______________________                 _______________________
EMPLOYER                                EMPLOYEE
{company_name}                          {employee.full_name}
Date: _____________                     Date: _____________
"""

        else:
            # Generic template
            content = f"""
{company_name}
{company_address}

{doc_type.upper()}

Date: {current_date}

Employee Information:
Name: {employee.full_name}
PESEL: {employee.pesel}
Position: {employee.position or 'N/A'}
Department: {employee.department or 'N/A'}

{self.notes_text.get('1.0', 'end-1c')}

_______________________
Authorized Signature
{company_name}
"""

        return content

    def preview_document(self):
        """Preview document before generation"""
        # Validate employee selection
        employee_name = self.employee_var.get()
        if not employee_name:
            messagebox.showerror("Error", "Please select an employee")
            return

        employee_id = self.employee_map.get(employee_name)
        employee = self.db.get_employee(employee_id)
        doc_type = self.doc_type_var.get()

        # Create preview window
        preview_window = tk.Toplevel(self.parent)
        preview_window.title(f"Document Preview - {doc_type}")
        preview_window.geometry("700x600")

        # Create text widget with scrollbar
        text_frame = ttk.Frame(preview_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)

        text_scroll = ttk.Scrollbar(text_frame)
        text_scroll.pack(side='right', fill='y')

        preview_text = tk.Text(text_frame, wrap='word', yscrollcommand=text_scroll.set)
        preview_text.pack(fill='both', expand=True)
        text_scroll.config(command=preview_text.yview)

        # Insert document content
        content = self.create_document_content(employee, doc_type)
        preview_text.insert('1.0', content)
        preview_text.config(state='disabled')

        # Buttons
        button_frame = ttk.Frame(preview_window)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Generate",
                  command=lambda: [self.generate_document(), preview_window.destroy()]).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Close", command=preview_window.destroy).pack(side='right', padx=5)

    def email_document(self):
        """Email document (placeholder)"""
        messagebox.showinfo("Info", "Email functionality would be implemented here.\n\nThis would integrate with email client or SMTP server.")

    def email_selected_document(self):
        """Email selected document"""
        if not self.selected_document_id:
            messagebox.showwarning("Warning", "Please select a document")
            return

        self.email_document()

    def on_search(self, event=None):
        """Handle search"""
        self.refresh_documents()

    def on_filter_change(self, event=None):
        """Handle filter change"""
        self.refresh_documents()

    def on_document_select(self, event=None):
        """Handle document selection"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_document_id = item['values'][0]
        else:
            self.selected_document_id = None

    def open_document(self, event=None):
        """Open selected document"""
        if not self.selected_document_id:
            messagebox.showwarning("Warning", "Please select a document")
            return

        # Get file path from tree
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            file_path = item['values'][5]  # File path column

            if file_path and os.path.exists(file_path):
                try:
                    os.startfile(file_path)  # Windows
                except:
                    try:
                        os.system(f'open "{file_path}"')  # macOS
                    except:
                        os.system(f'xdg-open "{file_path}"')  # Linux
            else:
                messagebox.showerror("Error", "Document file not found")

    def open_folder(self):
        """Open document folder"""
        if not self.selected_document_id:
            messagebox.showwarning("Warning", "Please select a document")
            return

        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            file_path = item['values'][5]

            if file_path:
                folder = os.path.dirname(file_path)
                if os.path.exists(folder):
                    try:
                        os.startfile(folder)  # Windows
                    except:
                        try:
                            os.system(f'open "{folder}"')  # macOS
                        except:
                            os.system(f'xdg-open "{folder}"')  # Linux

    def print_document(self):
        """Print document (placeholder)"""
        messagebox.showinfo("Info", "Print functionality would be implemented here.\n\nThis would send document to default printer.")

    def rename_document(self):
        """Rename document"""
        if not self.selected_document_id:
            messagebox.showwarning("Warning", "Please select a document")
            return

        # TODO: Implement rename dialog
        messagebox.showinfo("Info", "Rename functionality to be implemented")

    def delete_document(self):
        """Delete selected document"""
        if not self.selected_document_id:
            messagebox.showwarning("Warning", "Please select a document")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this document?"):
            # TODO: Implement delete functionality
            messagebox.showinfo("Info", "Delete functionality to be implemented")

    def manage_templates(self):
        """Manage document templates"""
        # Create template manager window
        template_window = tk.Toplevel(self.parent)
        template_window.title("Document Template Manager")
        template_window.geometry("600x400")

        ttk.Label(template_window, text="Document Template Manager",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        info_text = """
This feature allows you to:
- Create custom document templates
- Edit existing templates
- Import/Export templates
- Set default values and placeholders

Templates use placeholder tags like:
{{employee_name}}, {{position}}, {{hire_date}}, etc.

Coming in future version!
"""

        ttk.Label(template_window, text=info_text, justify='left').pack(padx=20, pady=20)

        ttk.Button(template_window, text="Close", command=template_window.destroy).pack(pady=10)

    def import_template(self):
        """Import document template"""
        filename = filedialog.askopenfilename(
            title="Select Template File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            messagebox.showinfo("Info", f"Template import functionality to be implemented.\n\nSelected: {filename}")

    def export_template(self):
        """Export document template"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            messagebox.showinfo("Info", f"Template export functionality to be implemented.\n\nSelected: {filename}")

    def edit_template(self):
        """Edit document template"""
        messagebox.showinfo("Info", "Template editor to be implemented.\n\nThis would allow visual editing of document templates.")