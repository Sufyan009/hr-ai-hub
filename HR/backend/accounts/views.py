from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework import viewsets, mixins, filters
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
from .models import JobPost
from .serializers import JobPostSerializer
from rest_framework.permissions import BasePermission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CandidateViewSet(viewsets.ModelViewSet):
    # type: ignore[attr-defined]
    queryset = Candidate.objects.all().order_by('-id')  # Default: newest first
    serializer_class = CandidateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = CandidateFilter  # Use the custom filter
    search_fields = [
        'first_name', 'last_name', 'email', 'phone_number',
        'job_title__name', 'city__name', 'source__name', 'communication_skills__name',
        'candidate_stage', 'notes'
    ]
    ordering_fields = [
        'id', 'first_name', 'last_name', 'email', 'candidate_stage',
        'years_of_experience', 'expected_salary', 'current_salary'
    ]
    ordering = ['-id']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrRecruiter()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        candidate = serializer.save()
        # Notify the user who created the candidate
        create_notification(self.request.user, f"Candidate {candidate.first_name} {candidate.last_name} was added.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = f"{instance.first_name} {instance.last_name}".strip()
        response = super().destroy(request, *args, **kwargs)
        create_notification(request.user, f"Candidate {name} was deleted.")
        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_stage = instance.candidate_stage
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        new_stage = serializer.instance.candidate_stage
        if old_stage != new_stage:
            name = f"{instance.first_name} {instance.last_name}".strip()
            create_notification(request.user, f"Candidate {name} stage changed to '{new_stage}'.")
        return Response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # type: ignore[attr-defined]
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metrics_view(request):
    from .models import JobPost  # Ensure JobPost is imported
    return Response({
        "total_candidates": Candidate.objects.count(),  # type: ignore[attr-defined]
        "hired": Candidate.objects.filter(candidate_stage__iexact='hired').count(),  # type: ignore[attr-defined]
        "rejected": Candidate.objects.filter(candidate_stage__iexact='rejected').count(),  # type: ignore[attr-defined]
        "active_positions": JobPost.objects.filter(status='open').count(),  # Added active positions
        # Add more metrics as needed
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activities_view(request):
    # Return the last 10 notifications for the user as recent activities
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    activities = [
        {
            "activity": n.message,
            "timestamp": n.created_at.isoformat(),
            "is_read": n.is_read
        }
        for n in notifications
    ]
    return Response(activities)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    try:
        print("Received data:", request.data)  # Log incoming data
        user_message = request.data.get('message', '')
        model = request.data.get('model', 'openai/gpt-3.5-turbo')
        prompt = request.data.get('prompt', 'You are a helpful HR assistant. Answer questions about candidates, hiring, and HR best practices.')
        extra_body = request.data.get('extra_body', {})
        if not user_message and not request.data.get('messages'):
            return Response({'error': 'No message provided.'}, status=400)
        api_url = 'https://openrouter.ai/api/v1/chat/completions'
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        if not api_key:
            return Response({'error': 'Openrouter API key not set.'}, status=500)
        payload = {
            "model": model,
            "messages": request.data.get('messages', [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ])
        }
        if isinstance(extra_body, dict):
            payload.update(extra_body)
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "Your Site Name"
        }
        print("Sending payload to OpenRouter:", payload)  # Log outgoing payload
        resp = requests.post(api_url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        reply = data['choices'][0]['message']['content']
        return Response({"response": reply})
    except Exception as e:
        import traceback
        print("Error in chat_view:", str(e))
        traceback.print_exc()
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
    # type: ignore[attr-defined]
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
            c.first_name, c.last_name, c.email, c.phone_number,
            str(c.job_title) if c.job_title else '',
            c.candidate_stage,
            c.current_salary, c.expected_salary, c.years_of_experience,
            str(c.communication_skills) if c.communication_skills else '',
            str(c.city) if c.city else '',
            str(c.source) if c.source else '',
            c.notes
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

class JobTitleViewSet(viewsets.ModelViewSet):
    # type: ignore[attr-defined]
    queryset = JobTitle.objects.all().order_by('name')
    serializer_class = JobTitleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrRecruiter()]
        return [IsAuthenticated()]

class CitySerializer(ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']
class CityViewSet(viewsets.ReadOnlyModelViewSet):
    # type: ignore[attr-defined]
    queryset = City.objects.all().order_by('name')
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class SourceSerializer(ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name']
class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    # type: ignore[attr-defined]
    queryset = Source.objects.all().order_by('name')
    serializer_class = SourceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class CommunicationSkillSerializer(ModelSerializer):
    class Meta:
        model = CommunicationSkill
        fields = ['id', 'name']
class CommunicationSkillViewSet(viewsets.ReadOnlyModelViewSet):
    # type: ignore[attr-defined]
    queryset = CommunicationSkill.objects.all().order_by('name')
    serializer_class = CommunicationSkillSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class IsAdminOrRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (getattr(request.user, 'role', None) in ['admin', 'recruiter'])

class JobPostViewSet(viewsets.ModelViewSet):
    # type: ignore[attr-defined]
    queryset = JobPost.objects.all().order_by('-created_at')
    serializer_class = JobPostSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'employment_type', 'department', 'location', 'job_title']
    search_fields = ['title', 'description', 'requirements', 'department', 'location', 'job_title__name']
    ordering_fields = ['created_at', 'title', 'salary_min', 'salary_max']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrRecruiter()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        job_post = serializer.save(posted_by=self.request.user)
        # Notify the user who created the job post
        create_notification(self.request.user, f"Job '{job_post.title}' was posted.")

class JobPostTitleChoices(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response([{'value': v, 'label': l} for v, l in JobPost.JOB_TITLES])

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_notifications_view(request):
    # type: ignore[attr-defined]
    unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    serializer = NotificationSerializer(unread, many=True)
    return Response(serializer.data)

UserModel = get_user_model()

class PasswordResetRequestView(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=400)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            # Do not reveal if user exists
            return Response({'message': 'If an account with that email exists, a reset link has been sent.'})
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"  # Adjust frontend URL as needed
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_url}',
            'no-reply@example.com',
            [user.email],
            fail_silently=True,
        )
        return Response({'message': 'If an account with that email exists, a reset link has been sent.'})

class PasswordResetConfirmView(APIView):
    permission_classes = []
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not (uidb64 and token and new_password):
            return Response({'error': 'Missing parameters.'}, status=400)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            return Response({'error': 'Invalid link.'}, status=400)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password has been reset successfully.'})

class EmailVerificationRequestView(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required.'}, status=400)
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response({'message': 'If an account with that email exists, a verification link has been sent.'})
        if user.is_active:
            return Response({'message': 'Account is already active.'})
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = f"http://localhost:3000/verify-email/{uid}/{token}/"  # Adjust frontend URL as needed
        send_mail(
            'Verify Your Email',
            f'Click the link to verify your email: {verify_url}',
            'no-reply@example.com',
            [user.email],
            fail_silently=True,
        )
        return Response({'message': 'If an account with that email exists, a verification link has been sent.'})

class EmailVerificationConfirmView(APIView):
    permission_classes = []
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            return Response({'error': 'Invalid link.'}, status=400)
        if user.is_active:
            return Response({'message': 'Account already verified.'})
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=400)
        user.is_active = True
        user.save()
        return Response({'message': 'Email verified successfully.'}) 