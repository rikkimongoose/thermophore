from django.http import HttpResponse, FileResponse
from django.template import loader
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from .models import Contest, Story, Vote
from .forms import ContestForm, ContestCoordinatorForm, StoryForm, UserRegisterForm
from .utils import pack_to_zip

class SignUpView(SuccessMessageMixin, CreateView):
    success_url = reverse_lazy('litcontest:login')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"
    template_name = "registration/register.html"

class ContestFormView(LoginRequiredMixin, FormView):
    template_name = "litcontest/contest_form.html"
    form_class = ContestForm
    success_url = reverse_lazy("litcontest:index")

class ContestUpdateFormView(LoginRequiredMixin, FormView):
    template_name = "litcontest/contest_form.html"
    form_class = ContestCoordinatorForm
    success_url = reverse_lazy("litcontest:index")

class ContestCreateView(LoginRequiredMixin, CreateView):
    model = Contest
    form_class = ContestForm

class ContestUpdateView(LoginRequiredMixin, UpdateView):
    model = Contest
    form_class = ContestForm

class ContestListView(ListView):
    model = Contest
    template_name = "litcontest/index.html"

class ContestDetailView(DetailView):
    model = Contest
    template_name = "litcontest/contest.html"

class StoryFormView(LoginRequiredMixin, FormView):
    template_name = "litcontest/story_form.html"
    form_class = StoryForm
    success_url = reverse_lazy("litcontest:index")

class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    fields = ["title", "text"]

class StoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Story
    fields = ["title", "text"]

class StoryDetailView(DetailView):
    model = Story
    template_name = "litcontest/story.html"

@require_http_methods(["POST"])
def vote(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "litcontest/story.html", {"story": story})

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
    template_name="litcontest/rules.html"

class AboutView(TemplateView):
    template_name="litcontest/about.html"