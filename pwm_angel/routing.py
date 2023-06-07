from channels.routing import ProtocolTypeRouter, URLRouter
# from django.conf.urls import url
from django.urls import re_path
# from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from users_managements.consumer import User_DevUpdates_Consumer


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                re_path(r"^user-socket-portal/(?P<deviceNo>)", User_DevUpdates_Consumer.as_asgi()),
            ]
        )
    )
})
