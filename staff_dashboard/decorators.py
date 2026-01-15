from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden

F = TypeVar("F", bound=Callable[..., HttpResponse])


def staff_required(view_func: F) -> F:
    """
    Доступ только для is_staff.
    - Если не залогинен -> редирект на /users/login/
    - Если залогинен, но не staff -> 403
    """

    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                login_url="/users/login/",
            )
        if not request.user.is_staff:
            return HttpResponseForbidden("Forbidden: staff only")
        return view_func(request, *args, **kwargs)

    return _wrapped  # type: ignore[return-value]
