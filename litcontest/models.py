from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


def validate_texts_num_to_vote(value):
    if value < 1 or value > 6:
        raise ValidationError(
            "Значение %(value)s не подходит. Должно быть от 1 до 6",
            params={"value": value},
        )

class Contest(models.Model):
    REQUIRED_FIELDS = ['title', 'coordinator']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_owner', on_delete=models.CASCADE)
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_coordinator', on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    discussion_url = models.CharField(max_length=256)
    theme = models.CharField(max_length=200)
    theme_by = models.CharField(max_length=200)
    max_in_group = models.PositiveSmallIntegerField(default=50)
    max_in_final = models.PositiveSmallIntegerField(default=50)
    max_votes = models.PositiveSmallIntegerField(default=6, validators=[MinValueValidator(1), MaxValueValidator(6)])
    min_text_size = models.PositiveIntegerField()
    max_text_size = models.PositiveIntegerField()
    starts = models.DateField(blank=True, null=True)
    submission_finishes = models.DateField(blank=True, null=True)
    voting_starts = models.DateField(blank=True, null=True)
    voting_starts_final = models.DateField(blank=True, null=True)
    finishes = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title}"
    class Meta:
        ordering = ["created"]

class Story(models.Model):
    REQUIRED_FIELDS = ['title', 'contest']
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    author = models.CharField(max_length=200) # добавлено для совместимости с прошлым движком
    title = models.CharField(max_length=200)
    text = models.TextField()
    hidden = models.BooleanField()
    group = models.PositiveSmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title}"
    class Meta:
        ordering = ["created"]

class Vote(models.Model):
    class VoteStage(models.IntegerChoices):
        FIRST = 1, "Начальное"
        FINAL = 2, "Финальное"
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    stage = models.IntegerField(choices=VoteStage.choices, default=VoteStage.FIRST)
    stars = models.PositiveSmallIntegerField()
    def __str__(self):
        return f"{self.owner} - {self.owner} {self.stars}"
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'story', 'stage'], name='unique_user_vote_combination'
            )
        ]