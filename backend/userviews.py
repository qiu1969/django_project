from backend.models import User
from backend.serializers import UserSerializer,UserUnserializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from backend.authentication import LoginAuthentication
from rest_framework import status
from django.db.models import Q
from rest_framework_jwt.serializers import jwt_decode_handler,jwt_payload_handler,jwt_encode_handler


class LoginView(APIView):
    # 用户登录视图
    def post(self,request,*args,**kwargs):
        # post请求处理登录逻辑
        username = request.data.get('username')
        password = request.data.get('password')
        if not (username and password):
            return Response('缺少用户名/邮箱/电话或密码',status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(Q(username__exact=username) | Q(email__exact=username) | Q(phone__exact=username))
        except User.DoesNotExist:
            return Response('用户不存在',status=status.HTTP_404_NOT_FOUND)
        except User.MultipleObjectsReturned:
            return Response('匹配到多个用户',status=status.HTTP_400_BAD_REQUEST)
        
        if user.password != password:
            return Response('用户名/邮箱/电话或密码错误',status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(instance=user)
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        data = serializer.data
        data['token'] = token

        return Response(data,status=status.HTTP_200_OK)


class RegisterView(APIView):
    # 用户注册的视图类
    def post(self,request,*args,**kwargs):
        serializer = UserUnserializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        user = serializer.save()
        serializer = UserSerializer(instance=user)
        return Response(serializer.data,status=status.HTTP_200_OK)


class UserView(APIView):
    authentication_classes = [LoginAuthentication]
    # 获取所有用户
    def get(self,request,*args,**kwargs):
        user_id = request.query_params.get('user_id')
        login_id = request.user['user_id']
        if not user_id:
            return Response('缺少用户id',status=status.HTTP_200_OK)
        # print(type(user_id))
        user_id = int(user_id)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(instance=user,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        try:
            user = User.objects.get(id=login_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_404_NOT_FOUND)
        request.data['password'] = user.password
        serializer = UserUnserializer(instance=user,data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        update_user = serializer.save()
        serializer = UserSerializer(instance=update_user,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        password = request.data.get('password')
        login_id = request.user['user_id']
        if not password:
            return Response('没有输入密码',status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id__exact=login_id)
        except User.DoesNotExist:
            return Response('您要注销的用户不存在',status=status.HTTP_404_NOT_FOUND)
        if user.password != password:
            return Response('密码错误',status=status.HTTP_401_UNAUTHORIZED)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowersView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        followee_id = request.query_params.get('followee_id')
        if not followee_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        followee_id = int(followee_id)
        try:
            followee = User.objects.get(id__exact=followee_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_404_NOT_FOUND)
        followers = followee.followers.all()
        serializer = UserSerializer(instance=followers,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class FolloweesView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        follower_id = request.query_params.get('follower_id')
        if not follower_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        follower_id = int(follower_id)
        try:
            follower = User.objects.get(id__exact=follower_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_404_NOT_FOUND)
        followees = follower.followee_set.all()
        serializer = UserSerializer(instance=followees,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class SearchUsersView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        keyword = request.query_params.get('keyword')
        if not keyword:
            return Response('缺少搜索关键字',status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(username__contains=keyword)
        serializer = UserSerializer(instance=users,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class ChangePassword(APIView):
    authentication_classes = [LoginAuthentication]
    def put(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not (old_password and new_password):
            return Response('缺少旧密码或新密码',status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=login_id)
        except User.DoesNotExist:
            return Response('用户不存在',status=status.HTTP_404_NOT_FOUND)
        if old_password != user.password:
            return Response('密码错误',status=status.HTTP_400_BAD_REQUEST)
        user.password = new_password
        user.save()
        return Response(status=status.HTTP_201_CREATED)


class FollowView(APIView):
    # 关注某人
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        followee_id = request.query_params.get('user_id')
        follower_id = request.user['user_id']
        if not followee_id :
            return Response('缺少要关注的用户id',status=status.HTTP_400_BAD_REQUEST)
        followee_id = int(followee_id)
        if followee_id == follower_id:
            return Response('请不要关注自己',status=status.HTTP_400_BAD_REQUEST)
        try:
            followee = User.objects.get(id__exact=followee_id)
        except User.DoesNotExist:
            return Response('您要关注用户不存在',status=status.HTTP_404_NOT_FOUND)
        except User.MultipleObjectsReturned:
            return Response('匹配到多个用户',status=status.HTTP_400_BAD_REQUEST)
        serializer = UserUnserializer(instance=followee)
        followee_data = serializer.data
        if follower_id in followee_data['followers']:
            return Response('您已经关注了TA',status=status.HTTP_400_BAD_REQUEST)
        followee_data['followers'].append(follower_id)
        serializer = UserUnserializer(instance=followee,data=followee_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        followee = serializer.save()
        serializer = UserSerializer(instance=followee,context={'login_id':follower_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        followee_id = int(request.query_params.get('user_id'))
        follower_id = request.user['user_id']
        if not followee_id :
            return Response('缺少您要取消关注的用户id',status=status.HTTP_400_BAD_REQUEST)
        elif followee_id == follower_id:
            return Response('请不要取消关注自己',status=status.HTTP_400_BAD_REQUEST)

        try:
            followee = User.objects.get(id__exact=followee_id)
        except User.DoesNotExist:
            return Response('您要取消关注的用户不存在',status=status.HTTP_404_NOT_FOUND)
        except User.MultipleObjectsReturned:
            return Response('匹配到多个用户',status=status.HTTP_400_BAD_REQUEST)

        serializer = UserUnserializer(instance=followee)
        followee_data = serializer.data
        if follower_id not in followee_data['followers']:
            return Response('您还没有关注了TA',status=status.HTTP_400_BAD_REQUEST)
        followee_data['followers'].remove(follower_id)
        serializer = UserUnserializer(instance=followee,data=followee_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        followee = serializer.save()
        serializer = UserSerializer(instance=followee,context={'login_id':follower_id})
        return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)


class ChangeAvatorView(APIView):
    # 更换头像
    authentication_classes = [LoginAuthentication]
    def put(self,request,*args,**kwargs):
        avator = request.data.get('avator')
        login_id = request.user['user_id']
        if not avator:
            return Response('缺少头像路径',status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=login_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_404_NOT_FOUND)
        user.avator = avator
        user.save()
        return Response(status=status.HTTP_201_CREATED)

        
        