from django.db.models import Count, Q
from django.http import HttpResponse, FileResponse, HttpResponseForbidden, Http404
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
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import escape_uri_path
from .models import Contest, Story, Vote, ContestStage
from .forms import ContestForm, ContestCoordinatorForm, StoryForm, UserRegisterForm, VoteForm
from .utils import pack_to_zip, update_groups, load_voting_groups

from collections import defaultdict

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

class ContestCreateView(LoginRequiredMixin, CreateView):
    model = Contest
    form_class = ContestForm
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return HttpResponseRedirect(self.get_success_url())

class ContestUpdateView(LoginRequiredMixin, UpdateView):
    model = Contest
    form_class = ContestForm

class ContestCoordinatorUpdateView(LoginRequiredMixin, UpdateView):
    model = Contest
    form_class = ContestCoordinatorForm

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
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Group if it's possible
        stage = context.object.get_voting_stage()

        is_only_my_stories = stage in (ContestStage.POST_STORY, AFTER_POST_STORY)
        is_groped = stage in (ContestStage.VOTING_FIRST, ContestStage.VOTING_FINAL)
        context["stage"] = stage
        context["is_voting"] = stage in (ContestStage.VOTING_FIRST, ContestStage.VOTING_FINAL)
        context["is_editable"] = stage in (ContestStage.POST_STORY)
        context["is_only_my_stories"] = is_only_my_stories
        context["is_groped"] = is_groped

        ##TODO - разбиения

        if stage >= ContestStage.VOTING_FIRST and stage < ContestStage.FINISHED:
            update_groups(self.kwargs.get('contest_id'))
        if is_only_my_stories:
            context["my_stories"] = Story.objects.filter(contest__id = contest_id, author = self.request.user).all()
        elif is_groped:
            if stage == ContestStage.VOTING_FIRST:
                stories = context.object.story_set.all
                if not stories: return context
                context["grouped"] = stories_grouped(stories)
            else:
                context["final_stories"] = stories_grouped(stories)
        return context

class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    fields = ["title", "text"]
    def form_valid(self, form):
        contest_id = self.kwargs.get('contest_id')
        form.instance.owner = self.request.user
        form.instance.contest = get_object_or_404(Contest, pk=contest_id)
        form.save()
        return redirect("litcontest:contest-detail", pk=contest_id)

class StoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Story
    fields = ["title", "text"]

class StoryDetailView(DetailView):
    model = Story
    template_name = "litcontest/story.html"


class ContestListView():
    model = Contest
    template_name = "litcontest/index.html"
    def get_queryset(self):
        qs = super(ContestListView, self).get_queryset()
        return qs.annotate(Count('story'))

class VotingView(ListView, FormView):
    model = Contest
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        contest_id = self.kwargs.get('contest_id')
        if not form.is_valid():
            return super().post(request, *args, **kwargs)
        contest = get_object_or_404(Contest, pk=contest_id)
        stage = contest.get_voting_stage()
        if stage not in (ContestStage.VOTING_FIRST, ContestStage.VOTING_FINAL): return HttpResponseForbidden

        allowed_groups = None
        if stage == ContestStage.VOTING_FIRST:
            allowed_groups = load_voting_groups(self.request.user, contest_id)
            if not allowed_groups: raise ValidationError("У вас нет историй. Вы не можете голосовать.")

        votes_to_check = []
        checking_errors = []
        for k, v in VOTES.items():
            votes_to_check.append(form.instance[f"vote{k}"])
        votes_len = len(votes.items())
        for i in range(0, votes_len):
            for j in range(i + 1, votes_len):
                if(votes_to_check[i] == votes_to_check[j]):
                    checking_errors.append(
                        ValidationError(
                            _("Вы проголосовали за одинаковые рассказы: %(i) и %(j)"),
                                params={"i": i, "j": j},
                            )
                        )
        for vote_story_id in votes_to_check:
            story = get_object_or_404(Story, pk=vote_story_id)
            if allowed_groups is not None and story.group not in allowed_groups:
                checking_errors.append(
                    ValidationError(
                        _("Вы проголосовали за историю '%(title)' из группы %(group). Вы не можете голосовать за истории из этой группы"),
                            params={"title": story.title, "group": story.group },
                        )
                    )
            if story.owner == self.request.user:
                checking_errors.append(
                    ValidationError(
                        _("Вы не можете голосовать за свою собственную историю '%(title)'."),
                            params={"title": story.title },
                        )
                    )

        if checking_errors: raise ValidationError(checking_errors)

        Vote.objects.filter(
            owner=self.request.user,
            stage=stage,
            story__contest__id=contest_id).delete()
        votes = []
        for k, v in VOTES.items():
            vote = Vote.objects.create(owner = self.request.user, story = get_object_or_404(Story, pk=form.instance[f"vote{k}"]), stage = stage, stars = v)
            votes.append(vote)
        Vote.objects.bulk_create(votes)
        return HttpResponseRedirect(self.get_success_url())

class ResultView(ListView):
    model = Contest

class RulesView(TemplateView):
    template_name="litcontest/rules.html"

class AboutView(TemplateView):
    template_name="litcontest/about.html"

@cache_page(60 * 60 * 24 * 365)
def generate_zip(request, *args, **kwargs):
    contest_id = kwargs.get('contest_id', None)
    if contest_id is None: raise Http404
    group = kwargs.get('group', None)
    texts_data = load_texts_for_zip(contest_id, group)
    return pack_texts_to_zip(texts_data)

@cache_page(60 * 60 * 24 * 365)
def generate_zip_final(request, *args, **kwargs):
    contest_id = kwargs.get('contest_id', None)
    if contest_id is None: raise Http404
    group = kwargs.get('group', None)
    texts_data = load_texts_for_zip(contest_id, None, True)
    return pack_texts_to_zip(texts_data)

def load_texts_for_zip(contest_id, group, is_final = False):
    if group is not None:
        return Story.objects.filter(contest_id = contest_id, group = group).values('title', 'text')
    if is_final:
        return Story.objects.filter(contest_id = contest_id).values('title', 'text')
    return Story.objects.filter(contest_id = contest_id, is_final = True).values('title', 'text')

def pack_texts_to_zip(texts_data):
    contest_data = Contest.objects.filter(id = contest_id).only('title')
    contest_title = escape_uri_path(contest_data[0].title)
    zip_file = {}
    for text in texts_data:
        zip_file[text["title"] + ".txt"] = text["text"]
    zip_file_attachment = pack_to_zip(zip_file)
    response = HttpResponse(zip_file_attachment, content_type='application/x-zip-compressed')
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{contest_title}.zip"
    return response