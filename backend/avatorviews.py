from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from backend.authentication import LoginAuthentication
from rest_framework import status
from Vue_django.settings import BASE_DIR


class UploadImage(APIView):
    # 用于图像上传的视图
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        file = request.FILES.get('file')
        login_id = request.user['user_id']
        save_path = str(BASE_DIR) + '/avators/' +str(login_id) + file.name

        print(save_path)

        # 创建文件
        with open(save_path,'wb') as f:
            for content in file.chunks():
                f.write(content)

        return Response((str(login_id)+file.name),status=status.HTTP_201_CREATED)