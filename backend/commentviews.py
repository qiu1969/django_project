from django.shortcuts import render
from backend.serializers import CommentUnserializer,CommentSerializer
from backend.models import Comment
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from backend.authentication import LoginAuthentication
from rest_framework import status

'''
状态码(status code):
200 OK - [GET]:服务器成功返回用户请求的数据
201 CREATED - [POST/PUT/PATCH]:用户新建或修改数据成功
202 ACCEPTED -[*]:表示一个请求已经进入后台排队(异步任务)
204 NO CONTENT - [DELETE]:表示用户删除数据成功
400 INAVLID REQUEST - [POST/PUT/PATCH]:用户发出的请求有错误，服务器没有进行新建或修改
401 UNAUTHORIZED - [*]:表示用户没有权限
404 NOT FOUND - [*]:用户发出的请求针对的是不存在的记录
406 NOT ACCEPTABLE - [GET]:用户请求的格式不可得
410 GONE - [GET]: 用户请求的资源被永久删除，且不会再得到
422 Unprocesable entity - [POST/PUT/PATCH]:创建一个对象发生了验证错误
500 INTERNAL SERVER ERROR - [*]:服务器发生错误
'''


class CommentView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        comments = Comment.objects.filter(answer__id__exact=answer_id)
        serializer = CommentSerializer(instance=comments,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        data = request.data
        data['author'] = login_id
        serializer = CommentUnserializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        comment = serializer.save()
        serializer = CommentSerializer(instance=comment,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def put(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response('缺少要修改的评论id',status=status.HTTP_400_BAD_REQUEST)
        comment_id = int(comment_id)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response('您所访问的评论不存在',status=status.HTTP_404_NOT_FOUND)
        if login_id != comment.author.id:
            return Response('您没有修改的权限',status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        data['author'] = login_id
        serializer = CommentUnserializer(instance=comment,data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        update_comment = serializer.save()
        serializer = CommentSerializer(instance=update_comment,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response('缺少要删除的评论id',status=status.HTTP_400_BAD_REQUEST)
        comment_id = int(comment_id)
        try:
            comment = Comment.objects.get(id__exact=comment_id)
        except Comment.DoesNotExist:
            return Response('您要删除的评论不存在',status=status.HTTP_404_NOT_FOUND)
        if comment.author.id != login_id:
            return Response('您没有删除权限',status=status.HTTP_401_UNAUTHORIZED)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeCommentView(APIView):
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        comment_id = request.query_params.get('comment_id')
        login_id = request.user['user_id']
        if not comment_id:
            return Response('缺少要点赞的评论id',status=status.HTTP_400_BAD_REQUEST)
        comment_id = int(comment_id)
        try:
            comment = Comment.objects.get(id__exact=comment_id)
        except Comment.DoesNotExist:
            return Response('评论不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = CommentUnserializer(instance=comment)
        comment_data = serializer.data
        if login_id in comment_data['likers']:
            return Response('您已经点赞了这个评论',status=status.HTTP_400_BAD_REQUEST)
        comment_data['likers'].append(login_id)
        serializer = CommentUnserializer(instance=comment, data=comment_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        comment = serializer.save()
        serializer = CommentSerializer(instance=comment,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        comment_id = request.GET.get('comment_id')
        login_id = request.user['user_id']
        if not comment_id:
            return Response('缺少要取消点赞的评论id',status=status.HTTP_400_BAD_REQUEST)
        comment_id = int(comment_id)
        try:
            comment = Comment.objects.get(id__exact=comment_id)
        except Comment.DoesNotExist:
            return Response('评论不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = CommentUnserializer(instance=comment)
        comment_data = serializer.data
        if login_id not in comment_data['likers']:
            return Response('您还没有点赞这个评论',status=status.HTTP_400_BAD_REQUEST)
        comment_data['likers'].remove(login_id)
        serializer = CommentUnserializer(instance=comment, data=comment_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        comment = serializer.save()
        serializer = CommentSerializer(instance=comment,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)
