from django.http import QueryDict
from rest_framework.response import Response
from rest_framework.views import APIView

from devices_management.mongo_curd import MongoDevicesManager


class Device_Portal(APIView):
    permission_classes = []
    def post(self, request, *args, **kwargs):
        data = request.data
        print(type(data))
        if type(data) == QueryDict:
            data = dict(request.data.dict())
            print(type(data))

        print(data)
        device_manager = MongoDevicesManager()
        if device_manager.isDevice(data) and not device_manager.isBlocked(data):
            update = device_manager.deviceUpdate(data)
            if update == True:
                return Response(device_manager.new_units)

        return Response(False)

