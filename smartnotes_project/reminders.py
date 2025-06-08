from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Note

def send_due_date_reminders():
    today = timezone.now().date()

    for user in User.objects.all():
        notes_due = Note.objects.filter(
            owner=user,
            due_date__lte=today,
            due_date__isnull=False
        ).order_by('due_date')

        if notes_due.exists():
            message = "📝 Here are your due/overdue notes:\n\n"
            for note in notes_due:
                status = "OVERDUE" if note.due_date < today else "DUE TODAY"
                message += f"• {note.title} ({status}) - {note.due_date}\n"

            send_mail(
                subject="📅 Daily Reminder: Your Notes",
                message=message,
                from_email=None,
                recipient_list=[user.email],
            )
