from rest_framework.authentication import BaseAuthentication
from rest_framework_jwt.serializers import jwt_decode_handler
from rest_framework import exceptions
from rest_framework.response import Response
import jwt

class LoginAuthentication(BaseAuthentication):
    # 验证用户登录的类
    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')

        if not token:
            raise exceptions.AuthenticationFailed('请先登录')

        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed('登录已失效，请重新登录')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('解码错误')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('认证失败')
        return (payload,token)



