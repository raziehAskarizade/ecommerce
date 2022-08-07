from functools import partial

from rest_framework import permissions


class MyPermission(permissions.BasePermission):

    def __init__(self, allowed_methods):
        super().__init__()
        self.allowed_methods = allowed_methods

    def has_permission(self, request, view):
        return request.method in self.allowed_methods


class ExampleView(APIView):
    permission_classes = (partial(MyPermission, ['GET', 'HEAD']),)
