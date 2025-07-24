from rest_framework import serializers
from .models import User, Candidate, Notification, JobTitle, City, Source, CommunicationSkill, JobPost, ChatSession, ChatMessage, Note
from django.contrib.auth import get_user_model

User = get_user_model()

class JobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTitle
        fields = ['id', 'name']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name']

class CommunicationSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationSkill
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'avatar', 'title', 'company']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'candidate', 'content', 'created_at']
        read_only_fields = ['id', 'created_at', 'candidate']

class CandidateSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True, source='notes_set')
    job_title = serializers.PrimaryKeyRelatedField(queryset=JobTitle.objects.all(), write_only=True)
    job_title_detail = JobTitleSerializer(source='job_title', read_only=True)
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True)
    city_detail = CitySerializer(source='city', read_only=True)
    source = serializers.PrimaryKeyRelatedField(queryset=Source.objects.all(), write_only=True)
    source_detail = SourceSerializer(source='source', read_only=True)
    communication_skills = serializers.PrimaryKeyRelatedField(queryset=CommunicationSkill.objects.all(), write_only=True)
    communication_skills_detail = CommunicationSkillSerializer(source='communication_skills', read_only=True)

    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ['notes']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

class JobPostSerializer(serializers.ModelSerializer):
    job_title = serializers.PrimaryKeyRelatedField(queryset=JobTitle.objects.all(), allow_null=True, required=False)
    job_title_detail = JobTitleSerializer(source='job_title', read_only=True)
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)
    class Meta:
        model = JobPost
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'session', 'role', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'session_name', 'role', 'model', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages', 'user'] 