from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import status, permissions, viewsets, serializers
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import action, api_view

from django.db.models import Manager

from http import HTTPMethod
from typing import List
from functools import wraps

from .models import User, Environment
from .serializers import (
    UserSerializer, 
    EnvironmentSerializer, 
    FileSerializer,
    FileNameSerializer,
    PromptSerializer
)
from .services import EnvironmentService

# Create your views here.

def serialize(queryset: Manager, serializers: List[type[serializers.Serializer]] = []):
    """Декоратор для проверки объекта на существование по pk и обработки других ошибок"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request: HttpRequest, pk: str, **kwargs):
            if (queryset.filter(id=pk).exists() == False):
                return JsonResponse(
                    {"detail": "Not found."}, 
                    status=status.HTTP_404_NOT_FOUND)
            if (all([x(data=request.data).is_valid() for x in serializers]) == False):
                return JsonResponse(
                    {"detail": "Bad request."},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                return func(self, request, pk, **kwargs)
            except Exception as e:
                return JsonResponse(
                    {"detail": " ".join(e.args)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return wrapper
    return decorator

"""
Endpoints:  

/
api/v1/users/ {list: GET, create: POST}
api/v1/users/{pk}/ {retrieve: GET, update: PUT, partial_update: PATCH, destroy: DELETE}
"""
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permissions_classes = [permissions.AllowAny]
    
"""
Endpoints:  

/
api/v1/environments/ {list: GET, create: POST}
api/v1/environments/{pk}/ {retrieve: GET, update: PUT, partial_update: PATCH, destroy: DELETE}

/env
api/v1/environments/{pk}/drop {drop: POST}

/files
api/v1/environments/{pk}/load-file {loadFile: POST}
api/v1/environments/{pk}/update-file {updateFile: POST}
api/v1/environments/{pk}/remove-file {removeFile: DELETE}
api/v1/environments/{pk}/read-file {readFile: GET}
api/v1/environments/{pk}/list-files {listFiles: GET}

/model
api/v1/environments/{pk}/generate {generate: POST}
api/v1/environments/{pk}/send-prompt {sendPrompt: POST}
api/v1/environments/{pk}/commit-files {commitFiles: POST}
api/v1/environments/{pk}/get-context {getContext: GET}
api/v1/environments/{pk}/clear-context {clearContext: DELETE}
"""
class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    permissions_classes = [permissions.AllowAny]
    
    environmentService = EnvironmentService()

    """Endpoints: """
    """For Environment:"""

    def perform_create(self, serializer: EnvironmentSerializer):
        self.environmentService.createEnvironment(serializer.data.get("id"))
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    @action(url_path="drop", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset)
    def drop(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Очистка окружения без его удаления"""

        return self.environmentService.clearEnvironment(pk)
    
    """For Files:"""

    @action(url_path="load-file", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset, serializers=[FileSerializer])
    def loadFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Загрузка файла в окружение"""
        
        file = request.FILES['file']
        return self.environmentService.saveFile(pk, file, file.name)
    
    @action(url_path="update-file", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset, serializers=[FileSerializer])
    def updateFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Обновление файла в окружение"""

        file = request.FILES['file']
        return self.environmentService.updateFile(pk, file, file.name)
    
    @action(url_path="remove-file", detail=True, methods=[HTTPMethod.DELETE])
    @serialize(queryset=queryset, serializers=[FileNameSerializer])
    def removeFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Удаление файла из окружения"""

        # filename = request.GET.get("filename", None)
        # if (filename is None):
        #     return JsonResponse(
        #         {"detail": "Bad request."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        filename = request.data.get("filename", None)
        return self.environmentService.removeFile(pk, filename)
    
    @action(url_path="read-file", detail=True, methods=[HTTPMethod.GET])
    @serialize(queryset=queryset, serializers=[FileNameSerializer])
    def readFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Считывание файла из окружения"""

        # filename = request.GET.get("filename", None)
        # if (filename is None):
        #     return JsonResponse(
        #         {"detail": "Bad request."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        filename = request.data.get("filename", None)
        return self.environmentService.readFile(pk, filename)
    
    @action(url_path="list-files", detail=True, methods=[HTTPMethod.GET])
    @serialize(queryset=queryset)
    def listFiles(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Получение списка файлов окружения и их свойств"""

        return self.environmentService.listFiles(pk)
    
    """For AI Model:"""
    
    @action(url_path="generate", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset)
    def generate(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Отправка запроса модели на генерацию текстового файла на основе файлов из окружения и дополнительного запроса"""
        
        return self.environmentService.generate(pk, request.data.get("prompt", ''))

    @action(url_path="send-prompt", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset, serializers=[PromptSerializer])
    def sendPrompt(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Отправка произвольного запроса модели"""
        print("controller:", request.data.get("prompt", ''))
        return self.environmentService.sendPrompt(pk, request.data.get("prompt", ''))
    
    @action(url_path="commit-files", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset)
    def commitFiles(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Загрузка текстовых файлов из окружения в контекст модели"""

        return self.environmentService.commitFiles(pk)

    @action(url_path="get-context", detail=True, methods=[HTTPMethod.GET])
    @serialize(queryset=queryset)
    def getContext(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Получение истории сообщений переписки с моделью"""

        return self.environmentService.getChatContext(pk)

    @action(url_path="clear-context", detail=True, methods=[HTTPMethod.DELETE])
    @serialize(queryset=queryset)
    def clearContext(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Очистка контекста модели"""

        return self.environmentService.clearChatContext(pk)