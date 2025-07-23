import pandas as pd
from accounts.models import Candidate, JobTitle, City, Source, CommunicationSkill
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import candidates from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='candidates.xlsx', help='Path to Excel file')

    def handle(self, *args, **options):
        file_path = options['file']
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            if not Candidate.objects.filter(email=row['Email']).exists():
                # Get or create related objects
                job_title, _ = JobTitle.objects.get_or_create(name=row['Job_Title'])
                city, _ = City.objects.get_or_create(name=row['City'])
                source, _ = Source.objects.get_or_create(name=row['Source'])
                comm_skills, _ = CommunicationSkill.objects.get_or_create(name=row['Communication_Skills'])

                Candidate.objects.create(
                    first_name=row['First_Name'],
                    last_name=row['Last_Name'],
                    email=row['Email'],
                    phone_number=row['Phone_Number'],
                    job_title=job_title,
                    candidate_stage=row['Candidate_Stage'],
                    current_salary=row['Current_Salary'],
                    expected_salary=row['Expected_Salary'],
                    years_of_experience=row['Years_Of_Experience'],
                    communication_skills=comm_skills,
                    city=city,
                    source=source,
                    notes=row.get('Source', '')
                )
        print('Import complete!')
