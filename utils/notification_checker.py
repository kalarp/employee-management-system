"""
Notification checker for Employee Management System
"""

import threading
from datetime import date, timedelta
from typing import Callable

from storage.database import Database
from models import Notification, Employee
from utils.logger import get_logger


class NotificationChecker:
    """Background notification checker"""

    def __init__(self, database: Database, callback: Callable[[int], None],
                 check_interval: int = 3600):
        """
        Initialize notification checker

        Args:
            database: Database instance
            callback: Callback function to call with notification count
            check_interval: Check interval in seconds
        """
        self.db = database
        self.callback = callback
        self.check_interval = check_interval
        self.logger = get_logger()
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        """Start notification checker"""
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            self.logger.info("Notification checker started")

    def stop(self):
        """Stop notification checker"""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.logger.info("Notification checker stopped")

    def _run(self):
        """Run notification checker"""
        while not self._stop_event.is_set():
            try:
                self.check_notifications()
            except Exception as e:
                self.logger.error(f"Error checking notifications: {e}")

            # Wait for next check
            self._stop_event.wait(self.check_interval)

    def check_notifications(self):
        """Check for and create notifications"""
        self.logger.debug("Checking notifications...")

        # Check contract expiry
        self._check_contract_expiry()

        # Check medical exams
        self._check_medical_exams()

        # Check safety training
        self._check_safety_training()

        # Get pending notification count
        notifications = self.db.get_pending_notifications()
        count = len(notifications)

        # Call callback with count
        if self.callback:
            self.callback(count)

        self.logger.debug(f"Found {count} pending notifications")

    def _check_contract_expiry(self):
        """Check for expiring contracts"""
        warning_days = 30
        check_date = date.today() + timedelta(days=warning_days)

        employees = self.db.get_all_employees()
        for employee in employees:
            if employee.contract_end_date:
                days_until_expiry = (employee.contract_end_date - date.today()).days

                if 0 < days_until_expiry <= warning_days:
                    # Check if notification already exists
                    existing = self._notification_exists(
                        employee.id,
                        "Contract Expiry",
                        employee.contract_end_date
                    )

                    if not existing:
                        notification = Notification(
                            employee_id=employee.id,
                            notification_type="Contract Expiry",
                            title=f"Contract Expiring Soon - {employee.full_name}",
                            message=f"Contract for {employee.full_name} expires on {employee.contract_end_date.strftime('%Y-%m-%d')} ({days_until_expiry} days remaining)",
                            due_date=employee.contract_end_date
                        )
                        self.db.create_notification(notification)
                        self.logger.info(f"Created contract expiry notification for {employee.full_name}")

    def _check_medical_exams(self):
        """Check for due medical exams"""
        warning_days = 30

        employees = self.db.get_all_employees()
        for employee in employees:
            if employee.medical_exam_date:
                # Assume medical exams are valid for 1 year
                next_exam_date = employee.medical_exam_date.replace(year=employee.medical_exam_date.year + 1)
                days_until_due = (next_exam_date - date.today()).days

                if 0 < days_until_due <= warning_days:
                    existing = self._notification_exists(
                        employee.id,
                        "Medical Exam",
                        next_exam_date
                    )

                    if not existing:
                        notification = Notification(
                            employee_id=employee.id,
                            notification_type="Medical Exam",
                            title=f"Medical Exam Due - {employee.full_name}",
                            message=f"Medical exam for {employee.full_name} is due on {next_exam_date.strftime('%Y-%m-%d')} ({days_until_due} days remaining)",
                            due_date=next_exam_date
                        )
                        self.db.create_notification(notification)
                        self.logger.info(f"Created medical exam notification for {employee.full_name}")

    def _check_safety_training(self):
        """Check for due safety training"""
        warning_days = 30

        employees = self.db.get_all_employees()
        for employee in employees:
            if employee.safety_training_date:
                # Assume safety training is valid for 1 year
                next_training_date = employee.safety_training_date.replace(year=employee.safety_training_date.year + 1)
                days_until_due = (next_training_date - date.today()).days

                if 0 < days_until_due <= warning_days:
                    existing = self._notification_exists(
                        employee.id,
                        "Safety Training",
                        next_training_date
                    )

                    if not existing:
                        notification = Notification(
                            employee_id=employee.id,
                            notification_type="Safety Training",
                            title=f"Safety Training Due - {employee.full_name}",
                            message=f"Safety training for {employee.full_name} is due on {next_training_date.strftime('%Y-%m-%d')} ({days_until_due} days remaining)",
                            due_date=next_training_date
                        )
                        self.db.create_notification(notification)
                        self.logger.info(f"Created safety training notification for {employee.full_name}")

    def _notification_exists(self, employee_id: int, notification_type: str, due_date: date) -> bool:
        """Check if notification already exists"""
        notifications = self.db.get_pending_notifications()
        for notif in notifications:
            if (notif.employee_id == employee_id and
                    notif.notification_type == notification_type and
                    notif.due_date == due_date):
                return True
        return False