from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileView, CandidateViewSet, metrics_view, recent_activities_view, chat_view, openrouter_models_view, NotificationViewSet, UserSettingsView, export_candidates_csv, JobTitleViewSet, CityViewSet, SourceViewSet, CommunicationSkillViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'jobtitles', JobTitleViewSet, basename='jobtitle')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'sources', SourceViewSet, basename='source')
router.register(r'communicationskills', CommunicationSkillViewSet, basename='communicationskill')

urlpatterns = [
    path('', include(router.urls)),
    path('user-settings/', UserSettingsView.as_view(), name='user-settings'),
]
urlpatterns += [
    path('metrics/', metrics_view, name='metrics'),
    path('recent-activities/', recent_activities_view, name='recent-activities'),
    path('chat/', chat_view, name='chat'),
    path('openrouter-models/', openrouter_models_view, name='openrouter-models'),
    path('candidates/export/csv/', export_candidates_csv, name='export-candidates-csv'),
] 