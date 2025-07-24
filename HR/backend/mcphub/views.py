import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'

@api_view(['POST'])
def chat_view(request):
    if not OPENROUTER_API_KEY:
        return Response({'error': 'OpenRouter API key not set.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    messages = request.data.get('messages', [])
    model = request.data.get('model', 'gpt-3.5')
    payload = {
        'model': model,
        'messages': messages,
    }
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
    }
    try:
        resp = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        ai_response = data['choices'][0]['message']['content'] if data.get('choices') else 'No response.'
        return Response({'response': ai_response})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def models_view(request):
    if not OPENROUTER_API_KEY:
        return Response({'data': [
            {"id": "gpt-3.5", "label": "GPT-3.5", "value": "gpt-3.5"},
            {"id": "gpt-4", "label": "GPT-4", "value": "gpt-4"}
        ]})
    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
    }
    try:
        resp = requests.get(OPENROUTER_MODELS_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # OpenRouter returns models as a list under 'data'
        return Response({'data': data.get('data', [])})
    except Exception as e:
        return Response({'data': [
            {"id": "gpt-3.5", "label": "GPT-3.5", "value": "gpt-3.5"},
            {"id": "gpt-4", "label": "GPT-4", "value": "gpt-4"}
        ], 'error': str(e)}) 