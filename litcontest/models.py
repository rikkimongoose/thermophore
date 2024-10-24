from enum import Enum
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class ContestStage(Enum):
    BEFORE_POST_STORY = 0
    POST_STORY = 1
    AFTER_POST_STORY = 2
    VOTING_FIRST = 3
    VOTING_FINAL = 4
    FINISHED = 5

class Contest(models.Model):
    REQUIRED_FIELDS = ['title', 'coordinator']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_owner', on_delete=models.CASCADE, verbose_name="Владелец")
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_coordinator', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Координатор")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    discussion_url = models.CharField(max_length=256, verbose_name="Ссылка на страницу с обсуждением")
    theme = models.CharField(max_length=200, blank=True, null=True, verbose_name="Тема")
    theme_ext = models.CharField(max_length=200, blank=True, null=True, verbose_name="Дополнительные условия")
    theme_by = models.CharField(max_length=200, blank=True, null=True, verbose_name="Тему предложил")
    max_in_group = models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(1)], verbose_name="Максимальное количество произведений в группе")
    max_in_final = models.PositiveSmallIntegerField(default=50, validators=[MinValueValidator(1)], verbose_name="Максимальное количество произведений в финале")
    max_votes = models.PositiveSmallIntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(6)], verbose_name="Количество произведений, за которые голосует участник")
    min_text_size = models.PositiveIntegerField(verbose_name="Минимальная длина произведения", validators=[MinValueValidator(0)])
    max_text_size = models.PositiveIntegerField(verbose_name="Максимальная длина произведения", validators=[MinValueValidator(0)])
    starts = models.DateField(blank=True, null=True, verbose_name="Дата окончания приема работ")
    submission_finishes = models.DateField(blank=True, null=True, verbose_name="Дата окончания приема работ")
    voting_starts = models.DateField(blank=True, null=True, verbose_name="Дата начала первого тура")
    voting_starts_final = models.DateField(blank=True, null=True, verbose_name="Дата окончания первого тура")
    finishes = models.DateField(blank=True, null=True, verbose_name="Дата окончания конкурса")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    def get_stage(self):
        now = datetime.now()
        if self.starts > now: ContestStage.BEFORE_POST_STORY
        if self.submission_finishes > now: ContestStage.POST_STORY
        if self.voting_starts > now: ContestStage.AFTER_POST_STORY
        if self.voting_starts_final > now: ContestStage.VOTING_FIRST
        if self.finishes > now: ContestStage.VOTING_FINAL
        return ContestStage.FINISHED
    def get_voting_stage(self):
        stage = self.get_stage()
        if stage == ContestStage.VOTING_FIRST: return Vote.VoteStage.FIRST
        if stage == ContestStage.VOTING_FINAL: return Vote.VoteStage.FINAL
        return None
    def needs_final(self):
        return self.max_in_group >= len(self.stories)
    def get_absolute_url(self):
        return reverse("litcontest:contest-detail", kwargs={"pk": self.pk})
    def is_active(self):
        return self.get_stage() not in (ContestStage.FINISHED)
    def __str__(self):
        return f"{self.title}"
    class Meta:
        ordering = ["pub_date"]
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'

class Story(models.Model):
    REQUIRED_FIELDS = ['title', 'contest']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Автор")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True, verbose_name="Конкурс")
    author = models.CharField(max_length=200, verbose_name="Имя автора") # добавлено для совместимости с прошлым движком
    title = models.CharField(max_length=200, verbose_name="Название")
    text = models.TextField(verbose_name="Текст")
    hidden = models.BooleanField(verbose_name="Скрыт", default=False)
    group = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Группа")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_final = BooleanField(verbose_name="Вышел в финал")
    def get_absolute_url(self):
        return reverse('litcontest:story-detail', kwargs={'pk': self.pk})
    def __str__(self):
        return f"{self.title}"
    class Meta:
        ordering = ["pub_date"]
        verbose_name = 'Рассказ'
        verbose_name_plural = 'Рассказы'

class Vote(models.Model):
    class VoteStage(models.IntegerChoices):
        FIRST = 1, "Начальное"
        FINAL = 2, "Финальное"
        def get_vote_stage(self, contest_stage):
            if contest_stage == ContestStage.VOTING_FIRST: return VoteStage.FIRST
            if contest_stage == ContestStage.VOTING_FINAL: return VoteStage.FINAL
            return None
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Голосующий")
    story = models.ForeignKey(Story, on_delete=models.CASCADE, verbose_name="Рассказ")
    stage = models.IntegerField(choices=VoteStage.choices, default=VoteStage.FIRST, verbose_name="Этап")
    stars = models.PositiveSmallIntegerField(verbose_name="Оценка")
    def __str__(self):
        return f"{self.owner} — {self.owner} {self.stars}"
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'story', 'stage'], name='unique_user_vote_combination'
            )
        ]
        verbose_name = 'Голосование'
        verbose_name_plural = 'Голосования'