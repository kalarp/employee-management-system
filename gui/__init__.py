# gui/__init__.py
"""
GUI components for Employee Management System
"""

from .main_window import MainWindow
from .employee_tab import EmployeeTab
from .employee_form import EmployeeForm
from .time_tracking_tab import TimeTrackingTab
from .leave_management_tab import LeaveManagementTab
from .documents_tab import DocumentsTab
from .notifications_tab import NotificationsTab


__all__ = [
    'MainWindow',
    'EmployeeTab',
    'EmployeeForm',
    'TimeTrackingTab',
    'LeaveManagementTab',
    'DocumentsTab',
    'NotificationsTab',

]