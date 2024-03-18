from django.urls import path, include

from . import views
from .views import SignUpView, ContestListView, ContestDetailView, StoryDetailView, RulesView, AboutView
from .feeds import RssSiteNewsFeed, AtomSiteNewsFeed
from django.contrib.auth import views as auth_views

app_name = "litcontest"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    # ex: / 
    path("", ContestListView.as_view(), name="index"),
    # ex: /5/
    path("<int:pk>/", ContestDetailView.as_view(), name="contest"),
    # ex: /polls/5/results/
    path("text/<int:pk>", StoryDetailView.as_view(), name="story"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("about/", AboutView.as_view(), name="about"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("rss/", RssSiteNewsFeed, name="rss"),
    path("atom/", AtomSiteNewsFeed, name="atom"),
]
