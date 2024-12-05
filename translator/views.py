from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from translator.models import Translation
from translator.serializers import TranslationSerializer
from drf_yasg.utils import swagger_auto_schema
import google.generativeai as genai
import os

env_path = os.path.join(os.path.dirname(__file__), '../.env')

if os.path.exists(env_path):
    with open(env_path, 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

GEMINI_API_KEY = os.environ.get('GOOGLE_API_KEY')

class AllTranslation(APIView):

    def get(self, request):

        print(GEMINI_API_KEY)
        result = Translation.objects.all()
        serialized_data = TranslationSerializer(result, many=True)
        return Response(data={'results': serialized_data.data}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=TranslationSerializer)
    def post(self, request):
        source_language = request.GET.get('source_language')
        source_text = request.GET.get('source_text')
        target_language = request.GET.get('target_language')

        if not source_language or not source_text or not target_language:
            return Response(data={'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"Traduis '{source_text}' en {target_language}. La réponse ne doit contenir que la traduction"
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        target_text = response.text

        translation = Translation.objects.create(
            source_language=source_language,
            source_text=source_text,
            target_language=target_language,
            target_text=target_text
        )

        return Response(data={
            'Result': "Translation created",
            'Translation': TranslationSerializer(translation).data
        }, status=status.HTTP_201_CREATED)
