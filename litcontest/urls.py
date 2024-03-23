from django.urls import path, include

from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .views import SignUpView, ContestCreateView, ContestUpdateView, ContestListView, ContestDetailView, StoryDetailView, StoryCreateView, StoryUpdateView, RulesView, AboutView
from .feeds import RssSiteNewsFeed, AtomSiteNewsFeed

app_name = "litcontest"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", ContestListView.as_view(), name="index"),
    path("<int:pk>/", ContestDetailView.as_view(), name="contest"),
    path("<int:contest_id>/download", views.generate_zip, name="generate_zip"),
    path("add/", ContestCreateView.as_view(), name="contest-add"),
    path("<int:pk>/edit", ContestUpdateView.as_view(), name="contest-update"),
    path("text/<int:pk>", StoryDetailView.as_view(), name="story"),
    path("<int:contest_id>/add", StoryCreateView.as_view(), name="story-add"),
    path("text/<int:pk>/edit", StoryUpdateView.as_view(), name="story-update"),
    path("rules/", RulesView.as_view(), name="rules"),
    path("about/", AboutView.as_view(), name="about"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("rss/", RssSiteNewsFeed()),
    path("feed/", AtomSiteNewsFeed()),
    path("atom/", AtomSiteNewsFeed()),
]
