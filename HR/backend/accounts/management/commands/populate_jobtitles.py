from django.core.management.base import BaseCommand
from accounts.models import JobTitle

JOB_TITLES = [
    'Power BI', 'Data Engineer (Java Centric)', 'Fast Students', 'Python Developer', 'Contractor',
    'Jr. Azure Data Engineer', 'Head of AI', 'Sr. Drupal Developer', 'Unity Game Developer',
    'Softskill Trainer', 'Coordinator', 'Admin Assistant', 'Jr. Net Software Engineer', 'Trainer',
    'Functional Consultant', 'Network Engineer', 'Sales&Marketing', 'Jr SQ Engineer', 'Data Analyst',
    'Dynamics BC', 'Business Analyst', 'Jr. NET Developer', 'Intern - Data Analyst', 'Java Developer',
    'IT Recruiter', 'Unity 3D Developer', 'Chief Operating Officer', 'Jira Administrator',
    'Oracle Technical Consultants', 'Data Analyst', 'Azure data Engineer', 'Azure Data Engineer',
    'Data Engineer', 'Executive Assistant', 'Sr. Project Coordinator', 'UI/UX Designer',
    'Junior Project Coordinator', 'Help Desk Specialist', 'AWS Data Engineer', 'Data Engineer',
    'Finance Executive', 'React Native', 'React Js', 'Azure cloud infrastructure', 'Incubator',
    'Cold Calling Specialist', 'Product Owner', 'QA Manual', 'Content Writer - HN', 'QA Automation',
    'BD', 'Graphic Designer', 'Lead Generation - HN Team', 'Programming Mentor', 'Shopify Developer',
    'ETL Consultants', 'Jr. React JS', 'Marketing Interns', 'BD Interns', 'BDE', 'HR', 'Admin Officer',
    'Marketing Team Lead', 'Accounts Officer', 'Flutter Developer', 'Android Developer', 'Wordpress',
    'Jr. ASO', 'Research Assistant', 'SEO', 'Content Writer', 'Dynamics AX', 'Angular Developer',
    'Devops', 'Mern Stack', 'Videographer', 'IOS Developer', 'Sharepoint Developer', 'Mobile App Developer',
    'Sales Force', 'Dynamics 365 FO', 'Python', 'HR Internal', 'Data Scientist', 'ASO Marketing Specialist',
    'ML/AI Engineer', 'Social Media Specialist', 'Sr. Software Engineer', 'Software Engineer', 'Office Boy',
    'HR Generalist', 'Full Stack Developer', 'Jr. BDE', 'Sales Representative', 'Cold Caller / SDR',
    'QA Test Engineer', 'Sr. ReactJS Developer', 'Sr. QA Engineer', 'Trainee', 'Associate Software Engineer',
    'Lead Gen & BD Specialist', 'Brand Strategist'
]

class Command(BaseCommand):
    help = 'Populate JobTitle model with a list of job titles.'

    def handle(self, *args, **kwargs):
        for title in JOB_TITLES:
            JobTitle.objects.get_or_create(name=title)
        self.stdout.write(self.style.SUCCESS('Job titles populated successfully.')) 