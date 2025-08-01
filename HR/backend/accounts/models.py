from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
import json

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

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['candidate_stage']),
            models.Index(fields=['job_title', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.strip().capitalize()
        if self.last_name:
            self.last_name = self.last_name.strip().capitalize()
        super().save(*args, **kwargs)

    def __str__(self):
        job_title_str = str(self.job_title) if self.job_title else ''
        return f"{self.first_name} {self.last_name} - {job_title_str}"

    def get_schema_org_data(self):
        """
        Generate Schema.org structured data for the candidate.
        Uses Person schema with additional job application context.
        """
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": f"{self.first_name} {self.last_name}",
            "email": self.email,
            "telephone": self.phone_number,
            "jobTitle": str(self.job_title) if self.job_title else None,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": str(self.city) if self.city else None
            },
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "candidate_stage",
                    "value": self.candidate_stage
                },
                {
                    "@type": "PropertyValue",
                    "name": "current_salary",
                    "value": str(self.current_salary)
                },
                {
                    "@type": "PropertyValue",
                    "name": "expected_salary",
                    "value": str(self.expected_salary)
                },
                {
                    "@type": "PropertyValue",
                    "name": "years_of_experience",
                    "value": str(self.years_of_experience)
                },
                {
                    "@type": "PropertyValue",
                    "name": "communication_skills",
                    "value": str(self.communication_skills) if self.communication_skills else None
                },
                {
                    "@type": "PropertyValue",
                    "name": "source",
                    "value": str(self.source) if self.source else None
                },
                {
                    "@type": "PropertyValue",
                    "name": "created_at",
                    "value": self.created_at.isoformat()
                }
            ]
        }

        # Add job application context
        schema_data["additionalProperty"].append({
            "@type": "PropertyValue",
            "name": "application_status",
            "value": self.candidate_stage
        })

        return schema_data

    def get_schema_org_json(self):
        """Return Schema.org data as JSON string"""
        return json.dumps(self.get_schema_org_data(), indent=2)

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:30]}..."

def create_notification(user, message):
    return Notification.objects.create(user=user, message=message)

class JobTitle(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class Source(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class CommunicationSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

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

    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['location']),
            models.Index(fields=['posted_by', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_schema_org_data(self):
        """
        Generate Schema.org structured data for the job posting.
        Uses JobPosting schema.
        """
        schema_data = {
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": self.title,
            "description": self.description,
            "datePosted": self.created_at.isoformat(),
            "employmentType": self.get_employment_type_display(),
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": self.location
                }
            },
            "hiringOrganization": {
                "@type": "Organization",
                "name": "HR Assistant Pro"
            },
            "department": self.department,
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "status",
                    "value": self.status
                },
                {
                    "@type": "PropertyValue",
                    "name": "job_title",
                    "value": str(self.job_title) if self.job_title else None
                },
                {
                    "@type": "PropertyValue",
                    "name": "posted_by",
                    "value": self.posted_by.username if self.posted_by else None
                }
            ]
        }

        # Add salary information if available
        if self.salary_min or self.salary_max:
            schema_data["baseSalary"] = {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "value": {
                    "@type": "QuantitativeValue",
                    "minValue": float(self.salary_min) if self.salary_min else None,
                    "maxValue": float(self.salary_max) if self.salary_max else None
                }
            }

        # Add requirements if available
        if self.requirements:
            schema_data["qualifications"] = self.requirements

        return schema_data

    def get_schema_org_json(self):
        """Return Schema.org data as JSON string"""
        return json.dumps(self.get_schema_org_data(), indent=2)

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    session_name = models.CharField(max_length=100, blank=True, null=True)  # Optional, for user to name sessions
    role = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'admin', 'hr', 'manager', etc.
    model = models.CharField(max_length=100, blank=True, null=True)  # Selected AI model for this session
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Track active sessions
    message_count = models.IntegerField(default=0)  # Cache message count for performance

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"Session {self.id} for {self.user} ({self.role or 'no role'})"

    def update_message_count(self):
        """Update the cached message count"""
        self.message_count = self.messages.count()
        self.save(update_fields=['message_count'])

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # 'user', 'assistant', 'system'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # Add compression and caching fields
    content_compressed = models.BinaryField(null=True, blank=True)  # For compressed content
    is_compressed = models.BooleanField(default=False)
    content_hash = models.CharField(max_length=64, null=True, blank=True)  # For deduplication

    class Meta:
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['session', 'role']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['content_hash']),
        ]
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.role} @ {self.timestamp}: {self.content[:30]}..."

    def save(self, *args, **kwargs):
        # Update session message count when message is saved
        super().save(*args, **kwargs)
        self.session.update_message_count()

    def delete(self, *args, **kwargs):
        # Update session message count when message is deleted
        super().delete(*args, **kwargs)
        self.session.update_message_count()

class Note(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='notes_set')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['candidate', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.candidate} at {self.created_at:%Y-%m-%d %H:%M}: {self.content[:30]}..." 