from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.viewes.decorators.http import require_http_methods
from .models import Contest, Story, Vote

def index(request):
    contests = get_list_or_404(Contest)
    return render(request, "thermophore/index.html", {"contests": contests})

def contest(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    return render(request, "thermophore/contest.html", {"contest": contest})

def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "thermophore/text.html", {"story": story})

@require_http_methods(["POST"])
def vote(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "thermophore/text.html", {"story": story})