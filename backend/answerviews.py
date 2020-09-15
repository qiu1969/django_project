from backend.models import Answer,User
from backend.serializers import AnswerSerializer,AnswerUnserializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from backend.authentication import LoginAuthentication
from rest_framework import status


class AnswerView(APIView):
    # 回答的增删改查
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        if not answer_id:
            return Response('缺少回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id__exact=answer_id)
        except Answer.DoesNotExist:
            return Response('您所访问的回答不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerSerializer(instance=answer,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        data = request.data
        data['author'] = login_id
        serializer = AnswerUnserializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        answer = serializer.save()
        serializer = AnswerSerializer(instance=answer,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        
    def put(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        if not answer_id:
            return Response('缺少要修改的回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id=answer_id)
        except Answer.DoesNotExist:
            return Response('您所访问的回答不存在',status=status.HTTP_404_NOT_FOUND)
        if login_id != answer.author.id:
            return Response('您没有修改的权限',status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        data['author'] = login_id
        serializer = AnswerUnserializer(instance=answer,data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        update_answer = serializer.save()
        serializer = AnswerSerializer(instance=update_answer,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        answer_id = request.query_params.get('answer_id')
        if not answer_id:
            return Response('缺少要删除的回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id__exact=answer_id)
        except Answer.DoesNotExist:
            return Response('您要删除的回答不存在',status=status.HTTP_404_NOT_FOUND)
        if answer.author.id != login_id:
            return Response('您没有删除权限',status=status.HTTP_401_UNAUTHORIZED)
        answer.delete()
        return Response('回答删除成功',status=status.HTTP_204_NO_CONTENT)


class CollectView(APIView):
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        if not answer_id:
            return Response('缺少要收藏的回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id__exact=answer_id)
        except Answer.DoesNotExist:
            return Response('回答不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerUnserializer(instance=answer)
        answer_data = serializer.data
        if login_id in answer_data['collectors']:
            return Response('您已经收藏了这个回答',status=status.HTTP_400_BAD_REQUEST)
        answer_data['collectors'].append(login_id)
        serializer = AnswerUnserializer(instance=answer, data=answer_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response({'msg':str(exception)},status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        answer = serializer.save()
        serializer = AnswerSerializer(instance=answer,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        if not answer_id:
            return Response('缺少取消收藏的回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id__exact=answer_id)
        except Answer.DoesNotExist:
            return Response('回答不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerUnserializer(instance=answer)
        answer_data = serializer.data
        if login_id not in answer_data['collectors']:
            return Response('您还没有收藏这个回答',status=status.HTTP_400_BAD_REQUEST)
        answer_data['collectors'].remove(login_id)
        serializer = AnswerUnserializer(instance=answer, data=answer_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        answer = serializer.save()
        # serializer = AnswerSerializer(instance=answer,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)


class LikeAnswerView(APIView):
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        if not answer_id:
            return Response('缺少要点在的回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id__exact=answer_id)
        except Answer.DoesNotExist:
            return Response('回答不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerUnserializer(instance=answer)
        answer_data = serializer.data
        if login_id in answer_data['likers']:
            return Response('您已经点赞了这个回答',status=status.HTTP_400_BAD_REQUEST)
        answer_data['likers'].append(login_id)
        serializer = AnswerUnserializer(instance=answer, data=answer_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        answer = serializer.save()
        serializer = AnswerSerializer(instance=answer,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        answer_id = request.query_params.get('answer_id')
        login_id = request.user['user_id']
        if not answer_id:
            return Response('缺少要取消点赞的回答id',status=status.HTTP_400_BAD_REQUEST)
        answer_id = int(answer_id)
        try:
            answer = Answer.objects.get(id__exact=answer_id)
        except Answer.DoesNotExist:
            return Response('回答不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = AnswerUnserializer(instance=answer)
        answer_data = serializer.data
        if login_id not in answer_data['likers']:
            return Response('您还没有点赞这个回答',status=status.HTTP_400_BAD_REQUEST)
        answer_data['likers'].remove(login_id)
        serializer = AnswerUnserializer(instance=answer, data=answer_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        answer = serializer.save()
        # serializer = AnswerSerializer(instance=answer,context={'login_id':login_id})
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionsView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        user_id = request.query_params.get('user_id')
        login_id = request.user['user_id']
        if not user_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        user_id = int(user_id)
        try:
            user = User.objects.get(id__exact=user_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_404_NOT_FOUND)
        answers = user.collection_set.all()
        serializer = AnswerSerializer(instance=answers,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)
        

class SearchAnswersView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        keyword = request.query_params.get('keyword')
        login_id = request.user['user_id']
        if not keyword:
            return Response('缺少搜索关键字',status=status.HTTP_400_BAD_REQUEST)
        answers = Answer.objects.filter(content__contains=keyword)
        serializer = AnswerSerializer(instance=answers,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)


class AnswersByAuthorView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        user_id = request.query_params.get('user_id')
        login_id = request.user['user_id']
        if not user_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        user_id = int(user_id)
        answers = Answer.objects.filter(author__id__exact=user_id)
        serializer = AnswerSerializer(instance=answers,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)


class AnswerByQuestionView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        question_id = request.query_params.get('question_id')
        login_id = request.user['user_id']
        if not question_id:
            return Response('缺少提问id',status=status.HTTP_400_BAD_REQUEST)
        question_id = int(question_id)
        answers = Answer.objects.filter(question__id__exact=question_id)
        serializer = AnswerSerializer(instance=answers,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)