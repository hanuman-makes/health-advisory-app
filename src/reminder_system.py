"""Medicine reminder system with SQLite storage."""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class MedicineReminderSystem:
    """Handle medicine reminders with persistent storage."""

    def __init__(self, db_path="data/reminders.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()

    def get_display_time(self, time_24hr):
        """Converts internal 24hr time (14:30) to AM/PM (02:30 PM) for the elderly."""
        from datetime import datetime
        try:
            return datetime.strptime(time_24hr, "%H:%M").strftime("%I:%M %p")
        except:
            return time_24hr

    def init_database(self):
        """Initialize SQLite database with reminders table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine_name TEXT NOT NULL,
                dosage TEXT,
                time TEXT NOT NULL,
                frequency TEXT DEFAULT 'daily',
                days TEXT,  -- JSON array of days (0=Monday, 6=Sunday)
                start_date TEXT,
                end_date TEXT,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT DEFAULT 'default'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminder_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_id INTEGER,
                scheduled_time TEXT,
                taken_time TEXT,
                status TEXT,  -- 'taken', 'missed', 'snoozed'
                FOREIGN KEY (reminder_id) REFERENCES reminders (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_reminder(self, medicine_name: str, time: str, dosage: str = "",
                     frequency: str = "daily", days: List[str] = None,
                     start_date: str = None, end_date: str = None,
                     notes: str = "") -> Dict:
        """Add a new medicine reminder."""

        if days is None:
            days = ["0", "1", "2", "3", "4", "5", "6"]  # All days

        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reminders
            (medicine_name, dosage, time, frequency, days, start_date, end_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (medicine_name, dosage, time, frequency, json.dumps(days),
              start_date, end_date, notes))

        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            'id': reminder_id,
            'medicine_name': medicine_name,
            'time': time,
            'status': 'success'
        }

    def get_reminders(self, user_id: str = 'default') -> List[Dict]:
        """Get all active reminders for a user."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, medicine_name, dosage, time, frequency, days,
                   start_date, end_date, notes, is_active
            FROM reminders
            WHERE user_id = ? AND is_active = 1
            ORDER BY time
        ''', (user_id,))

        reminders = cursor.fetchall()
        conn.close()

        result = []
        for row in reminders:
            result.append({
                'id': row[0],
                'medicine_name': row[1],
                'dosage': row[2],
                'time': row[3],
                'frequency': row[4],
                'days': json.loads(row[5]) if row[5] else [],
                'start_date': row[6],
                'end_date': row[7],
                'notes': row[8],
                'is_active': bool(row[9])
            })

        return result

    def get_upcoming_reminders(self, user_id: str = 'default') -> List[Dict]:
        """Get reminders due today."""

        today = datetime.now()
        current_day = str(today.weekday())  # 0=Monday, 6=Sunday
        current_time = today.strftime("%H:%M")

        all_reminders = self.get_reminders(user_id)
        upcoming = []

        for reminder in all_reminders:
            days = reminder.get('days', [])
            if current_day in days:
                reminder_time = datetime.strptime(reminder['time'], "%H:%M")
                now = datetime.strptime(current_time, "%H:%M")

                # Check if reminder is upcoming (within next 2 hours) or past
                time_diff = (reminder_time - now).total_seconds() / 3600

                reminder['time_until'] = time_diff
                reminder['is_overdue'] = time_diff < 0

                upcoming.append(reminder)

        # Sort by time
        upcoming.sort(key=lambda x: x['time'])
        return upcoming

    def update_reminder(self, reminder_id: int, **kwargs) -> Dict:
        """Update an existing reminder."""

        allowed_fields = ['medicine_name', 'dosage', 'time', 'frequency',
                         'days', 'start_date', 'end_date', 'notes', 'is_active']

        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return {'status': 'error', 'message': 'No valid fields to update'}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [reminder_id]

        cursor.execute(f'''
            UPDATE reminders SET {set_clause} WHERE id = ?
        ''', values)

        conn.commit()
        conn.close()

        return {'status': 'success', 'id': reminder_id}

    def delete_reminder(self, reminder_id: int) -> Dict:
        """Delete (deactivate) a reminder."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE reminders SET is_active = 0 WHERE id = ?
        ''', (reminder_id,))

        conn.commit()
        conn.close()

        return {'status': 'success', 'id': reminder_id}

    def mark_as_taken(self, reminder_id: int) -> Dict:
        """Mark a medicine as taken."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reminder_logs (reminder_id, scheduled_time, taken_time, status)
            VALUES (?, ?, ?, ?)
        ''', (reminder_id, datetime.now().isoformat(),
              datetime.now().isoformat(), 'taken'))

        conn.commit()
        conn.close()

        return {'status': 'success', 'message': 'Medicine marked as taken'}

    def get_statistics(self, user_id: str = 'default') -> Dict:
        """Get adherence statistics."""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total reminders
        cursor.execute('''
            SELECT COUNT(*) FROM reminders WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        total_reminders = cursor.fetchone()[0]

        # Total taken
        cursor.execute('''
            SELECT COUNT(*) FROM reminder_logs
            WHERE status = 'taken' AND reminder_id IN (
                SELECT id FROM reminders WHERE user_id = ?
            )
        ''', (user_id,))
        total_taken = cursor.fetchone()[0]

        # Total missed
        cursor.execute('''
            SELECT COUNT(*) FROM reminder_logs
            WHERE status = 'missed' AND reminder_id IN (
                SELECT id FROM reminders WHERE user_id = ?
            )
        ''', (user_id,))
        total_missed = cursor.fetchone()[0]

        conn.close()

        return {
            'total_reminders': total_reminders,
            'total_taken': total_taken,
            'total_missed': total_missed,
            'adherence_rate': (total_taken / (total_taken + total_missed) * 100)
                              if (total_taken + total_missed) > 0 else 0
        }
