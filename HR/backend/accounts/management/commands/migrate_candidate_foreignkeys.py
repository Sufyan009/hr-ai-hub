from django.core.management.base import BaseCommand
from accounts.models import Candidate, JobTitle, City, Source, CommunicationSkill

class Command(BaseCommand):
    help = 'Migrate Candidate string fields to ForeignKeys for job_title, city, source, and communication_skills.'

    def handle(self, *args, **kwargs):
        updated = 0
        for candidate in Candidate.objects.all():
            # Job Title
            if isinstance(candidate.job_title, str):
                jt = JobTitle.objects.filter(name=candidate.job_title).first()
                candidate.job_title = jt
            # City
            if isinstance(candidate.city, str):
                city = City.objects.filter(name=candidate.city).first()
                candidate.city = city
            # Source
            if isinstance(candidate.source, str):
                source = Source.objects.filter(name=candidate.source).first()
                candidate.source = source
            # Communication Skills
            if isinstance(candidate.communication_skills, str):
                skill = CommunicationSkill.objects.filter(name=candidate.communication_skills).first()
                candidate.communication_skills = skill
            candidate.save()
            updated += 1
        self.stdout.write(self.style.SUCCESS(f'Migrated {updated} candidates to use ForeignKeys.')) 