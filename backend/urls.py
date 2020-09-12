from django.conf.urls import url
from backend.commentviews import LikeCommentView
from backend.commentviews import CommentView
from backend.userviews import UserView,SearchUsersView,LoginView,RegisterView,FolloweesView,FollowersView
from backend.userviews import ChangePassword,FollowView
from backend.questionviews import QuestionView,FollowQuestionView,SearchQuestionView,QuestionsByAskerView
from backend.questionviews import QuestionsByFollowerView
from backend.answerviews import AnswerView,CollectView,LikeAnswerView,CollectionsView,AnswersByAuthorView
from backend.answerviews import SearchAnswersView,AnswerByQuestionView
from backend.avatorviews import AvatorView


urlpatterns = [
    url(r'^login$',LoginView.as_view()),
    url(r'^register$',RegisterView.as_view()),
    url(r'^user$',UserView.as_view()),
    url(r'^followers$',FollowersView.as_view()),
    url(r'^followees$',FolloweesView.as_view()),
    url(r'^searchusers$',SearchUsersView.as_view()),
    url(r'^changepassword$',ChangePassword.as_view()),
    url(r'^follow$',FollowView.as_view()),

    url(r'^question$',QuestionView.as_view()),
    url(r'^followquestion$',FollowQuestionView.as_view()),
    url(r'^searchquestions$',SearchQuestionView.as_view()),
    url(r'^questionsbyasker$',QuestionsByAskerView.as_view()),
    url(r'^questionsbyfollower$',QuestionsByFollowerView.as_view()),
    
    url(r'^answer$',AnswerView.as_view()),
    url(r'^collect$',CollectView.as_view()),
    url(r'^answersbyauthor$',AnswersByAuthorView.as_view()),
    url(r'^answersbyquestion$',AnswerByQuestionView.as_view()),
    url(r'^likeanswer$',LikeAnswerView.as_view()),
    url(r'^searchanswers$',SearchAnswersView.as_view()),
    url(r'^collections$',CollectionsView.as_view()),

    url(r'^likecomment$',LikeCommentView.as_view()),
    url(r'^comment$',CommentView.as_view()),
    
    url(r'^avator$',AvatorView.as_view())
    
    
]