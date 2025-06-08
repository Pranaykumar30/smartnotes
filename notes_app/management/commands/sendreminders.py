from django.core.management.base import BaseCommand
from notes_app.views import send_due_date_reminders

class Command(BaseCommand):
    help = "Send daily reminders for due notes"

    def handle(self, *args, **kwargs):
        send_due_date_reminders()
        self.stdout.write("Reminders sent successfully!")
