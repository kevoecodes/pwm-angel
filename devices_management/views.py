from django.http import QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView

from devices_management.mongo_curd import MongoDevicesManager


class Device_Portal(APIView):
    permission_classes = []

    @staticmethod
    def post(request, *args, **kwargs):
        data = request.data
        if 'token' not in data and 'deviceNo' not in data:
            return Response(0.0, status=400)
        print(type(data))
        if type(data) == QueryDict:
            data = dict(request.data.dict())
            print(type(data))

        print(data)
        device_manager = MongoDevicesManager()
        if device_manager.isDevice(data) and not device_manager.isBlocked(data):
            units = device_manager.deduce_token(data)
            return Response(units)

        return Response(0.0)

