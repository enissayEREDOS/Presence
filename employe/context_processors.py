# context_processors.py

from django.conf import settings

from .models import Notification

def unread_notifications_count(request):
    user_id = request.session.get('user_id')
    if user_id:
        count = Notification.objects.filter(utilisateur_id=user_id, vue=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}