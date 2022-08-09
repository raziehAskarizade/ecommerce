# import json
#
# from django.conf import settings
# from user.models import User
# from django.http.response import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_GET, require_POST
# from webpush.utils import send_to_subscription
#
#
# @require_GET
# def home(request):
#     webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
#     vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
#     print(type(vapid_key))
#     user = request.user
#     # return render(request, 'home.html', {user: user, 'vapid_key': vapid_key})
#     return
#
#
# @require_POST
# @csrf_exempt
# def send_push(request):
#     payload = {"head": "Welcome!", "body": "Hello World"}
#
#     user = request.user
#     push_infos = user.webpush_info.select_related("subscription")
#     for push_info in push_infos:
#         send_to_subscription(push_info.subscription, payload)
#
#     return render
