from .models import UserProfile


class UserProfileMiddleware:
    """
    Гарантирует наличие профиля пользователя и прокидывает его в request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.profile = None

        if request.user.is_authenticated:
            try:
                request.profile = request.user.profile
            except UserProfile.DoesNotExist:
                # Создаем профиль на лету, если по какой-то причине он отсутствует
                request.profile = UserProfile.objects.create(user=request.user)

        response = self.get_response(request)
        return response
