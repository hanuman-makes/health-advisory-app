import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from reminder_system import MedicineReminderSystem


def test_medicine_reminder_lifecycle(tmp_path):
    db_path = tmp_path / 'test_reminders.db'
    reminder_system = MedicineReminderSystem(str(db_path))

    reminder = reminder_system.add_reminder(
        medicine_name='Paracetamol',
        time='08:30',
        dosage='500mg',
        notes='After breakfast'
    )

    assert reminder['status'] == 'success'
    reminders = reminder_system.get_reminders()
    assert len(reminders) == 1
    assert reminders[0]['medicine_name'] == 'Paracetamol'
    assert reminders[0]['time'] == '08:30'

    update = reminder_system.update_reminder(reminder['id'], time='09:00')
    assert update['status'] == 'success'
    reminders = reminder_system.get_reminders()
    assert reminders[0]['time'] == '09:00'

    mark = reminder_system.mark_as_taken(reminder['id'])
    assert mark['status'] == 'success'

    stats = reminder_system.get_statistics()
    assert stats['total_reminders'] == 1
    assert stats['total_taken'] >= 1
    assert stats['adherence_rate'] >= 0

    delete = reminder_system.delete_reminder(reminder['id'])
    assert delete['status'] == 'success'
    assert reminder_system.get_reminders() == []


def test_display_time_conversion(tmp_path):
    db_path = tmp_path / 'temp_reminders.db'
    reminder_system = MedicineReminderSystem(str(db_path))
    assert reminder_system.get_display_time('14:30') == '02:30 PM'
