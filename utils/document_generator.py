"""
Document generator utility for Employee Management System
"""

import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any

from models import Employee, LeaveRequest


class DocumentGenerator:
    """Generate various documents for employees"""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.ensure_templates_exist()

    def ensure_templates_exist(self):
        """Ensure template directory exists"""
        Path(self.templates_dir).mkdir(exist_ok=True)

    def generate_employment_certificate(self,
                                        employee: Employee,
                                        purpose: str = "",
                                        additional_notes: str = "") -> str:
        """Generate employment certificate"""
        template = """
{company_name}
{company_address}
{company_phone}
{company_email}

CERTIFICATE OF EMPLOYMENT

Date: {current_date}

TO WHOM IT MAY CONCERN:

This is to certify that {employee_name} (PESEL: {pesel}) has been employed with {company_name} 
since {hire_date}.

Employment Details:
- Position: {position}
- Department: {department}
- Employment Type: {contract_type}
- Current Status: {status}

{employee_pronoun} has been a valuable member of our organization and continues to contribute 
to our team's success.

This certificate is issued upon request for {purpose}.

{additional_notes}

Should you require any additional information, please do not hesitate to contact our 
Human Resources Department.

Sincerely,

_______________________
{hr_manager_name}
Human Resources Manager
{company_name}

This is a computer-generated document and is valid without signature.
"""

        # Determine status
        status = "Active Employee"
        if employee.contract_end_date and employee.contract_end_date < date.today():
            status = f"Employment ended on {employee.contract_end_date.strftime('%B %d, %Y')}"

        # Format the certificate
        return template.format(
            company_name=self.get_company_info()['name'],
            company_address=self.get_company_info()['address'],
            company_phone=self.get_company_info()['phone'],
            company_email=self.get_company_info()['email'],
            current_date=date.today().strftime('%B %d, %Y'),
            employee_name=employee.full_name,
            pesel=employee.pesel,
            hire_date=employee.hire_date.strftime('%B %d, %Y') if employee.hire_date else 'N/A',
            position=employee.position or 'N/A',
            department=employee.department or 'N/A',
            contract_type=employee.contract_type.value,
            status=status,
            employee_pronoun="He/She",
            purpose=purpose or "official purposes",
            additional_notes=f"\n{additional_notes}\n" if additional_notes else "",
            hr_manager_name=self.get_company_info()['hr_manager']
        )

    def generate_leave_confirmation(self,
                                    employee: Employee,
                                    leave_request: LeaveRequest,
                                    additional_notes: str = "") -> str:
        """Generate leave confirmation letter"""
        template = """
{company_name}
{company_address}

LEAVE CONFIRMATION LETTER

Date: {current_date}

Dear {employee_name},

This letter confirms that your leave request has been {status}.

Leave Details:
- Leave Type: {leave_type}
- Start Date: {start_date}
- End Date: {end_date}
- Total Days: {total_days}
- Remaining Balance: {remaining_balance} days

Reason: {reason}

{status_message}

{additional_notes}

Please ensure all your responsibilities are properly handed over before your leave begins.

If you have any questions, please contact the Human Resources Department.

Best regards,

_______________________
{hr_manager_name}
Human Resources Department
{company_name}
"""

        status_message = ""
        if leave_request.status == "Approved":
            status_message = "Your leave has been approved. Please ensure a smooth handover of your duties."
        elif leave_request.status == "Rejected":
            status_message = "Unfortunately, your leave request could not be approved at this time."
        else:
            status_message = "Your leave request is pending review."

        return template.format(
            company_name=self.get_company_info()['name'],
            company_address=self.get_company_info()['address'],
            current_date=date.today().strftime('%B %d, %Y'),
            employee_name=employee.full_name,
            status=leave_request.status.lower(),
            leave_type=leave_request.leave_type.value,
            start_date=leave_request.start_date.strftime('%B %d, %Y'),
            end_date=leave_request.end_date.strftime('%B %d, %Y'),
            total_days=leave_request.days_count,
            remaining_balance=employee.remaining_leave_days,
            reason=leave_request.reason,
            status_message=status_message,
            additional_notes=f"\n{additional_notes}\n" if additional_notes else "",
            hr_manager_name=self.get_company_info()['hr_manager']
        )

    def generate_contract(self,
                          employee: Employee,
                          salary: str = "",
                          benefits: str = "",
                          additional_terms: str = "") -> str:
        """Generate employment contract"""
        template = """
EMPLOYMENT CONTRACT

This Employment Contract ("Contract") is entered into on {current_date}, between:

EMPLOYER:
{company_name}
{company_address}
(hereinafter referred to as "Employer")

AND

EMPLOYEE:
Name: {employee_name}
PESEL: {pesel}
Address: {employee_address}
(hereinafter referred to as "Employee")

WHEREAS, the Employer desires to employ the Employee, and the Employee desires to be employed 
by the Employer, on the terms and conditions set forth herein.

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein, 
the parties agree as follows:

1. POSITION AND DUTIES
   The Employee shall serve as {position} in the {department} department. The Employee shall 
   perform such duties as are customarily associated with such position and such other duties 
   as may be assigned by the Employer.

2. TERM OF EMPLOYMENT
   Employment shall commence on {start_date} and shall be {contract_type}.
   {contract_end_clause}

3. COMPENSATION
   {salary_clause}

4. BENEFITS
   {benefits_clause}

5. WORKING HOURS
   The Employee's regular working hours shall be Monday through Friday, from 8:00 AM to 5:00 PM, 
   with one hour for lunch. The Employee's work mode shall be {work_mode}.

6. ANNUAL LEAVE
   The Employee shall be entitled to {annual_leave_days} days of paid annual leave per year.

7. CONFIDENTIALITY
   The Employee agrees to maintain the confidentiality of all proprietary information of the 
   Employer during and after the term of employment.

8. TERMINATION
   This Contract may be terminated by either party with appropriate notice as per applicable 
   labor laws.

9. GOVERNING LAW
   This Contract shall be governed by the laws of the jurisdiction in which the Employer operates.

{additional_terms}

IN WITNESS WHEREOF, the parties have executed this Contract as of the date first above written.

EMPLOYER:                              EMPLOYEE:

_______________________               _______________________
{company_representative}               {employee_name}
{company_name}                        
Date: _____________                   Date: _____________
"""

        # Prepare contract end clause
        contract_end_clause = ""
        if employee.contract_end_date:
            contract_end_clause = f"This contract shall end on {employee.contract_end_date.strftime('%B %d, %Y')}."
        else:
            contract_end_clause = "This is a permanent employment contract with no fixed end date."

        # Prepare salary clause
        salary_clause = salary if salary else "As mutually agreed and documented separately."

        # Prepare benefits clause
        benefits_clause = benefits if benefits else "As per company policy and applicable regulations."

        # Additional terms section
        additional_terms_section = ""
        if additional_terms:
            additional_terms_section = f"\n10. ADDITIONAL TERMS\n{additional_terms}\n"

        return template.format(
            current_date=date.today().strftime('%B %d, %Y'),
            company_name=self.get_company_info()['name'],
            company_address=self.get_company_info()['address'],
            employee_name=employee.full_name,
            pesel=employee.pesel,
            employee_address=employee.address or '[To be provided]',
            position=employee.position or '[To be determined]',
            department=employee.department or '[To be determined]',
            start_date=employee.hire_date.strftime('%B %d, %Y') if employee.hire_date else '[To be determined]',
            contract_type=employee.contract_type.value.lower(),
            contract_end_clause=contract_end_clause,
            salary_clause=salary_clause,
            benefits_clause=benefits_clause,
            work_mode=employee.work_mode.value,
            annual_leave_days=employee.annual_leave_days,
            additional_terms=additional_terms_section,
            company_representative=self.get_company_info()['ceo']
        )

    def get_company_info(self) -> Dict[str, str]:
        """Get company information (should be configurable)"""
        return {
            'name': 'ABC Company Ltd.',
            'address': '123 Business Street, Warsaw, Poland',
            'phone': '+48 123 456 789',
            'email': 'hr@abccompany.pl',
            'ceo': 'John Smith',
            'hr_manager': 'Jane Doe'
        }

    def save_document(self, content: str, filename: str, output_dir: str = "documents") -> str:
        """Save document to file"""
        # Ensure output directory exists
        Path(output_dir).mkdir(exist_ok=True)

        # Generate unique filename if exists
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(output_dir, filename)
                counter += 1

        # Save document
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath