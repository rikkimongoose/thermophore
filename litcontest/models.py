from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Contest(models.Model):
    REQUIRED_FIELDS = ['title', 'coordinator']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_owner', on_delete=models.CASCADE, verbose_name="Владелец")
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_coordinator', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Координатор")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    discussion_url = models.CharField(max_length=256, verbose_name="Ссылка на страницу с обсуждением")
    theme = models.CharField(max_length=200, verbose_name="Тема")
    theme_by = models.CharField(max_length=200, verbose_name="Тему предложил")
    max_in_group = models.PositiveSmallIntegerField(default=50, verbose_name="Максимальное количество произведений в группе")
    max_in_final = models.PositiveSmallIntegerField(default=50, verbose_name="Максимальное количество произведений в финале")
    max_votes = models.PositiveSmallIntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(6)], verbose_name="Количество произведений, за которые голосует участник")
    min_text_size = models.PositiveIntegerField(verbose_name="Минимальная длина произведения")
    max_text_size = models.PositiveIntegerField(verbose_name="Максимальная длина произведения")
    starts = models.DateField(blank=True, null=True, verbose_name="Дата окончания приема работ")
    submission_finishes = models.DateField(blank=True, null=True, verbose_name="Дата окончания приема работ")
    voting_starts = models.DateField(blank=True, null=True, verbose_name="Дата начала первого тура")
    voting_starts_final = models.DateField(blank=True, null=True, verbose_name="Дата окончания первого тура")
    finishes = models.DateField(blank=True, null=True, verbose_name="Дата окончания конкурса")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    def __str__(self):
        return f"{self.title}"
    class Meta:
        ordering = ["pub_date"]
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'

class Story(models.Model):
    REQUIRED_FIELDS = ['title', 'contest']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Автор")
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, verbose_name="Конкурс")
    author = models.CharField(max_length=200, verbose_name="Имя автора") # добавлено для совместимости с прошлым движком
    title = models.CharField(max_length=200, verbose_name="Название")
    text = models.TextField(verbose_name="Текст")
    hidden = models.BooleanField(verbose_name="Скрыт")
    group = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Группа")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
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