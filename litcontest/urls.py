from django.urls import path

from . import views
app_name = "litcontest"
urlpatterns = [
    # ex: / 
    path("", views.index, name="index"),
    # ex: /5/
    path("<int:contest_id>/", views.contest, name="contest"),
    # ex: /polls/5/results/
    path("text/<int:story_id>", views.story, name="story"),
]
