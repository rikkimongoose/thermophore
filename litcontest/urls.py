from django.urls import path, include

from . import views

app_name = "litcontest"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    # ex: / 
    path("", views.index, name="index"),
    # ex: /5/
    path("<int:contest_id>/", views.contest, name="contest"),
    # ex: /polls/5/results/
    path("text/<int:story_id>", views.story, name="story"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
]
