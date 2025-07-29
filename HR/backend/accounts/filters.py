import django_filters
from .models import Candidate

class CandidateFilter(django_filters.FilterSet):
    job_title = django_filters.CharFilter(field_name='job_title__name', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='city__name', lookup_expr='icontains')
    source = django_filters.CharFilter(field_name='source__name', lookup_expr='icontains')
    communication_skills = django_filters.CharFilter(field_name='communication_skills__name', lookup_expr='icontains')
    candidate_stage = django_filters.CharFilter(field_name='candidate_stage', lookup_expr='iexact')
    email = django_filters.CharFilter(field_name='email', lookup_expr='iexact')

    class Meta:
        model = Candidate
        fields = ['job_title', 'city', 'source', 'communication_skills', 'candidate_stage', 'email'] 