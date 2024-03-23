from django.db.models import Count
from django.http import HttpResponse, FileResponse,Http404
from django.template import loader
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect
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
from django.utils.encoding import escape_uri_path
from .models import Contest, Story, Vote
from .forms import ContestForm, ContestCoordinatorForm, StoryForm, UserRegisterForm, VoteForm
from .utils import pack_to_zip

VOTES = {
    1:10,
    2:6,
    3:3,
    4:3,
    5:2,
    6:1
}

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
    success_url = reverse_lazy("litcontest:index")
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return HttpResponseRedirect(self.get_success_url())

class ContestUpdateView(LoginRequiredMixin, UpdateView):
    model = Contest
    form_class = ContestForm

class ContestListView(ListView):
    model = Contest
    template_name = "litcontest/index.html"
    def get_queryset(self):
        qs = super(ContestListView, self).get_queryset()
        return qs.annotate(Count('story'))

class ContestDetailView(DetailView, FormView):
    model = Contest
    template_name = "litcontest/contest.html"
    form_class = VoteForm

class StoryFormView(LoginRequiredMixin, FormView):
    template_name = "litcontest/story_form.html"
    form_class = StoryForm
    success_url = reverse_lazy("litcontest:index")

class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    fields = ["title", "text"]
    def form_valid(self, form):
        contest_id = self.kwargs.get('contest_id')
        form.instance.owner = self.request.user
        form.instance.contest = get_object_or_404(Contest, pk=contest_id)
        form.save()
        return redirect("litcontest:contest", pk=contest_id)

class StoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Story
    fields = ["title", "text"]

class StoryDetailView(DetailView):
    model = Story
    template_name = "litcontest/story.html"

@require_http_methods(["POST"])
def vote(request, contest_id):
    story = get_object_or_404(Story, pk=story_id)
    return render(request, "litcontest/story.html", {"contest_id": contest_id})

#@cache_page(60 * 60 * 24 * 365)
def generate_zip(request, *args, **kwargs):
    contest_id = kwargs.get('contest_id', None)
    if contest_id is None: raise Http404
    group = kwargs.get('group', None)
    texts_data = None
    if group is None:
        texts_data = Story.objects.filter(contest__id = contest_id).values('title', 'text')
    else:
        texts_data = Story.objects.filter(contest__id = contest_id, group = group).values('title', 'text')
    contest_data = Contest.objects.filter(id = contest_id).only('title')
    contest_title = escape_uri_path(contest_data[0].title)
    zip_file = {}
    for text in texts_data:
        zip_file[text["title"] + ".txt"] = text["text"]
    zip_file_attachment = pack_to_zip(zip_file)
    response = HttpResponse(zip_file_attachment, content_type='application/x-zip-compressed')
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{contest_title}.zip"
    return response

class RulesView(TemplateView):
    template_name="litcontest/rules.html"

class AboutView(TemplateView):
    template_name="litcontest/about.html"