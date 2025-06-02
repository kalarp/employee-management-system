"""
Database management for Employee Management System
"""

import sqlite3
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import os
from contextlib import contextmanager

from models import (
    Employee, TimeEntry, LeaveRequest, Document,
    Notification, Department, Position,
    ContractType, LeaveType, WorkMode
)


class Database:
    """SQLite database manager"""

    def __init__(self, db_path: str = "employee_management.db"):
        self.db_path = db_path
        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def create_tables(self):
        """Create all database tables"""
        with self.get_cursor() as cursor:
            # Employees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    pesel TEXT UNIQUE NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    position TEXT,
                    department TEXT,
                    hire_date DATE,
                    contract_number TEXT,
                    contract_type TEXT,
                    contract_end_date DATE,
                    annual_leave_days INTEGER DEFAULT 26,
                    remaining_leave_days INTEGER DEFAULT 26,
                    work_mode TEXT DEFAULT 'Office',
                    medical_exam_date DATE,
                    safety_training_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Time entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS time_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    check_in TIMESTAMP,
                    check_out TIMESTAMP,
                    work_mode TEXT DEFAULT 'Office',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')

            # Leave requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leave_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    leave_type TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    days_count INTEGER NOT NULL,
                    reason TEXT,
                    status TEXT DEFAULT 'Pending',
                    approved_by TEXT,
                    approved_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')

            # Documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    document_type TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    file_path TEXT,
                    generated_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')

            # Notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    notification_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT,
                    due_date DATE,
                    is_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')

            # Departments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    manager_id INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (manager_id) REFERENCES employees (id)
                )
            ''')

            # Positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    department_id INTEGER,
                    description TEXT,
                    min_salary REAL,
                    max_salary REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_employee_pesel ON employees(pesel)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_time_entries_employee ON time_entries(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_leave_requests_employee ON leave_requests(employee_id)')

    # Employee operations
    def create_employee(self, employee: Employee) -> int:
        """Create a new employee"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO employees (
                    first_name, last_name, pesel, address, phone, email,
                    position, department, hire_date, contract_number,
                    contract_type, contract_end_date, annual_leave_days,
                    remaining_leave_days, work_mode, medical_exam_date,
                    safety_training_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee.first_name, employee.last_name, employee.pesel,
                employee.address, employee.phone, employee.email,
                employee.position, employee.department, employee.hire_date,
                employee.contract_number, employee.contract_type.value,
                employee.contract_end_date, employee.annual_leave_days,
                employee.remaining_leave_days, employee.work_mode.value,
                employee.medical_exam_date, employee.safety_training_date
            ))
            return cursor.lastrowid

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_employee(row)
            return None

    def get_all_employees(self) -> List[Employee]:
        """Get all employees"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT * FROM employees ORDER BY last_name, first_name')
            return [self._row_to_employee(row) for row in cursor.fetchall()]

    def update_employee(self, employee: Employee) -> bool:
        """Update employee information"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                UPDATE employees SET
                    first_name = ?, last_name = ?, pesel = ?, address = ?,
                    phone = ?, email = ?, position = ?, department = ?,
                    hire_date = ?, contract_number = ?, contract_type = ?,
                    contract_end_date = ?, annual_leave_days = ?,
                    remaining_leave_days = ?, work_mode = ?,
                    medical_exam_date = ?, safety_training_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                employee.first_name, employee.last_name, employee.pesel,
                employee.address, employee.phone, employee.email,
                employee.position, employee.department, employee.hire_date,
                employee.contract_number, employee.contract_type.value,
                employee.contract_end_date, employee.annual_leave_days,
                employee.remaining_leave_days, employee.work_mode.value,
                employee.medical_exam_date, employee.safety_training_date,
                employee.id
            ))
            return cursor.rowcount > 0

    def delete_employee(self, employee_id: int) -> bool:
        """Delete employee"""
        with self.get_cursor() as cursor:
            cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            return cursor.rowcount > 0

    # Time entry operations
    def create_time_entry(self, entry: TimeEntry) -> int:
        """Create time entry"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO time_entries (
                    employee_id, date, check_in, check_out, work_mode, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entry.employee_id, entry.date, entry.check_in,
                entry.check_out, entry.work_mode.value, entry.notes
            ))
            return cursor.lastrowid

    def get_time_entries(self, employee_id: int, start_date: date = None, end_date: date = None) -> List[TimeEntry]:
        """Get time entries for employee"""
        query = 'SELECT * FROM time_entries WHERE employee_id = ?'
        params = [employee_id]

        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)

        query += ' ORDER BY date DESC'

        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return [self._row_to_time_entry(row) for row in cursor.fetchall()]

    # Leave request operations
    def create_leave_request(self, request: LeaveRequest) -> int:
        """Create leave request"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO leave_requests (
                    employee_id, leave_type, start_date, end_date,
                    days_count, reason, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.employee_id, request.leave_type.value,
                request.start_date, request.end_date,
                request.days_count, request.reason, request.status
            ))
            return cursor.lastrowid

    def get_leave_requests(self, employee_id: int = None, status: str = None) -> List[LeaveRequest]:
        """Get leave requests"""
        query = 'SELECT * FROM leave_requests WHERE 1=1'
        params = []

        if employee_id:
            query += ' AND employee_id = ?'
            params.append(employee_id)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC'

        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return [self._row_to_leave_request(row) for row in cursor.fetchall()]

    def approve_leave_request(self, request_id: int, approved_by: str) -> bool:
        """Approve leave request"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                UPDATE leave_requests SET
                    status = 'Approved',
                    approved_by = ?,
                    approved_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (approved_by, request_id))

            if cursor.rowcount > 0:
                # Update remaining leave days
                cursor.execute('''
                    SELECT employee_id, days_count FROM leave_requests WHERE id = ?
                ''', (request_id,))
                row = cursor.fetchone()
                if row:
                    cursor.execute('''
                        UPDATE employees SET
                            remaining_leave_days = remaining_leave_days - ?
                        WHERE id = ?
                    ''', (row['days_count'], row['employee_id']))

            return cursor.rowcount > 0

    # Notification operations
    def create_notification(self, notification: Notification) -> int:
        """Create notification"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO notifications (
                    employee_id, notification_type, title, message, due_date
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                notification.employee_id, notification.notification_type,
                notification.title, notification.message, notification.due_date
            ))
            return cursor.lastrowid

    def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM notifications 
                WHERE is_read = 0 
                ORDER BY due_date ASC
            ''')
            return [self._row_to_notification(row) for row in cursor.fetchall()]

    # Helper methods
    def _row_to_employee(self, row) -> Employee:
        """Convert database row to Employee object"""
        return Employee(
            id=row['id'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            pesel=row['pesel'],
            address=row['address'],
            phone=row['phone'],
            email=row['email'],
            position=row['position'],
            department=row['department'],
            hire_date=datetime.strptime(row['hire_date'], '%Y-%m-%d').date() if row['hire_date'] else None,
            contract_number=row['contract_number'],
            contract_type=ContractType(row['contract_type']),
            contract_end_date=datetime.strptime(row['contract_end_date'], '%Y-%m-%d').date() if row[
                'contract_end_date'] else None,
            annual_leave_days=row['annual_leave_days'],
            remaining_leave_days=row['remaining_leave_days'],
            work_mode=WorkMode(row['work_mode']),
            medical_exam_date=datetime.strptime(row['medical_exam_date'], '%Y-%m-%d').date() if row[
                'medical_exam_date'] else None,
            safety_training_date=datetime.strptime(row['safety_training_date'], '%Y-%m-%d').date() if row[
                'safety_training_date'] else None
        )

    def _row_to_time_entry(self, row) -> TimeEntry:
        """Convert database row to TimeEntry object"""
        return TimeEntry(
            id=row['id'],
            employee_id=row['employee_id'],
            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
            check_in=datetime.strptime(row['check_in'], '%Y-%m-%d %H:%M:%S') if row['check_in'] else None,
            check_out=datetime.strptime(row['check_out'], '%Y-%m-%d %H:%M:%S') if row['check_out'] else None,
            work_mode=WorkMode(row['work_mode']),
            notes=row['notes']
        )

    def _row_to_leave_request(self, row) -> LeaveRequest:
        """Convert database row to LeaveRequest object"""
        return LeaveRequest(
            id=row['id'],
            employee_id=row['employee_id'],
            leave_type=LeaveType(row['leave_type']),
            start_date=datetime.strptime(row['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(row['end_date'], '%Y-%m-%d').date(),
            days_count=row['days_count'],
            reason=row['reason'],
            status=row['status'],
            approved_by=row['approved_by'],
            approved_date=datetime.strptime(row['approved_date'], '%Y-%m-%d %H:%M:%S') if row['approved_date'] else None
        )

    def _row_to_notification(self, row) -> Notification:
        """Convert database row to Notification object"""
        return Notification(
            id=row['id'],
            employee_id=row['employee_id'],
            notification_type=row['notification_type'],
            title=row['title'],
            message=row['message'],
            due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date() if row['due_date'] else None,
            is_read=bool(row['is_read'])
        )