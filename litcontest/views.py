from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Contest, Story, Vote
from .forms import ContestForm, ContestCoordinatorForm, StoryForm

def index(request):
    contests = get_list_or_404(Contest)
    return render(request, "thermophore/index.html", {"contests": contests})

def contest(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    return render(request, "thermophore/contest.html", {"contest": contest})

def story(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "thermophore/text.html", {"story": story})

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class StoryFormView(FormView):
    template_name = "textform.html"
    form_class = StoryForm
    success_url = "/"

class ContestFormView(FormView):
    template_name = "contest_form.html"
    form_class = ContestForm
    success_url = "/"

class ContestCoordinatorFormView(FormView):
    template_name = "contest_form.html"
    form_class = ContestCoordinatorForm
    success_url = "/"

class StoryCreateView(CreateView):
    model = Story
    fields = ["title", "text"]

class StoryUpdateView(UpdateView):
    model = Story
    fields = ["title", "text"]

class ContestCreateView(CreateView):
    model = Story
    fields = ["title", "text"]

class ContestUpdateView(UpdateView):
    model = Story
    fields = ["title", "text"]

@require_http_methods(["POST"])
def vote(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "thermophore/text.html", {"story": story})

class RulesView(TemplateView):
    template_name="rules.html"

class AboutView(TemplateView):
    template_name="about.html"