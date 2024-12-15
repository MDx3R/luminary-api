from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import status, permissions, views, viewsets, serializers
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.authtoken.models import Token

from django.db.models import Manager
from django.contrib.auth import authenticate

from drf_spectacular.utils import (
    extend_schema, 
    extend_schema_view, 
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

from http import HTTPMethod
from typing import List
from functools import wraps

from .models import User, Environment
from .serializers import (
    UserSerializer, 
    LoginSerializer,
    EnvironmentSerializer, 
    FileSerializer,
    FileNameSerializer,
    PromptSerializer,
    GeneratePromptSerializer,
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

@extend_schema_view(
    post=extend_schema(
        summary="Авторизация",
        description="Авторизация на основе постоянных токенов.",
        # parameters=[
        #     OpenApiParameter(
        #         name="username",
        #         description="Имя пользователя",
        #         type=str,
        #         location=OpenApiParameter.QUERY,
        #         required=True,
        #     ),
        #     OpenApiParameter(
        #         name="password",
        #         description="Пароль",
        #         type=str,
        #         location=OpenApiParameter.QUERY,
        #         required=True,
        #     ),
        # ],
        request=LoginSerializer,
        responses={
            200: {
                "description": "Успешная авторизация",
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Токен доступа"},
                    "user": {"$ref": "#/components/schemas/User"}, # ссылка на UserSerializer
                },
            },
            401: {
                "description": "Неверные учетные данные",
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "Сообщение об ошибке"},
                },
            },
        },
    )
)
class LoginView(views.APIView):
    permissions_classes = [permissions.AllowAny]

    def post(self, request: HttpRequest):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if (user):
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key, 
                    "user": UserSerializer(user).data
                }, 
                status=status.HTTP_200_OK
            )
        
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permissions_classes = [permissions.AllowAny]

@extend_schema(tags=["Environments"])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список окружений",
    ),
    create=extend_schema(
        summary="Создание окружение",
    ),
    retrieve=extend_schema(
        summary="Получить информацию о окружении",
    ),
    update=extend_schema(
        summary="Обновить существующее окружение",
    ),
    partial_update=extend_schema(
        summary="Обновить определенные поля существующего окружения",
    ),
    destroy=extend_schema(
        summary="Удалить окружение",
    ),
    drop=extend_schema(
        summary="Очистить окружение без его удаления",
        description="Удаляет файлы окружения и очищаем контекст модели.",
        request=None,
        responses={
            200: None
        },
    ),
    loadFile=extend_schema(
        summary="Загрузить файл в окружение",
        description="Загружает один файл в окружение. Если файл с таким именем уже существует, он будет замен полученным файлом.",
        request=FileSerializer,
        responses={
            201: None
        },
    ),
    updateFile=extend_schema(
        summary="Обновить файл в окружение",
        description="Дополняет содержимое файла в окружении. Если файла не существует, он будет создан с полученным содержанием файла.",
        request=FileSerializer,
        responses={
            200: None
        },
    ),
    removeFile=extend_schema(
        summary="Удалить файл из окружения",
        description="Удаляет файл из окружения по его имени. Независимо от существования файла, возвращает 200 код ответа.",
        request=FileNameSerializer,
        responses={
            200: None
        },
    ),
    readFile=extend_schema(
        summary="Получить файл из окружения",
        description="Получает содержание файла из окружения по его имени.",
        request=FileNameSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "file": {"type": "string"},
                    }
                }
            )
            # добавить 404 при отсутсвии файла
        },
    ),
    listFiles=extend_schema(
        summary="Получить список файлов из окружения",
        description="Получает список файлов из окружения.",
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string"},
                            "size": {"type": "integer", "format": "int64"},
                            "updatedAt": {"type": "integer", "format": "int64"},
                        }
                    }
                }
            )
        },
    ),
    generate=extend_schema(
        summary="Отправить запрос на генерацию текста по файлам окружения",
        description="""Отправляет запрос на генерацию текста на основе файлов из окружения и дополнительного запроса, если он есть. 
                    Этот эндпоинт автоматически загрузит файлы в окружение аналогично commit-files""",
        request=GeneratePromptSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object", 
                    "properties": {
                        "response": {
                            "type": "string"
                        }
                    }
                }
            )
        },
    ),
    sendPrompt=extend_schema(
        summary="Отправить простой запрос на генерацию текста",
        description="Отправляет простой запрос на генерацию текста модели.",
        request=PromptSerializer,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object", 
                    "properties": {
                        "response": {
                            "type": "string"
                        }
                    }
                },
            )
        },
    ),
    commitFiles=extend_schema(
        summary="Загрузить содержание файлов окружения в контекст",
        description="Загружает содержание файлов окружения в контекст модели. Если файлов не сущетсвует, загружается пустой контекст.",
        request=None,
        responses={
            200: None
        },
    ),
    getContext=extend_schema(
        summary="Получить историю чата с моделью",
        description="Получает сообщения из контекста модели. Системные сообщения игнорируются, например, промпт по умолчанию или содержаение файлов.",
        request=None,
        responses={
            200: OpenApiResponse(
                response={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "content": {"type": "string"}
                        }
                    },
                },
                examples=[
                    OpenApiExample(
                        name="Пример ответа",
                        value=[
                            {"role": "user", "content": "request"},
                            {"role": "assistant", "content": "response"},
                        ],
                        response_only=True,
                    )
                ]
            )
        },
    ),
    clearContext=extend_schema(
        summary="Очистить контекст модели",
        description="Очищает контекст модели, оставляя промпт по умолчанию",
        request={},
        responses={
            200: None
        },
    ),
)
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

        filename = request.data.get("filename", None)
        return self.environmentService.removeFile(pk, filename)
    
    @action(url_path="read-file", detail=True, methods=[HTTPMethod.GET])
    @serialize(queryset=queryset, serializers=[FileNameSerializer])
    def readFile(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Считывание файла из окружения"""

        filename = request.data.get("filename", None)
        return self.environmentService.readFile(pk, filename)
    
    @action(url_path="list-files", detail=True, methods=[HTTPMethod.GET])
    @serialize(queryset=queryset)
    def listFiles(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Получение списка файлов окружения и их свойств"""

        return self.environmentService.listFiles(pk)
    
    """For AI Model:"""
    
    @action(url_path="generate", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset, serializers=[GeneratePromptSerializer])
    def generate(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Отправка запроса модели на генерацию текстового файла на основе файлов из окружения и дополнительного запроса"""
        
        return self.environmentService.generate(pk, request.data.get("prompt", ''))

    @action(url_path="send-prompt", detail=True, methods=[HTTPMethod.POST])
    @serialize(queryset=queryset, serializers=[PromptSerializer])
    def sendPrompt(self, request: HttpRequest, pk: str) -> JsonResponse:
        """Отправка произвольного запроса модели"""

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