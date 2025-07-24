from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username

class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    job_title = models.ForeignKey('JobTitle', on_delete=models.SET_NULL, null=True, blank=True)
    candidate_stage = models.CharField(max_length=100)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2)
    years_of_experience = models.FloatField()
    communication_skills = models.ForeignKey('CommunicationSkill', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True)
    source = models.ForeignKey('Source', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.strip().capitalize()
        if self.last_name:
            self.last_name = self.last_name.strip().capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        job_title_str = str(self.job_title) if self.job_title else ''
        return f"{self.first_name} {self.last_name} - {job_title_str}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else ''
        msg = self.message[:30] + ('...' if len(self.message) > 30 else '')
        return f"{user_str}: {msg}"

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)

class JobTitle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class CommunicationSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class JobPost(models.Model):
    job_title = models.ForeignKey('JobTitle', on_delete=models.SET_NULL, null=True, blank=True, help_text='Job title for this posting')
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full_time')
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    requirements = models.TextField(blank=True)
    posted_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='job_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})" 

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    session_name = models.CharField(max_length=100, blank=True, null=True)  # Optional, for user to name sessions
    role = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'admin', 'hr', 'manager', etc.
    model = models.CharField(max_length=100, blank=True, null=True)  # Selected AI model for this session
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optionally: is_active, etc.

    def __str__(self):
        return f"Session {self.id} for {self.user} ({self.role or 'no role'})"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # 'user', 'assistant', 'system'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} @ {self.timestamp}: {self.content[:30]}..." 

class Note(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='notes_set')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.candidate} at {self.created_at:%Y-%m-%d %H:%M}: {self.content[:30]}..." 