from rest_framework import serializers
from .models import User, Candidate, Notification, JobTitle, City, Source, CommunicationSkill

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

class CandidateSerializer(serializers.ModelSerializer):
    job_title = JobTitleSerializer()
    city = CitySerializer()
    source = SourceSerializer()
    communication_skills = CommunicationSkillSerializer()

    class Meta:
        model = Candidate
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at'] 