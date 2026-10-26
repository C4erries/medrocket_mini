


import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse


class RequestTracingMiddleware:
    """
    Middleware трассировки и контроля безопасности API.
    Демонстрирует прямой ход, обратный ход и short-circuit.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        # Инициализируется 1 раз при старте Django-проецсса.
        # get_response - ссылка на следующий слой луковицы (next в go)
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse | None:
        # 1. прямой ход (request phase)
        start_time = time.perf_counter()

        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.request_id = request_id # type: ignore[attr-defined]

        # пример short-circuit (теперь у нас не соответствие SRP, но для примера норм)
        # если клиент стучится в закрытое API без базового секрета - отклоняем запрос сразу
        if (
            request.path.startswith("/api/v1/internal/")
            and not request.headers.get("X-Internal-Token")
        ):
            # todo: создать константу для таких ошибок
            # (навряд ли у нас она в единственном месте будет)
            return JsonResponse({"error": "Forbidden: missing internal token"}, status=403)

        # передаем управление следующей middleware (или view)
        response = self.get_response(request)

        # 2. обратный ход (response phase)
        duration = time.perf_counter() - start_time

        # Обогащаем заголовки ответа для клиента
        response["X-Request-ID"] = request_id
        response["X-Process-Time"] = f"{duration:.4f}s"

        return response

    def process_view(
        self,
        _request: HttpRequest,
        _view_func: Callable[..., HttpResponse],
        _view_args: tuple[object, ...],
        _view_kwargs: dict[str, object],
    ) -> HttpResponse | None:
        """
        Вызывает после того, как роутер нашел функцию View, но до её вызова.
        Если вернуть None - выполнение продолжается.
        Если вернуть HttpResponse - выполнение прерывается (short circuit).
        """

        # Позволяет проверить метаданные самой функции view (например, кастомные атрибуты)
        return None

    def process_exception(self, _request: HttpRequest, _exc: Exception) -> HttpResponse | None:
        """
        Выызвается, если view выбросила необработанное исключение.
        Идет также снизу вверх. Позволяет вернуть JSON вместо 500 HTML-страницы.
        """

        return None

class MedicalApiSecurityMiddleware:

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse | None:
        start_time = time.perf_counter()
        if request.path.startswith("/api/") and not request.headers.get("X-Client-Platform"):
            return JsonResponse({"error": "Missing required X-Client-Platform header"}, status=400)

        response = self.get_response(request)

        duration = time.perf_counter() - start_time

        response["X-Service-Name"] = "MiniMedRocket"
        response["X-Response-Time"] = f"{duration:.4f}"

        return response

    def process_exception(
        self,
        _request: HttpRequest,
        exc: Exception,
    ) -> HttpResponse | None:
        if isinstance(exc, ValueError):
            return JsonResponse({"error": "Bad Request", "detail": str(exc)}, status=400)
        return None
