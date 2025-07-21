from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework import viewsets
from .models import Candidate
from .serializers import CandidateSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
import logging
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import create_notification
from rest_framework import status
from .models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import csv
from .models import JobTitle
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer
from .models import City, Source, CommunicationSkill
from .filters import CandidateFilter
from rest_framework.parsers import MultiPartParser, FormParser

logger = logging.getLogger(__name__)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all().order_by('id')  # Add default ordering
    serializer_class = CandidateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CandidateFilter  # Use the custom filter

    def perform_create(self, serializer):
        candidate = serializer.save()
        # Notify the user who created the candidate
        create_notification(self.request.user, f"Candidate {candidate.first_name} {candidate.last_name} was added.")

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metrics_view(request):
    return Response({
        "total_candidates": Candidate.objects.count(),  # type: ignore[attr-defined]
        "hired": Candidate.objects.filter(candidate_stage__iexact='hired').count(),  # type: ignore[attr-defined]
        "rejected": Candidate.objects.filter(candidate_stage__iexact='rejected').count(),  # type: ignore[attr-defined]
        # Add more metrics as needed
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activities_view(request):
    return Response([
        # Example dummy activities
        {"activity": "Candidate John Doe was hired.", "timestamp": "2025-07-18T12:00:00Z"},
        {"activity": "Candidate Jane Smith was rejected.", "timestamp": "2025-07-17T15:30:00Z"},
    ])

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    user_message = request.data.get('message', '')
    model = request.data.get('model', 'openai/gpt-3.5-turbo')
    prompt = request.data.get('prompt', 'You are a helpful HR assistant. Answer questions about candidates, hiring, and HR best practices.')
    extra_body = request.data.get('extra_body', {})
    if not user_message:
        return Response({'error': 'No message provided.'}, status=400)
    api_url = 'https://openrouter.ai/api/v1/chat/completions'
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
    if not api_key:
        return Response({'error': 'Openrouter API key not set.'}, status=500)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
    }
    if isinstance(extra_body, dict):
        payload.update(extra_body)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-site.com",  # Optional: replace with your site
        "X-Title": "Your Site Name"               # Optional: replace with your site name
    }
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        reply = data['choices'][0]['message']['content']
        return Response({"response": reply})
    except Exception as e:
        logger.error(f"Error calling Openrouter: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def openrouter_models_view(request):
    api_url = 'https://openrouter.ai/api/v1/models'
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
    if not api_key:
        return Response({'error': 'Openrouter API key not set.'}, status=500)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_candidates_csv(request):
    queryset = Candidate.objects.all()
    # Apply filters
    for field in ['job_title', 'city', 'source', 'communication_skills', 'candidate_stage']:
        value = request.GET.get(field)
        if value:
            queryset = queryset.filter(**{field: value})
    for field in ['years_of_experience', 'current_salary', 'expected_salary']:
        min_val = request.GET.get(f'{field}__gte')
        max_val = request.GET.get(f'{field}__lte')
        if min_val:
            queryset = queryset.filter(**{f'{field}__gte': min_val})
        if max_val:
            queryset = queryset.filter(**{f'{field}__lte': max_val})
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="candidates.csv"'
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Job Title', 'Stage', 'Current Salary', 'Expected Salary', 'Experience', 'Skills', 'City', 'Source', 'Notes'])
    for c in queryset:
        writer.writerow([
            c.first_name, c.last_name, c.email, c.phone_number, c.job_title, c.candidate_stage,
            c.current_salary, c.expected_salary, c.years_of_experience, c.communication_skills,
            c.city, c.source, c.notes
        ])
    return response

class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobTitleSerializer(ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']

class JobTitleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobTitle.objects.all().order_by('name')
    serializer_class = JobTitleSerializer
    permission_classes = []
    pagination_class = None

class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']
class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all().order_by('name')
    serializer_class = CitySerializer
    permission_classes = []
    pagination_class = None

class SourceSerializer(ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name']
class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all().order_by('name')
    serializer_class = SourceSerializer
    permission_classes = []
    pagination_class = None

class CommunicationSkillSerializer(ModelSerializer):
    class Meta:
        model = CommunicationSkill
        fields = ['id', 'name']
class CommunicationSkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationSkill.objects.all().order_by('name')
    serializer_class = CommunicationSkillSerializer
    permission_classes = []
    pagination_class = None 