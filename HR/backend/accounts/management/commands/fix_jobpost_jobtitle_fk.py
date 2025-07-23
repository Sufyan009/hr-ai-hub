from django.core.management.base import BaseCommand
from accounts.models import JobPost, JobTitle
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix JobPost.job_title values that do not match any JobTitle ID.'

    def handle(self, *args, **options):
        with transaction.atomic():
            nullified = 0
            for jp in JobPost.objects.all():
                jt_val = jp.job_title
                if jt_val is None or jt_val == '':
                    jp.job_title = None
                    jp.save(update_fields=['job_title'])
                    nullified += 1
                    continue
                try:
                    jt_id = int(jt_val)
                    if not JobTitle.objects.filter(id=jt_id).exists():
                        jp.job_title = None
                        jp.save(update_fields=['job_title'])
                        nullified += 1
                except ValueError:
                    jp.job_title = None
                    jp.save(update_fields=['job_title'])
                    nullified += 1
            self.stdout.write(self.style.SUCCESS(f'Nullified {nullified} JobPost.job_title values that did not match any JobTitle ID or were empty.')) 