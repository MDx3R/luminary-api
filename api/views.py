from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import status, permissions, viewsets
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from .models import User, Environment
from .serializers import UserSerializer, EnvironmentSerializer, FileSerializer

from http import HTTPMethod

# Create your views here.

"""
Endpoints:  

/
api/v1/users/ {list: GET, create: POST}
api/v1/users/{pk}/ {retrieve: GET, create: POST, update: PUT, partial_update: PATCH, destroy: DELETE}
"""
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permissions_classes = [permissions.AllowAny]
    
"""
Endpoints:  

/
api/v1/environments/ {list: GET, create: POST}
api/v1/environments/{pk}/ {retrieve: GET, create: POST, update: PUT, partial_update: PATCH, destroy: DELETE}

/env
api/v1/environments/{pk}/drop {drop: POST} -

/files
api/v1/environments/{pk}/load-file {loadFile: POST} +
api/v1/environments/{pk}/update-file {updateFile: POST} -
api/v1/environments/{pk}/remove-file {removeFile: POST} +
api/v1/environments/{pk}/read-file {readFile: GET} -
api/v1/environments/{pk}/list-files {listFiles: GET} +-

/model
api/v1/environments/{pk}/generate {generate: POST} +
api/v1/environments/{pk}/send-prompt {sendPrompt: POST} +
api/v1/environments/{pk}/commit-files {commitFiles: POST} +-
api/v1/environments/{pk}/clear-context {clearContext: POST} -
"""
class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    permissions_classes = [permissions.AllowAny]

    #environmentService = EnvironmentService()
    
    """Endpoints: """
    """For Environment:"""

    @action(url_path="drop", detail=True, methods=[HTTPMethod.POST])
    def drop(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Очистка окружения без его удаления"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    """For Files:"""

    @action(url_path="load-file", detail=True, methods=[HTTPMethod.POST])
    def loadFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Загрузка файла в окружение"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    @action(url_path="update-file", detail=True, methods=[HTTPMethod.POST])
    def updateFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Обновление файла в окружение"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    @action(url_path="remove-file", detail=True, methods=[HTTPMethod.POST])
    def removeFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Удаление файла из окружения"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    @action(url_path="read-file", detail=True, methods=[HTTPMethod.GET])
    def readFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Считывание файла из окружения"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    @action(url_path="list-files", detail=True, methods=[HTTPMethod.GET])
    def listFiles(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Получение списка файлов окружения и их свойств"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    """For AI Model:"""
    
    @action(url_path="generate", detail=True, methods=[HTTPMethod.POST])
    def generate(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Отправка запроса модели на генерацию текстового файла на основе файлов из окружения и дополнительного запроса"""
        
        return JsonResponse({}, status=status.HTTP_200_OK)

    @action(url_path="send-prompt", detail=True, methods=[HTTPMethod.POST])
    def sendPrompt(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Отправка произвольного запроса модели"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    @action(url_path="commit-files", detail=True, methods=[HTTPMethod.POST])
    def commitFiles(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Загрузка текстовых файлов из окружения в контекст модели"""

        return JsonResponse({}, status=status.HTTP_200_OK)
    
    @action(url_path="clear-context", detail=True, methods=[HTTPMethod.POST])
    def clearContext(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Очистка контекста модели"""

        return JsonResponse({}, status=status.HTTP_200_OK)