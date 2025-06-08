from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note, Category
from .forms import NoteForm, UserRegisterForm, UserUpdateForm, ProfileImageForm
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import Note
from django.db.models import F, ExpressionWrapper, DurationField
# Create your views here.

from django.core.paginator import Paginator

@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category_id', '')
    notes = Note.objects.filter(owner=request.user)
    today = timezone.now().date()
    today_notes_exist = Note.objects.filter(owner=request.user, due_date=today).exists()
    overdue_count = notes.filter(due_date__lt=today).count()
    today_count = notes.filter(due_date=today).count()
    upcoming_count = notes.filter(due_date__gt=today).count()
    most_overdue_note = notes.filter(due_date__lt=today).order_by('due_date').first()
    days_overdue = (today - most_overdue_note.due_date).days if most_overdue_note else 0
    notes = notes.order_by('-is_pinned', 'due_date', '-updated_at')  # 🧠 pinned first, then latest
    

    if query:
        notes = notes.filter(
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query)
        )
    if category_id:
        notes = notes.filter(category_id=category_id)

    paginator = Paginator(notes.order_by('-updated_at'), 6)  # Show 6 notes per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('notes_app/_note_list.html', {'page_obj': page_obj})
        return JsonResponse({'html': html})
    
    note_count = notes.count()
    recent_notes = notes.order_by('-updated_at')[:5]
    category_stats = Category.objects.filter(note__owner=request.user).annotate(total=models.Count('note'))


    return render(request, 'notes_app/dashboard.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'note_count': note_count,
        'recent_notes': recent_notes,
        'category_stats': category_stats,
        'overdue_count': overdue_count,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'days_overdue': days_overdue,
        'today_notes_exist': today_notes_exist,
        
    })
@login_required
def todays_notes(request):
    today = timezone.now().date()# ⬅️ Convert to just the date
    notes = Note.objects.filter(owner=request.user, due_date=today)
    return render(request, 'notes_app/todays_notes.html', {'notes': notes})




@login_required
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST or None, user=request.user)
        if form.is_valid():
            note = form.save(commit=False)  # don’t save yet
            note.owner = request.user       # assign the current user
            note.save()
            messages.success(request, "Note added successfully!")
            return redirect('dashboard')
    else:
        form = NoteForm()

    return render(request, 'notes_app/add_note.html', {'form': form})


@login_required
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated successfully.")
            return redirect('dashboard')
    else:
        form = NoteForm(instance=note)

    return render(request, 'notes_app/edit_note.html', {'form': form, 'note': note})


@login_required
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)

    if request.method == 'POST':
        note.delete()
        messages.success(request, "Note deleted successfully.")
        return redirect('dashboard')

    return render(request, 'notes_app/delete_note.html', {'note': note})



@login_required
def search_notes(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category_id', '')
    notes = Note.objects.filter(owner=request.user)

    if query:
        notes = notes.filter(
            models.Q(title__icontains=query) |
            models.Q(content__icontains=query)
        )

    if category_id:
        notes = notes.filter(category_id=category_id)

    html = render_to_string('notes_app/_note_list.html', {'notes': notes})
    return JsonResponse({'html': html})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after signup
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'notes_app/register.html', {'form': form})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        if 'update_info' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            image_form = ProfileImageForm(request.POST, request.FILES, instance=request.user.profile)
            if user_form.is_valid() and image_form.is_valid():
                user_form.save()
                image_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile_edit')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Password changed successfully.")
                return redirect('profile_edit')
    else:
        user_form = UserUpdateForm(instance=request.user)
        image_form = ProfileImageForm(instance=request.user.profile)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'notes_app/profile_edit.html', {
        'user_form': user_form,
        'image_form': image_form,
        'password_form': password_form
    })

def public_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'notes_app/public_profile.html', {'profile_user': user})


@login_required
def toggle_pin(request, note_id):
    note = get_object_or_404(Note, id=note_id, owner=request.user)
    note.is_pinned = not note.is_pinned
    note.save()
    return redirect('dashboard')


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



@login_required
def category_list(request):
    categories = Category.objects.filter(owner=request.user)

    if request.method == "POST":
        new_name = request.POST.get('new_category')
        if new_name:
            Category.objects.get_or_create(name=new_name, owner=request.user)
            return redirect('category_list')

    return render(request, 'notes_app/category_list.html', {
        'categories': categories,
    })


@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, owner=request.user)
    category.delete()
    return redirect('category_list')
