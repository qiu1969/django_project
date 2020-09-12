from backend.models import Question,Tag,User
from backend.serializers import QuestionSerializer,QuestionUnserializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from backend.authentication import LoginAuthentication
from rest_framework import status


def tagNamesTotagIDs(tagNames):
    tagIDs = []
    for tagName in tagNames:
        try:
            tag = Tag.objects.get(name__exact=tagName)
        except Tag.DoesNotExist:
            tag = Tag()
            tag.name = tagName
            tag.save()
        tagIDs.append(tag.id)
    return tagIDs


class QuestionView(APIView):
    # 提问相关的视图
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        # 获取所有的提问
        question_id = request.query_params.get('question_id')
        login_id = request.user['user_id']
        if not question_id:
            return Response('缺少提问id',status=status.HTTP_400_BAD_REQUEST)
        question_id = int(question_id)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response('您所访问的提问不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionSerializer(instance=question,context={'login_id': login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request,*args,**kwargs):
        # 提问
        login_id = request.user['user_id']
        data = request.data
        data['asker'] = login_id
        data['tags'] = tagNamesTotagIDs(data['tags'])
        serializer = QuestionUnserializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        question = serializer.save()
        serializer = QuestionSerializer(instance=question,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def put(self,request,*args,**kwargs):
        question_id = request.query_params.get('question_id')
        login_id = request.user['user_id']
        if not question_id:
            return Response('缺少要修改的提问主键',status=status.HTTP_400_BAD_REQUEST)
        question_id = int(question_id)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response('您所访问的提问不存在',status=status.HTTP_404_NOT_FOUND)
        if login_id != question.asker.id:
            return Response('您没有修改的权限',status=status.HTTP_401_UNAUTHORIZED)
        data = request.data
        data['asker'] = login_id
        data['tags'] = tagNamesTotagIDs(data['tags'])
        serializer = QuestionUnserializer(instance=question,data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        update_question = serializer.save()
        serializer = QuestionSerializer(instance=update_question,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def delete(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response('缺少要删除的提问的主键',status=status.HTTP_400_BAD_REQUEST)
        question_id = int(question_id)
        try:
            question = Question.objects.get(id__exact=question_id)
        except Question.DoesNotExist:
            return Response('您要删除的提问不存在',status=status.HTTP_404_NOT_FOUND)
        if question.asker.id != login_id:
            return Response('您没有删除权限',status=status.HTTP_401_UNAUTHORIZED)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowQuestionView(APIView):
    # 关注提问的视图
    authentication_classes = [LoginAuthentication]
    def post(self,request,*args,**kwargs):
        login_id = request.user['user_id']
        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response('缺少您要关注的提问的id',status=status.HTTP_400_BAD_REQUEST)
        question_id = int(question_id)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response('提问不存在',status=status.HTTP_404_NOT_FOUND)
        serializer = QuestionUnserializer(instance=question)
        question_data = serializer.data
        if login_id in question_data['followers']:
            return Response('您已经关注了这个提问',status=status.HTTP_400_BAD_REQUEST)
        question_data['followers'].append(login_id)
        serializer = QuestionUnserializer(instance=question,data=question_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        question = serializer.save()
        serializer = QuestionSerializer(instance=question,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_201_CREATED)

    def delete(self,request,*args,**kwargs):
        question_id = request.query_params.get('question_id')
        login_id = request.user['user_id']
        if not question_id :
            return Response('缺少您要取消管制的提问id',status=status.HTTP_400_BAD_REQUEST)
        question_id = int(question_id)
        try:
            question = Question.objects.get(id__exact=question_id)
        except Question.DoesNotExist:
            return Response('提问不存在',status=status.HTTP_404_NOT_FOUND)
        except Question.MultipleObjectsReturned:
            return Response('匹配到多个提问',status=status.HTTP_400_BAD_REQUEST)

        serializer = QuestionUnserializer(instance=question)
        question_data = serializer.data
        if login_id not in question_data['followers']:
            return Response('您还没有关注了这个提问',status=status.HTTP_400_BAD_REQUEST)
        question_data['followers'].remove(login_id)
        serializer = QuestionUnserializer(instance=question,data=question_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exception:
            return Response(str(exception),status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        question = serializer.save()
        serializer = QuestionSerializer(instance=question,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_204_NO_CONTENT)


class QuestionsByAskerView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        user_id = request.query_params.get('user_id')
        login_id = request.user['user_id']
        if not user_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        questions = Question.objects.filter(asker__id__exact=user_id)
        serializer = QuestionSerializer(instance=questions,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)


class SearchQuestionView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        keyword = request.query_params.get('keyword')
        login_id = request.user['user_id']
        if not keyword:
            return Response('缺少搜索关键字',status=status.HTTP_400_BAD_REQUEST)
        questions = Question.objects.filter(title__contains=keyword)
        serializer = QuestionSerializer(instance=questions,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)


class QuestionsByFollowerView(APIView):
    authentication_classes = [LoginAuthentication]
    def get(self,request,*args,**kwargs):
        follower_id = request.query_params.get('follower_id')
        login_id = request.user['user_id']
        if not follower_id:
            return Response('缺少用户id',status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id__exact=follower_id)
        except User.DoesNotExist:
            return Response('您所访问的用户不存在',status=status.HTTP_400_BAD_REQUEST)
        questions = user.followquestion_set.all()
        serializer = QuestionSerializer(instance=questions,many=True,context={'login_id':login_id})
        return Response(serializer.data,status=status.HTTP_200_OK)