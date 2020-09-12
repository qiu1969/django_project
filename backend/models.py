from django.db import models
import datetime


class User(models.Model):
    # 用户的数据实体
    username = models.CharField(max_length=20,null=False,unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15,unique=True)

    avator = models.CharField(max_length=15,default='2default.jpg')
    residence = models.CharField(max_length=50,null=True,blank=True)
    profession = models.CharField(max_length=50,null=True,blank=True)
    career_experience = models.CharField(max_length=50,null=True,blank=True)
    education_experience = models.CharField(max_length=50,null=True,blank=True)
    introduction = models.CharField(max_length=500,default='这个人很懒，什么都没有留下')
    signature = models.CharField(max_length=200,default='这个人很懒，什么都没有留下')
    create_time = models.DateTimeField(auto_now_add=True)
    followers = models.ManyToManyField(to='User',related_name='followee_set',blank=True) # 关注了我的人
    
    class Meta:
        db_table = 'User'


class Question(models.Model):
    # 问题的数据实体
    title = models.CharField(max_length=50,null=False)
    description = models.TextField(null=True,blank=True)
    asker = models.ForeignKey(to='User',on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(to='Tag',related_name='question_set',blank=True) # 这个问题的标签
    followers = models.ManyToManyField(to='User',related_name='followquestion_set',blank=True) # 关注了这个问题的人

    class Meta:
        db_table = 'Question'


class Tag(models.Model):
    # 问题的标签数据实体
    name = models.CharField(max_length=15,unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Tag'


class Answer(models.Model):
    # 回答的数据实体
    question = models.ForeignKey(to='Question',on_delete=models.CASCADE)
    author = models.ForeignKey(to='User', on_delete=models.CASCADE)
    content = models.TextField()
    update_time = models.DateTimeField(auto_now=True)
    collectors = models.ManyToManyField(to='User',related_name='collection_set',blank=True) # 收藏了这个回答的人
    likers = models.ManyToManyField(to='User',related_name='likeanswer_set',blank=True) # 点赞了这个回答的人
    
    class Meta:
        db_table = 'Answer'


class Comment(models.Model):
    # 评论的数据实体
    answer = models.ForeignKey(to='Answer',on_delete=models.CASCADE)
    author = models.ForeignKey(to='User',on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    reply = models.ForeignKey(to='self',on_delete=models.CASCADE,null=True,blank=True)
    update_time = models.DateTimeField(auto_now=True)
    likers = models.ManyToManyField(to='User',related_name='likecomment_set',blank=True) # 点赞了这个评论的人

    class Meta:
        db_table = 'Comment'


class Dialogue(models.Model):
    # 对话的实体类
    talker = models.ForeignKey(to='User',on_delete=models.CASCADE,related_name='talk_set')
    listener = models.ForeignKey(to='User',on_delete=models.CASCADE,related_name='listen_set')
    content = models.CharField(max_length=500)
    send_time = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return str(self.talker) + '对' + str(self.listener) + '说:'+str(self.content)
    
    class Meta:
        db_table = 'Dialogue'


class Message(models.Model):
    # 关于消息通知的数据实体
    acceipter = models.ForeignKey(to='User',on_delete=models.CASCADE,related_name='acceipt_set')
    sender = models.ForeignKey(to='User',on_delete=models.CASCADE,related_name='send_set')
    obj = models.IntegerField(null=True,blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    message_type = models.IntegerField()
    message_content = models.CharField(max_length=100)
    read = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.message_content
    
    class Meta:
        db_table = 'Message'


class Avator(models.Model):
    # 保存头像路径的实体
    user = models.ForeignKey(to='User',on_delete=models.CASCADE,related_name='avator_set')
    path = models.CharField(max_length=30)