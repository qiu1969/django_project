from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from backend.authentication import LoginAuthentication
from rest_framework import status
from Vue_django.settings import BASE_DIR
from backend.models import Avator
from backend.serializers import AvatorSerializer


class AvatorView(APIView):
    # 用于图像上传的视图
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        file = request.FILES.get('file')
        login_id = request.user['user_id']
        save_path = str(BASE_DIR) + '/avators/' +str(login_id) + file.name

        avator = {
            'user':login_id,
            'path':str(login_id)+file.name
        }
        serializer = AvatorSerializer(data=avator)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 创建文件
        with open(save_path,'wb') as f:
            for content in file.chunks():
                f.write(content)
        avator = serializer.save()
        serializer = AvatorSerializer(instance=avator)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def get(self,request,*args,**kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        avators = Avator.objects.filter(user__id__exact=user_id)
        serializer = AvatorSerializer(instance=avators,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)