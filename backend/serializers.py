from rest_framework import serializers
from backend.models import User,Question,Answer,Comment,Tag,Dialogue,Message,Avator


'''
序列化器的作用主要为序列化和反序列化
序列化是将模型类对象转化为json数据，在序列化器的构造函数当中使用instance传递模型类对象
反序列化将json数据转化为模型类对象，在序列化器的构造函数当中使用data传递json数据

'''
class UserSerializer(serializers.Serializer):
    # 用户的序列化器
    id = serializers.IntegerField(label='ID', read_only=True)
    username = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=254)
    phone = serializers.CharField(max_length=15)
    avator = serializers.CharField(max_length=40, required=False)
    residence = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    profession = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    career_experience = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    education_experience = serializers.CharField(allow_blank=True, allow_null=True, max_length=50, required=False)
    introduction = serializers.CharField(max_length=500, required=False)
    signature = serializers.CharField(max_length=200, required=False)
    create_time = serializers.DateTimeField(read_only=True)

    followers_count = serializers.SerializerMethodField()
    followees_count = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    is_followed = serializers.SerializerMethodField()
    def get_followers_count(self,obj):
        return obj.followers.count()
    
    def get_followees_count(self,obj):
        return obj.followee_set.count()

    def get_answers_count(self,obj):
        return obj.answer_set.count()

    def get_is_followed(self,obj):
        login_id = self.context.get('login_id')
        if not login_id:
            return False
        try:
            obj.followers.get(id__exact=login_id)
        except User.DoesNotExist:
            return False
        return True


class QuestionSerializer(serializers.Serializer):
    # 提问的序列化器
    id = serializers.IntegerField(label='ID', read_only=True)
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(allow_blank=True, allow_null=True, required=False, style={'base_template': 'textarea.html'})
    update_time = serializers.DateTimeField(read_only=True)
    followers_count = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    asker = UserSerializer()
    tags = serializers.StringRelatedField(many=True)
    is_followed = serializers.SerializerMethodField()
    
    def get_followers_count(self,obj):
        return obj.followers.count()

    def get_answers_count(self,obj):
        return obj.answer_set.count()

    def get_is_followed(self,obj):
        login_id = self.context['login_id']
        try:
            obj.followers.get(id__exact=login_id)
        except User.DoesNotExist:
            return False
        return True


class AnswerSerializer(serializers.Serializer):
    # 回答的序列化器
    id = serializers.IntegerField(label='ID', read_only=True)
    content = serializers.CharField(style={'base_template': 'textarea.html'})
    update_time = serializers.DateTimeField(read_only=True)
    author = UserSerializer()
    likers_count = serializers.SerializerMethodField()
    collectors_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_collected = serializers.SerializerMethodField()
    question_id = serializers.IntegerField(source='question.id')
    question_title = serializers.CharField(source='question.title')

    def get_likers_count(self,obj):
        return obj.likers.count()
    
    def get_collectors_count(self,obj):
        return obj.collectors.count()

    def get_is_liked(self,obj):
        login_id = self.context['login_id']
        try:
            obj.likers.get(id__exact=login_id)
        except User.DoesNotExist:
            return False
        return True

    def get_is_collected(self,obj):
        login_id = self.context['login_id']
        try:
            obj.collectors.get(id__exact=login_id)
        except User.DoesNotExist:
            return False
        return True


class CommentSerializer(serializers.Serializer):
    # 评论的序列化器
    id = serializers.IntegerField(label='ID', read_only=True)
    content = serializers.CharField(max_length=500)
    update_time = serializers.DateTimeField(read_only=True)
    answer = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all())
    reply = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Comment.objects.all(), required=False)
    author = UserSerializer()
    likers_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    def get_likers_count(self,obj):
        return obj.likers.count()
    
    def get_is_liked(self,obj):
        login_id = self.context['login_id']
        try:
            obj.likers.get(id__exact=login_id)
        except User.DoesNotExist:
            return False
        return True


class DialogueSerializer(serializers.ModelSerializer):
    # 标签的序列化器
    class Meta:
        model = Dialogue
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    # 消息的序列化器
    class Meta:
        model = Message
        fields = '__all__'


class UserUnserializer(serializers.ModelSerializer):
    # 用户的反序列化器
    class Meta:
        model = User
        fields = '__all__'


class QuestionUnserializer(serializers.ModelSerializer):
    # 提问的反序列化器
    class Meta:
        model = Question
        fields = '__all__'


class AnswerUnserializer(serializers.ModelSerializer):
    # 回答的反序列化器
    class Meta:
        model = Answer
        fields = '__all__'


class CommentUnserializer(serializers.ModelSerializer):
    # 评论的反序列化器
    class Meta:
        model = Comment
        fields = '__all__'


class AvatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avator
        fields = '__all__'