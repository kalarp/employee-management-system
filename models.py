"""
Data models for Employee Management System
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class ContractType(Enum):
    """Types of employment contracts"""
    EMPLOYMENT = "Employment Contract"
    SERVICE = "Service Contract"
    WORK = "Work Contract"


class LeaveType(Enum):
    """Types of leave"""
    VACATION = "Vacation"
    SICK = "Sick Leave"
    UNPAID = "Unpaid Leave"
    MATERNITY = "Maternity Leave"
    PATERNITY = "Paternity Leave"
    OTHER = "Other"


class WorkMode(Enum):
    """Work mode types"""
    OFFICE = "Office"
    REMOTE = "Remote"
    HYBRID = "Hybrid"


@dataclass
class Employee:
    """Employee model"""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    pesel: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    position: str = ""
    department: str = ""
    hire_date: date = None
    contract_number: str = ""
    contract_type: ContractType = ContractType.EMPLOYMENT
    contract_end_date: Optional[date] = None
    annual_leave_days: int = 26
    remaining_leave_days: int = 26
    work_mode: WorkMode = WorkMode.OFFICE
    medical_exam_date: Optional[date] = None
    safety_training_date: Optional[date] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


@dataclass
class TimeEntry:
    """Time tracking entry model"""
    id: Optional[int] = None
    employee_id: int = None
    date: date = None
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    work_mode: WorkMode = WorkMode.OFFICE
    notes: str = ""
    created_at: datetime = None

    @property
    def hours_worked(self) -> float:
        """Calculate hours worked"""
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return round(delta.total_seconds() / 3600, 2)
        return 0.0


@dataclass
class LeaveRequest:
    """Leave request model"""
    id: Optional[int] = None
    employee_id: int = None
    leave_type: LeaveType = LeaveType.VACATION
    start_date: date = None
    end_date: date = None
    days_count: int = 0
    reason: str = ""
    status: str = "Pending"  # Pending, Approved, Rejected
    approved_by: Optional[str] = None
    approved_date: Optional[datetime] = None
    created_at: datetime = None

    @property
    def is_approved(self) -> bool:
        return self.status == "Approved"

    @property
    def is_pending(self) -> bool:
        return self.status == "Pending"


@dataclass
class Document:
    """Document model"""
    id: Optional[int] = None
    employee_id: int = None
    document_type: str = ""  # Contract, Certificate, Leave Confirmation, etc.
    document_name: str = ""
    file_path: Optional[str] = None
    generated_date: datetime = None
    created_at: datetime = None


@dataclass
class Notification:
    """Notification model"""
    id: Optional[int] = None
    employee_id: Optional[int] = None
    notification_type: str = ""  # Contract Expiry, Medical Exam, Training
    title: str = ""
    message: str = ""
    due_date: date = None
    is_read: bool = False
    created_at: datetime = None

    @property
    def is_overdue(self) -> bool:
        """Check if notification is overdue"""
        if self.due_date:
            return date.today() > self.due_date
        return False


@dataclass
class Department:
    """Department model"""
    id: Optional[int] = None
    name: str = ""
    manager_id: Optional[int] = None
    description: str = ""
    created_at: datetime = None


@dataclass
class Position:
    """Position model"""
    id: Optional[int] = None
    title: str = ""
    department_id: Optional[int] = None
    description: str = ""
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    created_at: datetime = None