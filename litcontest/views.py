from django.http import HttpResponse, FileResponse
from django.template import loader
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Contest, Story, Vote
from .forms import ContestForm, ContestCoordinatorForm, StoryForm
from .utils import pack_to_zip

def index(request):
    contests = get_list_or_404(Contest)
    return render(request, "thermophore/index.html", {"contests": contests})

def contest(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    return render(request, "thermophore/contest.html", {"contest": contest})

def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "thermophore/text.html", {"story": story})

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
class StoryFormView(FormView):
    template_name = "thermophore/story_form.html"
    form_class = StoryForm
    success_url = "/"

@login_required
class ContestFormView(FormView):
    template_name = "thermophore/contest_form.html"
    form_class = ContestForm
    success_url = "/"

@login_required
class ContestCoordinatorFormView(FormView):
    template_name = "thermophore/contest_form.html"
    form_class = ContestCoordinatorForm
    success_url = "/"

class ContestCreateView(CreateView):
    model = Contest
    fields = ["title", "text"]

class ContestListView(ListView):
    model = Contest
    template_name = "thermophore/index.html"

class ContestDetailView(DetailView):
    model = Contest
    template_name = "thermophore/contest.html"

class ContestUpdateView(UpdateView):
    model = Story
    fields = ["title", "text"]

class StoryCreateView(CreateView):
    model = Story
    fields = ["title", "text"]

class StoryUpdateView(UpdateView):
    model = Story
    fields = ["title", "text"]

class StoryDetailView(DetailView):
    model = Story
    template_name = "thermophore/story.html"

@require_http_methods(["POST"])
def vote(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "thermophore/story.html", {"story": story})

@cache_page(60 * 60 * 24 * 365)
def generate_zip(contest_id, group = None):
    texts = None
    if group is None:
        texts = Story.objects.filter(contest__id = contest_id).values('title', 'text')
    else:
        texts = Story.objects.filter(contest__id = contest_id, group = group).values('title', 'text')
    contest_title = Contest.objects.filter(id = contest_id).only('title')
    return FileResponse(pack_to_zip({x.title: x.text for x in texts}), as_attachment=True, filename=f"{contest_title}.zip")

class RulesView(TemplateView):
    template_name="thermophore/rules.html"

class AboutView(TemplateView):
    template_name="thermophore/about.html"