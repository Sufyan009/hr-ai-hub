from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileView, CandidateViewSet, metrics_view, recent_activities_view, chat_view, openrouter_models_view, NotificationViewSet, UserSettingsView, export_candidates_csv, JobTitleViewSet, CityViewSet, SourceViewSet, CommunicationSkillViewSet, unread_notifications_view, JobPostViewSet, JobPostTitleChoices, PasswordResetRequestView, PasswordResetConfirmView, EmailVerificationRequestView, EmailVerificationConfirmView, candidate_metrics_view, ChatSessionViewSet, ChatMessageViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'candidates', CandidateViewSet, basename='candidate')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'jobtitles', JobTitleViewSet, basename='jobtitle')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'sources', SourceViewSet, basename='source')
router.register(r'communicationskills', CommunicationSkillViewSet, basename='communicationskill')
router.register(r'jobposts', JobPostViewSet, basename='jobpost')
router.register(r'chatsessions', ChatSessionViewSet, basename='chatsession')
router.register(r'chatmessages', ChatMessageViewSet, basename='chatmessage')
router.register(r'notes', NoteViewSet)

urlpatterns = [
    path('notifications/unread/', unread_notifications_view, name='unread-notifications'),
    path('', include(router.urls)),
    path('user-settings/', UserSettingsView.as_view(), name='user-settings'),
]
urlpatterns += [
    path('metrics/', metrics_view, name='metrics'),
    path('recent-activities/', recent_activities_view, name='recent-activities'),
    path('chat/', chat_view, name='chat'),
    path('openrouter-models/', openrouter_models_view, name='openrouter-models'),
    path('candidates/export/csv/', export_candidates_csv, name='export-candidates-csv'),
    path('candidates/metrics/', candidate_metrics_view, name='candidate-metrics'),
    path('jobposts/job-title-choices/', JobPostTitleChoices.as_view(), name='jobpost-title-choices'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('email-verification/', EmailVerificationRequestView.as_view(), name='email-verification'),
    path('verify-email/<uidb64>/<token>/', EmailVerificationConfirmView.as_view(), name='verify-email'),
] 