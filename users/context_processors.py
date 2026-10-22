def notifications(request):
    """Количество непрочитанных уведомлений для значка в шапке сайта."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {}
    return {'unread_notifications_count': user.notifications.filter(viewed=False).count()}
